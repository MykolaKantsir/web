from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.forms import modelform_factory
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.db.models.functions import ExtractWeek, ExtractYear
from django.db.models import Q, Min, Max, ManyToManyField
from django.db.models import Case, When, Value, IntegerField
from django.contrib.contenttypes.models import ContentType
from .models import *
from inventory import models
from inventory.choices import OrderStatus
from inventory.functions import get_next_order_status
import json

# singleton class to get all non-abstract subclasses of Product
# can be used later to get all subclasses of a class
# might be moved to a separate file later
class ProductSubclasses:
    _instance = None
    subclasses = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.subclasses = self._get_all_subclasses(Product)

    def _get_all_subclasses(self, cls):
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            subclasses.extend(self._get_all_subclasses(subclass))
        return [cls for cls in subclasses if not cls._meta.abstract]

# Usage in views
non_abstract_subclasses = ProductSubclasses.get_instance().subclasses

# Create your views here.
def index(request):
    return render(request, 'inventory/index.html')

# fuction to add recent orders to a queryset of products
def annotate_products_with_orders(products_queryset, product_factory):
    # Define the date for three weeks ago from today
    three_weeks_ago = timezone.now() - timedelta(weeks=6)

    # Convert the queryset to a list to sort in Python
    products_list = list(products_queryset)

    # Iterate over the products queryset and annotate each product
    for product in products_queryset:
        # Use the factory to get the specific product class based on tool_type or similar attribute
        specific_product_class = product_factory.get_product(tool_type_str=product.tool_type)
        product_type = type(specific_product_class)
        product_content_type = ContentType.objects.get_for_model(product_type)

        # Get orders in the last three weeks for each product
        recent_orders = Order.objects.filter(
            content_type=product_content_type, 
            object_id=product.id,
            order_date__gte=three_weeks_ago
        ).order_by('-order_date')

        # Set is_ordered to True if there are recent orders, and attach the orders to the product
        product.is_ordered = recent_orders.exists()
        product.recent_orders = recent_orders if product.is_ordered else []

    # Now sort the list so that products with recent orders come first
    products_list.sort(key=lambda x: x.is_ordered, reverse=True)

    return products_list

# view to search for products by id, description, or barcode
def search_product(request):
    # Fetching the single search query
    search_term = request.GET.get('search_term', '')    
    matched_products = []

    def query_subclasses(klass):
        # If the class is non-abstract, query it based on multiple attributes using the single search term
        if not getattr(klass._meta, 'abstract', False):
            matched_products.extend(
                list(klass.objects.filter(
                    Q(barcode__icontains=search_term) |
                    Q(code__icontains=search_term) |
                    Q(ean__icontains=search_term)
                ))
            )
        else:
            # If the class is abstract, recursively explore its subclasses
            for subclass in klass.__subclasses__():
                query_subclasses(subclass)

    # Start the recursive querying with the Product model
    query_subclasses(Product)        

    # Annotate the matched products with orders
    annotated_products = annotate_products_with_orders(matched_products, ProductFactory())

    context = {
        'products': annotated_products,
    }
    
    # Render the product cards and return as HTML response
    return render(request, 'inventory/product_card.html', context)

# function to check if a product exists
# used in the scanner view
def product_exists(barcode):
    exists = False

    # Check in ProductToBeAdded first
    if ProductToBeAdded.objects.filter(barcode=barcode).exists():
        return 'review'

    def query_subclasses(klass):
        nonlocal exists
        if not getattr(klass._meta, 'abstract', False):
            if klass.objects.filter(Q(ean=barcode) | Q(barcode=barcode) | Q(code=barcode)).exists():
                exists = True
        else:
            for subclass in klass.__subclasses__():
                query_subclasses(subclass)

    query_subclasses(Product)
    return 'exists' if exists else 'new'

# view to scan barcodes
def scanner(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        barcode = data.get('barcode', '').strip()

        status = product_exists(barcode)
        if status == 'exists':
            return JsonResponse({'message': f'Product {barcode} already exists'}, status=200)
        elif status == 'review':
            return JsonResponse({'message': f'Product {barcode} is already under review'}, status=200)
        else:
            # Add to ProductToBeAdded if not exists
            ProductToBeAdded.objects.get_or_create(barcode=barcode)
            return JsonResponse({'message': f'Product {barcode} added to be reviewed'}, status=201)
    else:
        # Fetch all barcodes from ProductToBeAdded
        existing_barcodes = ProductToBeAdded.objects.all().order_by('-date_added')
        return render(request, 'inventory/scanner.html', {'existing_barcodes': existing_barcodes})

def get_all_subclasses(cls):
    """Recursively get all subclasses of a class"""
    subclasses = cls.__subclasses__()
    for subclass in subclasses:
        subclasses.extend(get_all_subclasses(subclass))
    return subclasses

# view to search for products by category with facets
def search_category(request):
    category = request.GET.get('category', "").strip()
    # Extract facet selections from the request
    facets_str = request.GET.get('facets', '{}')
    facet_selections = json.loads(facets_str)
    products_context = {}
    results = {}

    # Get all non-abstract subclasses of Product
    all_subclasses = get_all_subclasses(Product)
    non_abstract_subclasses = [cls for cls in all_subclasses if not cls._meta.abstract]

    # Find the first product that matches the category among subclasses
    matching_product = None
    for subclass in non_abstract_subclasses:
        matching_product = subclass.objects.filter(tool_type=category).first()
        if matching_product:
            break


    # If there's a match, get all objects of the same class and its facet_fields
    if matching_product:
        product_class = matching_product.__class__
        queryset = product_class.objects.all()  # Modify as per your needs
        
        # Filter the queryset based on facet selections
        for facet, selections in facet_selections.items():
            if isinstance(selections, list):  
                # Categorical facet
                # # Check if the facet corresponds to a ManyToManyField field
                if isinstance(getattr(product_class, facet).field, ManyToManyField):
                    # Fetch the related model
                    related_model = getattr(product_class, facet).field.related_model
                    # Replace string selections with their corresponding IDs
                    ids = [related_model.objects.get(name=selection).id for selection in selections]
                    queryset = queryset.filter(**{facet + '__in': ids})
                else:
                    queryset = queryset.filter(**{facet + '__in': selections})
            elif isinstance(selections, dict):  # Numerical facet
                min_val = selections.get('min')
                max_val = selections.get('max')
                if min_val is not None:
                    queryset = queryset.filter(**{facet + '__gte': min_val})
                if max_val is not None:
                    queryset = queryset.filter(**{facet + '__lte': max_val})
            else:  # Boolean facet
                queryset = queryset.filter(**{facet: selections})

        facet_fields = product_class.facet_fields

        facets_data = []

        for facet in facet_fields:
            if len(facet) == 3:
                field, display_name, facet_type = facet
                if facet_type == 'categorical':
                    if queryset.model._meta.get_field(field).is_relation:
                        # If it's a ForeignKey, get the related object's name (or any other appropriate field)
                        unique_values = list(queryset.values_list(f"{field}__name", flat=True).distinct().order_by(f"{field}__name"))
                    else:
                        unique_values = list(queryset.values_list(field, flat=True).distinct().order_by(field))
                    # does not create a facter if there's only one unique value
                    if len(unique_values) == 1:
                        continue
                    facets_data.append({
                        'type': 'categorical',
                        'name': field,
                        'display_name': display_name,
                        'options': unique_values
                    })
                elif facet_type == 'numerical':
                    min_val = queryset.aggregate(Min(field))[f"{field}__min"]
                    max_val = queryset.aggregate(Max(field))[f"{field}__max"]
                    # does not create a facter if max and min are the same
                    if min_val == max_val:
                        continue
                    facets_data.append({
                        'type': 'numerical',
                        'name': field,
                        'display_name': display_name,
                        'min': min_val,
                        'max': max_val
                    })
            if len(facet) == 4:
                field, display_name, facet_type, boolean_options = facet
                if facet_type == 'boolean':
                    facets_data.append({
                        'type': 'boolean',
                        'name': field,
                        'display_name': display_name,
                        'options': {'option_true': boolean_options['true_label'], 
                                    'option_false': boolean_options['false_label']
                                    }
                    })

        # Annotate the products with orders
        annotated_products = annotate_products_with_orders(queryset, ProductFactory())
        products_context = {'products': annotated_products}

        # Render facets and products
        facets_html = render_to_string('inventory/facet.html', {'facets_data': facets_data})
        products_html = render_to_string('inventory/product_card.html', products_context)


        results = {
            'products': products_html, 
            'facets': facets_html,
            'applied_filters': facet_selections  # Include the applied filters here
        }

    # Return the results
    return JsonResponse(results)

def create_order(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product_tool_type = data.get('product_tool_type')
        quantity = data.get('quantity')
        if not product_id or not product_tool_type:
            return JsonResponse({'status': 'error', 'message': 'Product ID or tool type not provided'}, status=400)
        # Find corresponting product_tool_type object
        corresponding_product = ProductFactory().get_product(tool_type_str=product_tool_type)
        product_type = type(corresponding_product)
        product_model_name = product_type.__name__
        product_model = ContentType.objects.get(model=product_model_name.lower())
        ordered_product = product_type.objects.get(id=product_id)
        new_order = Order.objects.create(
            content_type = product_model,
            object_id = product_id,
            quantity = quantity,)
        new_order.save()
        return JsonResponse({
            'status': 'success',
            'message': f'Order for {quantity} {ordered_product} successfully placed.'
            })
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# view for the orders page
def orders_page(request):
    # Define custom ordering for statuses
    status_ordering = Case(
        When(status=OrderStatus.PENDING, then=Value(1)),
        When(status=OrderStatus.ORDERED, then=Value(2)),
        default=Value(3),
        output_field=IntegerField()
    )

    # Order by custom status ordering and then by order_date
    orders = Order.objects.annotate(
        custom_status_order=status_ordering
    ).annotate(
        year=ExtractYear('order_date'),
        week=ExtractWeek('order_date')
    ).order_by('-year', '-week', '-order_date', 'custom_status_order')

    # Group orders by year and week
    orders_grouped = {}
    for order in orders:
        year_week = (order.year, order.week)
        if year_week not in orders_grouped:
            orders_grouped[year_week] = []
        orders_grouped[year_week].append(order)

    status_choices = Order._meta.get_field('status').choices
    context = {
        'orders_grouped': orders_grouped,
        'status_choices': status_choices
    }
    return render(request, 'inventory/orders.html', context)

# view to add a comment to an order
@require_POST
def add_comment(request, order_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        comment_text = data.get('comment_text')
        
        # Prevent creating empty comments
        if not comment_text.strip():
            return JsonResponse({'status': 'error', 'message': 'Comment text cannot be empty.'}, status=400)

        order = get_object_or_404(Order, pk=order_id)
        comment = Comment.objects.create(order=order, text=comment_text)

        # Prepare and send JSON response
        return JsonResponse({
            'status': 'success',
            'comment': {
                'text': comment.text,
                'id': comment.id
            }
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# view to change the status of an order
def change_order_status(request, order_id):
    if request.method == 'POST':
        try:
            # Try to get the order by its primary key (id)
            order = Order.objects.get(pk=order_id)

            # Determine if a new status is provided or should be determined automatically
            if 'status' in request.POST and request.POST.get('status'):
                # Use the provided new status
                new_status = request.POST.get('status')
            else:
                # No new status provided, determine automatically based on current status
                new_status = get_next_order_status(order.status)

            # If the order exists, change its status to the new status
            order.status = new_status
            # Save the changes to the database
            order.save()

            return JsonResponse({'status': 'success', 'message': 'Order status updated', 'new_status': new_status})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# view to delete an order
def delete_order(request, order_id):
    # Check if the request method is POST
    if request.method == 'POST':
        try:
            # Try to get the order by its primary key (id)
            order = Order.objects.get(pk=order_id)
            # If the order exists, delete it
            order.delete()
        except Order.DoesNotExist:
            # If the order does not exist, do nothing and pass
            pass
        # After attempting to delete the order, redirect to the orders page
        return HttpResponseRedirect(reverse('orders_page'))
    
def add_product_selection(request):
    return render(request, 'inventory/add_product_selection.html')

def add_product(request, product_type):
    # Dynamically get the model class based on the product_type
    model_class = getattr(models, product_type, None)
    if not model_class:
        # Handle the case where the model class doesn't exist
        return redirect('index')  # or some error page

    # Create a dynamic form for the model
    ProductForm = modelform_factory(model_class, exclude=())

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # or wherever you want to redirect after creation
    else:
        form = ProductForm()

    return render(request, 'inventory/product_form.html', {'form': form})

