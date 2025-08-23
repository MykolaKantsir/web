from django.db import models
from django.forms.models import model_to_dict
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from abc import abstractmethod
from pandas.core.frame import DataFrame
from .logging_config import logger
from .choices import Facet
from . import defaults
from . import choices
from . import utils

import math

# Create your models here.

# Describes general product model
class Product(models.Model):
    code = models.CharField(max_length=255, default=defaults.DefaultProduct.CODE)
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=defaults.DefaultProduct.TOOL_TYPE)
    ean = models.CharField(max_length=50, unique=True, default=defaults.DefaultProduct.EAN, blank=True)
    barcode = models.CharField(max_length=50, blank=True, db_index=True)
    manufacturer = models.CharField(max_length=50, choices=choices.Manufacturer.choices, default=defaults.DefaultProduct.MANUFACTURER)
    description = models.TextField(default=defaults.DefaultProduct.DESCRIPTION)
    link = models.URLField(max_length=300, default=defaults.DefaultProduct.LINK, blank=True)
    picture = models.URLField(default=defaults.DefaultProduct.PICTURE, blank=True)
    location = models.CharField(max_length=50, default=defaults.DefaultProduct.LOCATION, blank=True)
    quantity = models.PositiveIntegerField(default=defaults.DefaultProduct.QUANTITY)
    catalog_price = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultProduct.CATALOG_PRICE)
    facet_fields = [
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('catalog_price', 'Catalog price', choices.Facet.numerical),
        ]
    
    def __str__(self):
        return f'Product: {self.__class__}, {self.manufacturer}, {self.code}'
    
    
    def to_json(self) -> dict:
        # Use Django's model_to_dict to convert the model instance to a dictionary
        return model_to_dict(self)
    
    def get_label(self) -> list:
        descriptionLabel = Label(
            template=choices.LabelTemplates.DESCRIPTION_TEMPLATE,
            attributes={choices.LabelKeys.DESCRIPTION: str(self)}
        )
        # Check for too long description
        if len(str(self)) > 20:
            descriptionLabel.attributes[choices.LabelKeys.DESCRIPTION] = str(self)[:20]

        barcodeLabel = Label(
            template=choices.LabelTemplates.BARCODE_TEMPLATE,
            attributes={choices.LabelKeys.BARCODE: self.ean}
        )
        # Check for empty ean and barcode
        barcode_result = ""
        if self.ean != choices.Strings.EMPTY_STRING:
            barcode_result = self.ean
        elif self.barcode != choices.Strings.EMPTY_STRING:
            barcode_result = self.barcode
        else:
            barcode_result = self.code
        barcodeLabel.attributes[choices.LabelKeys.BARCODE] = barcode_result
        return [descriptionLabel, barcodeLabel]

    class Meta:
        abstract = True

# Describes a barcode of the product to be added
class ProductToBeAdded(models.Model):
    barcode = models.CharField(max_length=255, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.barcode

# Describes an order
class Order(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product_content_object = GenericForeignKey('content_type', 'object_id')
    order_date = models.DateField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=defaults.DefaultOrder.QUANTITY)
    status = models.CharField(max_length=50, choices=choices.OrderStatus.choices, default=defaults.DefaultOrder.STATUS)
    
    ordered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='inverrntory_orders'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the real save() method
        WeekOrders.add_order_to_week(self)  # Add this order to the appropriate WeekOrders

    def __str__(self):
        return f'Order: {self.quantity}, {self.content_type}, {self.order_date}, {self.status}'
    
    class Meta:
        verbose_name_plural = "Orders"
        ordering = ['-order_date']

# Describes a week orders
class WeekOrders(models.Model):
    year = models.IntegerField()
    week = models.IntegerField()
    orders = models.ManyToManyField(Order, related_name='week_orders')

    class Meta:
        unique_together = ('year', 'week')

    def __str__(self):
        return f"Week {self.week} of {self.year}"

    @classmethod
    def add_order_to_week(cls, order):
        year, week, _ = order.order_date.isocalendar()
        week_orders, created = cls.objects.get_or_create(year=year, week=week)
        week_orders.orders.add(order)

# Describe a comment for an order
class Comment(models.Model):
    order = models.ForeignKey(Order, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # add in author later
    # author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if len(self.text) < 30:
            return f'{self.order} - {self.text}'
        text_beginning = self.text[:30]
        return f'{self.order} - {text_beginning}...'


# Describes a material group to be machined [P, M, K, N, S, H, O]
class MaterialToBeMachined(models.Model):
    name = models.CharField(max_length=50, default=defaults.DefaultMaterialToBeMachined.NAME)
    colour = models.CharField(max_length=50, default=defaults.DefaultMaterialToBeMachined.COLOUR)
    group = models.CharField(max_length=1, default=defaults.DefaultMaterialToBeMachined.GROUP)
    
    def __str__(self):
        return f'{self.name}'

    def to_json(self) -> dict:
        # Use Django's model_to_dict to convert the model instance to a dictionary
        return model_to_dict(self)
    
    @classmethod
    def all_mtbm(cls) -> list:
        # Query the database to get all Mtbm instances except the one with the name choices.Strings.UNDEFINED
        return cls.objects.exclude(name=choices.Strings.UNDEFINED).all()
    
    @classmethod
    def get_undefined(cls):
        return cls.objects.get(name=choices.Strings.UNDEFINED)

    @classmethod
    def get_default_mtbm(cls):
        return cls.objects.get(name=defaults.DefaultMaterialToBeMachined.NAME).id
    
    class Meta:
        verbose_name_plural = "Materials to be machined"

# Describes a cutting tool (drill, cutter, mill, insert etc.)
class Tool(Product):
    material = models.CharField(
        max_length=50,
        choices=choices.ToolMaterial.choices,
        default=defaults.DefaultTool.MATERIAL,
        blank=True,
        null=True
        )
    coating = models.CharField(
        max_length=50,
        choices=choices.ToolCoating.choices,
        default=defaults.DefaultTool.COATING,
        blank=True,
        null=True
        )
    mtbm = models.ManyToManyField(
        MaterialToBeMachined,
        related_name='tools'
    )
    facet_fields = [
        ('material', 'Material', choices.Facet.categorical),
        ('coating', 'Coating', choices.Facet.categorical),
        ]

    def save(self, *args, **kwargs):
        self.material = choices.normalize_tool_material(self.material)
        super(Tool, self).save(*args, **kwargs)
    
    def add_mtbm(self, mtbm: MaterialToBeMachined):
        # Check if the mtbm to be added is the default one and should not be added
        if mtbm.name == defaults.DefaultTool.MTBM.NAME:
            # Perhaps log some message or handle the case where mtbm is the default one
            return

        # Remove the default MTBM if it's currently associated
        if self.mtbm.filter(name=defaults.DefaultTool.MTBM).exists():
            self.mtbm.remove(MaterialToBeMachined.objects.get(name=defaults.DefaultTool.MTBM))

        # Add the new MaterialToBeMachined to the mtbm set
        self.mtbm.add(mtbm)

    class Meta:
        abstract = True
   
# Describes a milling tool (end_mill, face_mill, chamfer etc)
class MillingTool(Tool):
    diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMillingTool.DIAMETER)
    overall_length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMillingTool.OVERALL_LENGTH)
    neck_diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMillingTool.NECK_DIAMETER)
    shank_diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMillingTool.SHANK_DIAMETER)
    flute_length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMillingTool.FLUTE_LENGTH)
    usable_length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMillingTool.USABLE_LENGTH)
    corner_radius = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMillingTool.CORNER_RADIUS)
    corner_chamfer = models.DecimalField(max_digits=10, decimal_places=3, default=defaults.DefaultMillingTool.CORNER_CHAMFER)
    number_of_flutes = models.PositiveIntegerField(default=defaults.DefaultMillingTool.NUMBER_OF_FLUTES)
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('flute_length', 'Flute length', choices.Facet.numerical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]    
    
    class Meta:
        abstract = True
        ordering = ['-diameter', '-flute_length', '-usable_length']

# Describes a drilling tool (drill, reamer, tap etc.)
class DrillingTool(Tool):
    diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultDrillingTool.DIAMETER)
    overall_length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultDrillingTool.OVERALL_LENGTH)
    point_angle = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultDrillingTool.POINT_ANGLE)
    number_of_flutes = models.PositiveIntegerField(default=defaults.DefaultDrillingTool.NUMBER_OF_FLUTES)
    flute_length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultDrillingTool.FLUTE_LENGTH)
    shank_diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultDrillingTool.SHANK_DIAMETER)
    usable_length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultDrillingTool.USABLE_LENGTH)
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('flute_length', 'Flute length', choices.Facet.numerical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ]
    
    class Meta:
        abstract = True
        ordering = ['-diameter', '-flute_length', '-usable_length']


# ==================================
# ============Mills=================
# ==================================

# Describes an end Mill
class EndMill(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.END_MILL)
    length_category = models.CharField(max_length=50, choices=choices.MillLengthCategory.choices, default=defaults.DefaultEndMill.LENGTH_CATEGORY)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='end_mills')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('length_category', 'Length category', choices.Facet.categorical),
        ('flute_length', 'Flute length', choices.Facet.numerical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('corner_radius', 'Corner radius', choices.Facet.numerical),
        ('corner_chamfer', 'Corner chamfer', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]
    
    def __str__(self):
        return f'{self.tool_type} {self.diameter} x {self.flute_length} x {self.usable_length} | {self.length_category}'
    
        # method to construct length category 
    def construct_length_category(self) -> None:
        if self.length_category.value == defaults.DefaultEndMill.LENGTH_CATEGORY.value:
            # Calculate the numeric ratio using the polynomial regression formula
            d = self.diameter
            l = self.usable_length
            # change this formula to correct one
            numeric_ratio = l/d

            # Map the numeric ratio to predefined categories
            if numeric_ratio <= 1:
                self.length_category = choices.MillLengthCategory.EXTRA_SHORT
            elif numeric_ratio <= 2:
                self.length_category = choices.MillLengthCategory.SHORT
            elif numeric_ratio <= 3.5:
                self.length_category = choices.MillLengthCategory.MEDIUM
            elif numeric_ratio <= 4.5:
                self.length_category = choices.MillLengthCategory.MEDIUM_PLUS
            elif numeric_ratio <= 5.5:
                self.length_category = choices.MillLengthCategory.LONG
            elif numeric_ratio <= 20:
                self.length_category = choices.MillLengthCategory.EXTRA_LONG
            else:
                self.length_category = choices.MillLengthCategory.UNKNOWN

    class Meta:
        verbose_name_plural = "End mills"
  
# Describes a chamfer mill
class ChamferMill(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.CHAMFER_MILL)
    angle = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultChamferMill.CHAMFER_ANGLE)
    point_diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultChamferMill.POINT_DIAMETER)
    max_chamfer_width = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultChamferMill.MAX_CHAMFER_WIDTH)
    is_rear_side_cutting = models.BooleanField(default=defaults.DefaultChamferMill.IS_REAR_SIDE_CUTTING)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='chamfer_mills')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('angle', 'Angle', choices.Facet.numerical),
        ('max_chamfer_width', 'Max chamfer width', choices.Facet.numerical),
        ('is_rear_side_cutting', 'Is double sided', choices.Facet.boolean, {
            'true_label': 'Yes',
            'false_label': 'No'
            }
            ),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]
    
    def __str__(self):
        double_side = 'Rear' if self.is_rear_side_cutting else ''
        return f'{self.tool_type} {self.diameter} x {self.angle} {double_side}'.strip()
    
    class Meta:
        verbose_name_plural = "Chamfer mills"

    
    # Method to construct maximum length of chamfer
    def construct_max_chamfer_width(self) -> None:
        # Calculate the half-angle in radians
        half_angle_rad = math.radians(self.angle / 2)
        
        # Calculate the maximum chamfer width
        chamfer_width = ((self.diameter - self.point_diameter) / 2) / math.sin(half_angle_rad)
        
        # Round chamfer width to the nearest 0.1 and store it
        self.max_chamfer_width = math.floor(chamfer_width * 10) / 10.0

# Describes a ball mill
class BallMill(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.BALL_MILL)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='ball_mills')
    facet_fields = [
        ('corner_radius', 'Corner radius', choices.Facet.numerical),
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('flute_length', 'Flute length', choices.Facet.numerical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('material', 'Material', choices.Facet.categorical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]

    def __str__(self):
        return f'{self.tool_type} {self.diameter}'
    
    # method to construct radius if not provided
    def construct_radius(self):
        self.corner_radius = self.diameter / 2

    class Meta:
        verbose_name_plural = "Ball mills"
        ordering = ['-diameter', '-flute_length']

# Describes a face mill
class FaceMill(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.FACE_MILL)
    face_angle = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultFaceMill.FACE_ANGLE)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='face_mills')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('face_angle', 'Face angle', choices.Facet.numerical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]

    class Meta:
        verbose_name_plural = "Face mills"

    def __str__(self):
        return f'{self.tool_type} {self.diameter}'

    def save(self, *args, **kwargs):
            self.material = None
            self.coating = None
            super(FaceMill, self).save(*args, **kwargs)

            # Set the mtbm field
            all_mtbm = MaterialToBeMachined.all_mtbm()
            self.mtbm.set(all_mtbm)

# Describes a thread mill
class ThreadMill(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.THREAD_MILL)
    thread = models.CharField(max_length=20, default=defaults.DefaultThreadMill.THREAD)
    thread_series = models.CharField(max_length=20, default=defaults.DefaultThreadMill.THREAD_SERIES)
    thread_pitch = models.CharField(max_length=20, default=defaults.DefaultThreadMill.THREAD_PITCH)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='thread_mills')
    facet_fields = [
        ('thread', 'Thread', choices.Facet.categorical),
        ('thread_series', 'Thread series', choices.Facet.categorical),
        ('thread_pitch', 'Thread pitch', choices.Facet.categorical),
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('flute_length', 'Flute length', choices.Facet.numerical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]
    
    def __str__(self):
        return f'{self.tool_type} {self.thread}'
    
    class Meta:
        verbose_name_plural = "Thread mills"
    
    def construct_thread_series(self):
        if self.thread_series == defaults.DefaultThreadMill.THREAD_SERIES:
            if self.thread.startswith('M'):
                self.thread_series = 'M'
            elif self.thread.startswith('G'):
                self.thread_series = 'G'
            elif self.thread.startswith('UNC'):
                self.thread_series = 'UNC'
            elif self.thread.startswith('UNF'):
                self.thread_series = 'UNF'
            else:
                self.thread_series = defaults.DefaultThreadMill.THREAD_SERIES

# Describes a radius mill
class RadiusMill(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.RADIUS_MILL)
    radius = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultRadiusMill.RADIUS)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='radius_mills')
    facet_fields = [
        ('radius', 'Radius', choices.Facet.numerical),
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('flute_length', 'Flute length', choices.Facet.numerical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('material', 'Material', choices.Facet.categorical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]
    
    class Meta:
        verbose_name_plural = "Radius mills"
        ordering = ['-radius', '-flute_length']

    def __str__(self):
        return f'{self.tool_type} {self.diameter} x {self.radius}'

    def construct_flute_length(self):
        self.flute_length = self.radius

    def construct_neck_diameter(self):
        self.neck_diameter = self.diameter + 2*self.radius

# Describes a lollipop mill
class LollipopMill(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.LOLLIPOP_MILL)
    neck_diameter = models.DecimalField(max_digits=5, decimal_places=2, default=defaults.DefaultLollipopMill.NECK_DIAMETER)
    mtbm = models.ManyToManyField(
        MaterialToBeMachined,
        related_name='lollipopmills'
    )
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('flute_length', 'Flute length', choices.Facet.numerical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('neck_diameter', 'Neck diameter', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]

    class Meta:
        verbose_name_plural = "Lollipop mills"
        ordering = ['-diameter', '-neck_diameter']

    def construct_radius(self):
        self.corner_radius = self.diameter / 2

    def __str__(self):
        return f'{self.tool_type} {self.diameter}'

# Describes a T-slot mill
class TSlotMill(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.TSLOT_MILL)
    thickness = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultTSlotMill.THICKNESS)
    cutting_depth_max = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultTSlotMill.CUTTING_DEPTH_MAX)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='tslot_mills')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('thickness', 'Thickness', choices.Facet.numerical),
        ('cutting_depth_max', 'Cutting depth max', choices.Facet.numerical),
        ('material', 'Material', choices.Facet.categorical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]

    class Meta:
        verbose_name_plural = "T-slot mills"
        ordering = ['-thickness', '-diameter']

    def __str__(self):
        return f'{self.tool_type} {self.diameter} x {self.thickness}'
    
    def construct_cutting_depth_max(self):
        self.cutting_depth_max = (self.diameter - self.neck_diameter)/2
    
# Describes a milling body
class MillingBody(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.MILLING_BODY)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='milling_bodies')

    def __str__(self):
        return f'{self.tool_type}'

    def save(self, *args, **kwargs):
            self.material = None
            self.coating = None
            super(MillingBody, self).save(*args, **kwargs)

            # Set the mtbm field
            all_mtbm = MaterialToBeMachined.all_mtbm()
            self.mtbm.set(all_mtbm)

# Describes a circular saw
class CircularSaw(MillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.CIRCULAR_SAW)
    thickness = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultCircularSaw.THICKNESS)
    cutting_depth_max = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultCircularSaw.CUTTING_DEPTH_MAX)
    inner_diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultCircularSaw.INNER_DIAMETER)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='circular_saws')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('thickness', 'Thickness', choices.Facet.numerical),
        ('cutting_depth_max', 'Cutting depth max', choices.Facet.numerical),
        ('inner_diameter', 'Inner diameter', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]

    class Meta:
        verbose_name_plural = "Circular saws"
        ordering = ['-thickness', '-diameter']

    def __str__(self):
        return f'{self.tool_type} {self.diameter} x {self.thickness}'
    
    def construct_cutting_depth_max(self):
        self.cutting_depth_max = (self.diameter - self.inner_diameter)/2

# ===============================
# ============Drills=============
# ===============================

# Describes a drill
class Drill(DrillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.DRILL)
    length_category = models.CharField(max_length=50, choices=choices.DrillLengthCategory.choices, default=defaults.DefaultDrill.LENGTH_CATEGORY)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='drills')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('length_category', 'Length category', choices.Facet.categorical),
        ('material', 'Material', choices.Facet.categorical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('number_of_flutes', 'Number of flutes', choices.Facet.numerical),
        ]
    
    def __str__(self):
        return f'{self.tool_type} {self.diameter} {self.length_category}'


    # method to construct length category if not provided
    def construct_length_category(self):
        if self.length_category == defaults.DefaultDrill.LENGTH_CATEGORY:
            # Calculate the numeric ratio using the polynomial regression formula
            d = self.diameter
            l = self.usable_length
            numeric_ratio = 3.86 - 0.85 * d + 0.14 * l + 0.07 * d**2 - 0.02 * d * l + 0.0007 * l**2

            # Map the numeric ratio to predefined categories
            if numeric_ratio <= 3:
                self.length_category = '3xD'
            elif numeric_ratio <= 5:
                self.length_category = '5xD'
            elif numeric_ratio <= 7:
                self.length_category = '7xD'
            elif numeric_ratio <= 8:
                self.length_category = '8xD'
            elif numeric_ratio <= 10:
                self.length_category = '10xD'
            elif numeric_ratio <= 12:
                self.length_category = '12xD'
            elif numeric_ratio <= 20:
                self.length_category = '20xD'
            else:
                self.length_category = defaults.DefaultDrill.LENTGTH_CATEGORY

# Describes a spot drill
class SpotDrill(DrillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.SPOT_DRILL)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='spot_drills')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('point_angle', 'Point angle', choices.Facet.numerical),
        ('material', 'Material', choices.Facet.categorical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ]
    
    def __str__(self):
        return f'{self.tool_type} {self.diameter} x {self.point_angle}'
    
    class Meta:
        verbose_name_plural = "Spot drills"

# Describes a reamer
class Reamer(DrillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.REAMER)
    tolerance = models.CharField(max_length=50, default=defaults.DefaultReamer.TOLERANCE)
    upper_tolerance = models.DecimalField(max_digits=10, decimal_places=3, default=defaults.DefaultReamer.UPPER_TOLERANCE)
    lower_tolerance = models.DecimalField(max_digits=10, decimal_places=3, default=defaults.DefaultReamer.LOWER_TOLERANCE)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='reamers')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('tolerance', 'Tolerance', choices.Facet.categorical),
        ('upper_tolerance', 'Upper tolerance', choices.Facet.numerical),
        ('lower_tolerance', 'Lower tolerance', choices.Facet.numerical),
        ('material', 'Material', choices.Facet.categorical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ]
    
    def __str__(self):
        res = None
        if self.tolerance == defaults.DefaultReamer.TOLERANCE:
            res = f'{self.tool_type} {self.diameter} : {self.upper_tolerance}/{self.lower_tolerance}'
        else:
            res = f'{self.tool_type} {self.diameter} : {self.tolerance}'
        return res


# Describes a tap
class Tap(DrillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.TAP)
    diameter = models.DecimalField(max_digits=10, decimal_places=3, default=defaults.DefaultTap.DIAMETER)
    shank_diameter = models.DecimalField(max_digits=10, decimal_places=3, default=defaults.DefaultTap.SHANK_DIAMETER)
    pitch = models.DecimalField(max_digits=10, decimal_places=3, default=defaults.DefaultTap.PITCH)
    thread = models.CharField(max_length=20, default=defaults.DefaultTap.THREAD)
    thread_series = models.CharField(max_length=20, default=defaults.DefaultTap.THREAD_SERIES)
    thread_class = models.CharField(max_length=20, default=defaults.DefaultTap.THREAD_CLASS)
    tap_type = models.CharField(max_length=20, choices=choices.TapType.choices, default=defaults.DefaultTap.TAP_TYPE)
    tap_hole_diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultTap.TAP_HOLE_DIAMETER)
    tap_thread_length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultTap.TAP_THREAD_LENGTH)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='taps')
    facet_fields = [
        ('thread', 'Thread', choices.Facet.categorical),
        ('tap_type', 'Tap type', choices.Facet.categorical),
        ('pitch', 'Pitch', choices.Facet.numerical),
        ('thread_series', 'Thread series', choices.Facet.categorical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('thread_class', 'Thread class', choices.Facet.categorical),
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ]

    def __str__(self):
        return f'{self.tool_type} {self.thread} {self.tap_type}'
    
    class Meta:
        verbose_name_plural = "Taps"

    def construct_from_thread(self, series = None):
        self.diameter = utils.get_tap_diameter(self.thread, series=series)


# Describes a center drill
class CenterDrill(DrillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.CENTER_DRILL)
    step_angle = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultCenterDrill.STEP_ANGLE)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='center_drills')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('step_angle', 'Step angle', choices.Facet.numerical),
        ('material', 'Material', choices.Facet.categorical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ]

    def __str__(self):
        return f'{self.diameter} x {self.step_angle}'

    class Meta:
        verbose_name_plural = "Center drills"

# Deascribes a U-drill
class U_Drill(DrillingTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.U_DRILL)
    max_diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultU_Drill.MAX_DIAMETER)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='udrills')
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('max_diameter', 'Max diameter', choices.Facet.numerical),
        ('usable_length', 'Usable length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ]

    def __str__(self):
        return f'{self.tool_type} {self.diameter}'
    
    class Meta:
        verbose_name_plural = "U-drills"

    def save(self, *args, **kwargs):
        self.material = None
        self.coating = None
        super(U_Drill, self).save(*args, **kwargs)

        # Set the mtbm field
        all_mtbm = MaterialToBeMachined.all_mtbm()
        self.mtbm.set(all_mtbm)


# ================================
# ============Cutters=============
# ================================

# Describes an external cutter
class ExternalCutter(Tool):
    insert_iso_code = models.CharField(max_length=50, default=defaults.DefaultExternalCutter.MASTER_INSERT_ISO_CODE)
    cutter_iso_code = models.CharField(max_length=50, default=defaults.DefaultExternalCutter.CUTTER_ISO_CODE)
    facet_fields = [
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    class Meta:
        abstract = True
        ordering = ['cutter_iso_code']

# Describes an internal cutter
class InternalCutter(Tool):
    insert_iso_code = models.CharField(max_length=50, default=defaults.DefaultInternalCutter.MASTER_INSERT_ISO_CODE)
    cutter_iso_code = models.CharField(max_length=50, default=defaults.DefaultInternalCutter.CUTTER_ISO_CODE)
    min_bore_diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultInternalCutter.MIN_BORE_DIAMETER)
    overall_length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultInternalCutter.OVERALL_LENGTH)
    functional_length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultInternalCutter.FUNCTIONAL_LENGTH)
    facet_fields = [
        ('min_bore_diameter', 'Min bore diameter', choices.Facet.numerical),
        ('functional_length', 'Functional length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    class Meta:
        abstract = True
        ordering = ['min_bore_diameter', 'cutter_iso_code', '-functional_length']

# Describes a general external cutter
class GeneralCutter(ExternalCutter):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.GENERAL_CUTTER)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='general_cutters')
    facet_fields = [
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    def __str__(self):
        if self.cutter_iso_code != defaults.DefaultExternalCutter.CUTTER_ISO_CODE:
            return f'{self.manufacturer} {self.tool_type} {self.cutter_iso_code}'
        else:
            return f'{self.manufacturer} {self.tool_type} {self.insert_iso_code}'
        
    class Meta:
        verbose_name_plural = "General cutters"

    def save(self, *args, **kwargs):
        self.material = None
        self.coating = None
        super(GeneralCutter, self).save(*args, **kwargs)

        # Set the mtbm field
        all_mtbm = MaterialToBeMachined.all_mtbm()
        self.mtbm.set(all_mtbm)

# Desribes a boring cutter
class BoringCutter(InternalCutter):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.BORING_CUTTER)
    angle = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultBoringCutter.ANGLE)
    facet_fields = [
        ('min_bore_diameter', 'Min bore diameter', choices.Facet.numerical),
        ('angle', 'Angle', choices.Facet.numerical),
        ('functional_length', 'Functional length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    def __str__(self):
        if self.cutter_iso_code != defaults.DefaultInternalCutter.CUTTER_ISO_CODE:
            return f'{self.manufacturer} {self.tool_type} {self.cutter_iso_code}'
        else:
            return f'{self.manufacturer} {self.tool_type} {self.insert_iso_code}'
    
    class Meta:
        verbose_name_plural = "Boring cutters"

    # Constructs angle from iso code
    def construct_from_iso_code(self):
        angle_corresponding_letter = self.cutter_iso_code[7]
        self.angle = defaults.DefaultBoringCutter().iso_code_values['angle'][angle_corresponding_letter]


    def save(self, *args, **kwargs):
        self.material = None
        self.coating = None
        super(BoringCutter, self).save(*args, **kwargs)

        # Set the mtbm field
        all_mtbm = MaterialToBeMachined.all_mtbm()
        self.mtbm.set(all_mtbm)

# Describes a solid internal cutter
class SolidBoringCutter(InternalCutter):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.SOLID_BORING_CUTTER)
    material = models.CharField(max_length=50, default=defaults.DefaultSolidBoringCutter.MATERIAL)
    angle = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultSolidBoringCutter.ANGLE)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='solid_boring_cutters')
    facet_fields = [
        ('min_bore_diameter', 'Min bore diameter', choices.Facet.numerical),
        ('angle', 'Angle', choices.Facet.numerical),
        ('functional_length', 'Functional length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    class Meta:
        verbose_name_plural = "Solid boring cutters"


    def __str__(self):
        res = f'{self.manufacturer} {self.tool_type}'
        if self.min_bore_diameter != defaults.DefaultInternalCutter.MIN_BORE_DIAMETER:
            res += f' {self.min_bore_diameter}'
            if self.functional_length != defaults.DefaultInternalCutter.FUNCTIONAL_LENGTH:
                res += f' x {self.functional_length}'
        return res

# Describes an external grooving cutter
class GroovingExternalCutter(ExternalCutter):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.GROOVING_EXTERNAL_CUTTER)
    cutting_width = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultGroovingExternalCutter.CUTTING_WIDTH)
    max_cutting_depth = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultGroovingExternalCutter.MAX_CUTTING_DEPTH)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='grooving_external_cutters')
    facet_fields = [
        ('cutting_width', 'Cutting width', choices.Facet.numerical),
        ('max_cutting_depth', 'Max cutting depth', choices.Facet.numerical),
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    def __str__(self):
        if self.cutting_width != defaults.DefaultGroovingExternalCutter.CUTTING_WIDTH:
            return f'{self.manufacturer} {self.tool_type} {self.cutting_width}'
        else:
            return f'{self.manufacturer} {self.tool_type}'
        
    class Meta:
        verbose_name_plural = "Grooving external cutters"

    def save(self, *args, **kwargs):
        self.material = None
        self.coating = None
        super(GroovingExternalCutter, self).save(*args, **kwargs)

        # Set the mtbm field
        all_mtbm = MaterialToBeMachined.all_mtbm()
        self.mtbm.set(all_mtbm)

# Describes an internal grooving cutter
class GroovingInternalCutter(InternalCutter):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.GROOVING_INTERNAL_CUTTER)
    cutting_width = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultGroovingInternalCutter.CUTTING_WIDTH)
    max_cutting_depth = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultGroovingInternalCutter.MAX_CUTTING_DEPTH)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='grooving_internal_cutters')
    facet_fields = [
        ('cutting_width', 'Cutting width', choices.Facet.numerical),
        ('max_cutting_depth', 'Max cutting depth', choices.Facet.numerical),
        ('min_bore_diameter', 'Min bore diameter', choices.Facet.numerical),
        ('functional_length', 'Functional length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]
    
    def __str__(self):
        if self.cutting_width != defaults.DefaultGroovingInternalCutter.CUTTING_WIDTH:
            return f'{self.manufacturer} {self.tool_type} {self.cutting_width}'
        else:
            return f'{self.manufacturer} {self.tool_type}'
        
    class Meta:
        verbose_name_plural = "Grooving internal cutters"

    def save(self, *args, **kwargs):
        self.material = None
        self.coating = None
        super(GroovingInternalCutter, self).save(*args, **kwargs)

        # Set the mtbm field
        all_mtbm = MaterialToBeMachined.all_mtbm()
        self.mtbm.set(all_mtbm)

# Describe a solid grooving cutter
class SolidGroovingCutter(InternalCutter):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.SOLID_GROOVING_CUTTER)
    cutting_width = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultSolidGroovingCutter.CUTTING_WIDTH)
    max_cutting_depth = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultSolidGroovingCutter.MAX_CUTTING_DEPTH)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='solid_grooving_cutters')
    facet_fields = [
        ('cutting_width', 'Cutting width', choices.Facet.numerical),
        ('max_cutting_depth', 'Max cutting depth', choices.Facet.numerical),
        ('min_bore_diameter', 'Min bore diameter', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('functional_length', 'Functional length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    class Meta:
        verbose_name_plural = "Solid grooving cutters"

    def __str__(self):
        if self.cutting_width != defaults.DefaultSolidGroovingCutter.CUTTING_WIDTH:
            return f'{self.manufacturer} {self.tool_type} {self.cutting_width}'
        else:
            return f'{self.manufacturer} {self.tool_type}'
    
# Describes a thread external cutter
class ThreadExternalCutter(ExternalCutter):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.THREAD_EXTERNAL_CUTTER)
    is_metric = models.BooleanField(default=defaults.DefaultThreadCutter.IS_METRIC)
    is_inch = models.BooleanField(default=defaults.DefaultThreadCutter.IS_INCH)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='thread_external_cutters')
    facet_fields = [
        ('is_metric', 'Is metric', choices.Facet.boolean, {'true_label': 'Metric', 'false_label': 'Inch'}),
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    def __str__(self):
        return f'{self.manufacturer} {self.tool_type}'
    
    class Meta:
        verbose_name_plural = "Thread external cutters"

    
    def save(self, *args, **kwargs):
        self.material = None
        self.coating = None
        super(ThreadExternalCutter, self).save(*args, **kwargs)

        # Set the mtbm field
        all_mtbm = MaterialToBeMachined.all_mtbm()
        self.mtbm.set(all_mtbm)
    
# Describes a thread internal cutter
class ThreadInternalCutter(InternalCutter):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.THREAD_INTERNAL_CUTTER)
    is_metric = models.BooleanField(default=defaults.DefaultThreadCutter.IS_METRIC)
    is_inch = models.BooleanField(default=defaults.DefaultThreadCutter.IS_INCH)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='thread_internal_cutters')
    facet_fields = [
        ('is_metric', 'Is metric', choices.Facet.boolean, {'true_label': 'Metric', 'false_label': 'Inch'}),
        ('min_bore_diameter', 'Min bore diameter', choices.Facet.numerical),
        ('functional_length', 'Functional length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    def __str__(self):
        return f'{self.manufacturer} {self.tool_type}'
    
    class Meta:
        verbose_name_plural = "Thread internal cutters"

    def save(self, *args, **kwargs):
        self.material = None
        self.coating = None
        super(ThreadInternalCutter, self).save(*args, **kwargs)

        # Set the mtbm field
        all_mtbm = MaterialToBeMachined.all_mtbm()
        self.mtbm.set(all_mtbm)

# Describes a solid thread cutter
class SolidThreadCutter(InternalCutter):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.SOLID_THREAD_CUTTER)
    is_metric = models.BooleanField(default=defaults.DefaultThreadCutter.IS_METRIC)
    is_inch = models.BooleanField(default=defaults.DefaultThreadCutter.IS_INCH)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='solid_thread_cutters')
    facet_fields = [
        ('is_metric', 'Is metric', choices.Facet.boolean, {'true_label': 'Metric', 'false_label': 'Inch'}),
        ('min_bore_diameter', 'Min bore diameter', choices.Facet.numerical),
        ('functional_length', 'Functional length', choices.Facet.numerical),
        ('overall_length', 'Overall length', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('cutter_iso_code', 'Cutter ISO code', choices.Facet.categorical),
        ('insert_iso_code', 'Insert ISO code', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
    ]

    class Meta:
        verbose_name_plural = "Solid thread cutters"

    def __str__(self):
        return f'{self.manufacturer} {self.tool_type}'

# ================================
# ============Inserts=============
# ================================

# Describes an insert
class Insert(Tool):
    chip_breaker = models.CharField(max_length=20, default=defaults.DefaultInsert.CHIP_BREAKER)
    facet_fields = [
        ('chip_breaker', 'Chip breaker', choices.Facet.categorical),
    ]

    class Meta:
        abstract = True
        ordering = ['chip_breaker']

# Describes a milling insert
class MillingInsert(Insert):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.INSERT_MILLING)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='milling_inserts')
    facet_fields = [
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('chip_breaker', 'Chip breaker', choices.Facet.categorical),
    ]

    def __str__(self):
        return f'{self.manufacturer} {self.tool_type}'
    
    class Meta:
        verbose_name_plural = "Milling inserts"

# Describes a drilling insert
class DrillingInsert(Insert):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.INSERT_DRILLING)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='drilling_inserts')
    facet_fields = [
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('chip_breaker', 'Chip breaker', choices.Facet.categorical),
    ]

    def __str__(self):
        return f'{self.manufacturer} {self.tool_type}'
    
    class Meta:
        verbose_name_plural = "Drilling inserts"

# Describes a turning insert
class TurningInsert(Insert):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.INSERT_TURNING)
    isocode = models.CharField(max_length=20, default=defaults.DefaultInsertTurning.ISOCODE)
    shape = models.CharField(max_length=20, default=defaults.DefaultInsertTurning.SHAPE)
    relief_angle = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultInsertTurning.RELIEF_ANGLE)
    tolerance = models.CharField(max_length=20, default=defaults.DefaultInsertTurning.TOLERANCE)
    cross_section = models.CharField(max_length=20, default=defaults.DefaultInsertTurning.CROSS_SECTION)
    insert_size = models.CharField(max_length=20, default=defaults.DefaultInsertTurning.INSERT_SIZE)
    thickness = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultInsertTurning.THICKNESS)
    corner_radius = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultInsertTurning.CORNER_RADIUS)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='turning_inserts')
    facet_fields = [
        ('isocode', 'ISO code', choices.Facet.categorical),
        ('corner_radius', 'Corner radius', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('shape', 'Shape', choices.Facet.categorical),
        ('relief_angle', 'Relief angle', choices.Facet.numerical),
        ('tolerance', 'Tolerance', choices.Facet.categorical),
        ('cross_section', 'Cross section', choices.Facet.categorical),
        ('insert_size', 'Insert size', choices.Facet.categorical),
        ('thickness', 'Thickness', choices.Facet.numerical),
    ]

    def __str__(self):
        #return f'{self.tool_type} {self.isocode}'
        return f'{self.isocode}'
    
    class Meta:
        verbose_name_plural = "Turning inserts"

    def construct_iso_code(self):
        rev_abr = defaults.InsertAbreviations.reversed_values
        self.isocode = (
            rev_abr['shape'][str(self.shape)]
            + rev_abr['relief_angle'][str(self.relief_angle)]
            + rev_abr['tolerance'][str(self.tolerance)]
            + rev_abr['cross_section'][str(self.cross_section)]
            + rev_abr['insert_size'][str(self.insert_size)]
            + rev_abr['thickness'][str(self.thickness)]
            + rev_abr['corner_radius'][str(self.corner_radius)]
            )
        return self.isocode
    
    def deconstruct_iso_code(self):
        abr = defaults.InsertAbreviations.values
        self.shape = abr['shape'][self.isocode[0]][0]
        self.relief_angle = abr['relief_angle'][self.isocode[1]]
        self.tolerance = abr['tolerance'][self.isocode[2]]
        self.cross_section = abr['cross_section'][self.isocode[3]]
        self.insert_size = abr['insert_size'][self.isocode[4:6]]
        self.thickness = abr['thickness'][self.isocode[6:8]]
        self.corner_radius = abr['corner_radius'][self.isocode[8:10]]    

    class Meta:
        ordering = ['isocode']

# Describes a thread insert
class ThreadInsert(Insert):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.INSERT_THREAD)
    thread_type = models.CharField( # Internal or external
        max_length=20,
        default=defaults.DefaultInsertThreading.THREAD_TYPE
        )
    thread_profile = models.CharField( # ISO, UN, Trapezoidal, etc.
        max_length=20,
        default=defaults.DefaultInsertThreading.THREAD_PROFILE
        )
    thread_pitch = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=defaults.DefaultInsertThreading.THREAD_PITCH
        )
    thread_pitch_second = models.DecimalField( # second value for double pitch inserts
        max_digits=10,
        decimal_places=3,
        default=defaults.DefaultInsertThreading.THREAD_PITCH_SECOND
        )
    thread_tpi = models.IntegerField(default=defaults.DefaultInsertThreading.THREAD_TPI)
    thread_tpi_second = models.IntegerField( # second value for double pitch inserts
        default=defaults.DefaultInsertThreading.THREAD_TPI_SECOND
        )
    thread_profile_type = models.CharField( # Full profile, partial profile
        max_length=20,
        default=defaults.DefaultInsertThreading.THREAD_PROFILE_TYPE
        )
    thread_width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=defaults.DefaultInsertThreading.THREAD_WIDTH
        )
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='thread_inserts')
    facet_fields = [
        ('thread_type', 'Thread type', choices.Facet.categorical),
        ('thread_profile', 'Thread profile', choices.Facet.categorical),
        ('thread_pitch', 'Thread pitch', choices.Facet.numerical),
        ('thread_tpi', 'Thread TPI', choices.Facet.numerical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('thread_profile_type', 'Thread profile type', choices.Facet.categorical),
        ('thread_width', 'Thread width', choices.Facet.numerical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
    ]

    def __str__(self):
        res = ''
        if self.thread_pitch != defaults.DefaultInsertThreading.THREAD_PITCH:
            res = self.thread_pitch
        if self.thread_tpi != defaults.DefaultInsertThreading.THREAD_TPI:
            res = self.thread_tpi
        return f'TurningInsert: {self.manufacturer} {self.thread_profile} {res} {self.thread_type}'

    class Meta:
        verbose_name_plural = "Thread inserts"

    # check if thread type is metric or imperial
    def check_thread_profile(self):
        if self.thread_profile == defaults.DefaultInsertThreading.THREAD_PROFILE:
            if self.thread_tpi != defaults.DefaultInsertThreading.THREAD_TPI:
                self.thread_profile = 'Imperial'
            elif self.thread_pitch != defaults.DefaultInsertThreading.THREAD_PITCH:
                self.thread_profile = 'Metric'

    class Meta:
        ordering = ['thread_profile', 'thread_pitch', 'thread_type', 'thread_tpi']

# Describes a grooving insert
class GroovingInsert(Insert):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.INSERT_GROOVING)
    width = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultInsertGrooving.WIDTH)
    max_cut_depth = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultInsertGrooving.MAX_CUT_DEPTH_GR)
    min_cut_diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultInsertGrooving.MIN_CUT_DIAMETER)
    mtbm = models.ManyToManyField(MaterialToBeMachined, related_name='grooving_inserts')
    facet_fields = [
        ('width', 'Width', choices.Facet.numerical),
        ('manufacturer', 'Manufacturer', choices.Facet.categorical),
        ('chip_breaker', 'Chip breaker', choices.Facet.categorical),
        ('mtbm', 'MTBM', choices.Facet.categorical),
        ('max_cut_depth', 'Max cut depth', choices.Facet.numerical),
        ('min_cut_diameter', 'Min cut diameter', choices.Facet.numerical),
    ]

    def __str__(self):
        return f'{self.manufacturer} {self.tool_type} {self.width}'
    
    class Meta:
        ordering = ['width']
        verbose_name_plural = "Grooving inserts"

# =====================================
# ============ Equipment ==============
# =====================================

# Describes an equipment (holder, adapter, etc.)
class Equipment(Product):

    class Meta:
        abstract = True
    
    def __str__(self):
        return f'{self.manufacturer} {self.tool_type} {self.code}'
    
# Describes a milling equipment
class EquipmentMilling(Equipment):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.EQUIPMENT_MILLING)
    class Meta:
        ordering = ['code']
        verbose_name_plural = 'Equipments Milling'
    
# Describes a turning equipment
class EquipmentTurning(Equipment):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.EQUIPMENT_TURNING)
    class Meta:
        ordering = ['code']
        verbose_name_plural = 'Equipments Turning'
    
# Describes a measuring equipment
class MeasurementTool(Equipment):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.MEASURING)
    min = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMeasurementTool.MIN)
    max = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMeasurementTool.MAX)
    precision = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMeasurementTool.PRECISION)
    facet_fields = [
        ('min', 'Min', choices.Facet.numerical),
        ('max', 'Max', choices.Facet.numerical),
        ('precision', 'Precision', choices.Facet.numerical),
    ]

    class Meta:
        verbose_name_plural = 'Measurment tools'

# Describes a thread gauge
class ThreadGauge(Equipment):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.THREAD_GAUGE)
    gouge_type = models.CharField(max_length=20, choices=choices.ThreadGaugeType.choices, default=choices.ThreadGaugeType.GO_NO_GO)
    thread_profile = models.CharField(max_length=20, default=defaults.DefaultThreadGauge.THREAD_PROFILE)
    thread_pitch = models.DecimalField(max_digits=10, decimal_places=3, default=defaults.DefaultThreadGauge.THREAD_PITCH)
    thread_tpi = models.IntegerField(default=defaults.DefaultThreadGauge.THREAD_TPI)
    facet_fields = [
        ('gouge_type', 'Thread type', choices.Facet.categorical),
        ('thread_profile', 'Thread profile', choices.Facet.categorical),
        ('thread_pitch', 'Thread pitch', choices.Facet.numerical),
        ('thread_tpi', 'Thread TPI', choices.Facet.numerical),
    ]

    class Meta:
        verbose_name_plural = 'Thread gauges'

# Describes a gauge
class Gauge(Equipment):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.GAUGE)
    min = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultGauge.MIN)
    max = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultGauge.MAX)
    facet_fields = [
        ('min', 'Min', choices.Facet.numerical),
        ('max', 'Max', choices.Facet.numerical),
    ]

    class Meta:
        verbose_name_plural = 'Gauges'

# Describes a measuring pin
class MeasuringPin(Equipment):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.MEASURING_PIN)
    diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMeasuringPin.DIAMETER)
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
    ]

    class Meta:
        verbose_name_plural = 'Measuring pins'

# Describes a milling holder
class MillingHolder(Equipment):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.MILLING_HOLDER)
    name = models.CharField( # SK40-25-100
        max_length=50, 
        default=defaults.DefaultMillingHolder.NAME
        )
    length = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMillingHolder.LENGTH)
    diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultMillingHolder.DIAMETER)
    holder_type = models.CharField( # ER, Weldon, Shrink, etc.
        max_length=50, 
        default=defaults.DefaultMillingHolder.HOLDER_TYPE
        )
    facet_fields = [
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('holder_type', 'Holder type', choices.Facet.categorical),
        ('length', 'Length', choices.Facet.numerical),
    ]

    class Meta:
        ordering = ['diameter', 'name']
        verbose_name_plural = 'Milling holders'

# Describes a collet
class Collet(Equipment):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.COLLET)
    type = models.CharField(max_length=20, default=defaults.DefaultCollet.TYPE)
    diameter = models.DecimalField(max_digits=10, decimal_places=2, default=defaults.DefaultCollet.DIAMETER)
    is_sealed = models.BooleanField(default=defaults.DefaultCollet.IS_SEALED)
    facet_fields = [
        ('type', 'Type', choices.Facet.categorical),
        ('diameter', 'Diameter', choices.Facet.numerical),
        ('is_sealed', 'Is sealed', choices.Facet.boolean, {'true_label': 'Sealed', 'false_label': 'Not sealed'}),
    ]

    def __str__(self):
        sealed = 'Sealed' if self.is_sealed else ''
        return f'{self.type} {self.diameter} {sealed}'.strip()

    class Meta:
        ordering = ['type', 'diameter']
        verbose_name_plural = 'Collets'

# Describes a workholding equipment(vice, clamp, etc.)
class Workholding(Equipment):
    def __init__(self):
        return super().__init__()

# =====================================
# ============== Items ================
# =====================================

# Describes a spare part (screw, shim, nut, etc.)
class Item(Product):
    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.manufacturer} {self.tool_type} {self.code}'
    
# Describes a shim
class Shim(Item):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.SHIM)
    class Meta:
        ordering = ['code']

# Describes a screw
class Screw(Item):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.SCREW)
    class Meta:
        ordering = ['code']

# Describes a manual tool (screwdriver, wrench, etc.)
class ManualTool(Item):
    class Meta:
        abstract = True

# Describes a screwdriver
class Screwdriver(ManualTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.SCREWDRIVER)
    screwdriver_size = models.CharField(max_length=20, default=defaults.DefaultScrewdriver.SCREWDRIVER_SIZE)
    facet_fields = [
        ('screwdriver_size', 'Screwdriver size', choices.Facet.categorical),
    ]

    def __str__(self):
        if self.screwdriver_size != defaults.DefaultScrewdriver.SCREWDRIVER_SIZE:
            return f'{self.tool_type} {self.screwdriver_size}'
        else:
            return super().__str__()

    class Meta:
        ordering = ['screwdriver_size']

# Describes a key tool
class Key(ManualTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.KEY)
    key_size = models.CharField(max_length=20, default=defaults.DefaultKey.KEY_SIZE)
    facet_fields = [
        ('key_size', 'Key size', choices.Facet.categorical),
    ]

    def __str__(self):
        if self.key_size != defaults.DefaultKey.KEY_SIZE:
            return f'{self.tool_type} {self.key_size}'
        else:
            return super().__str__()

    class Meta:
        ordering = ['key_size']

# Describes a wrench
class Wrench(ManualTool):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.WRENCH)
    class Meta:
        ordering = ['code']
        verbose_name_plural = 'Wrenches'

# Describes items that are used in post machining (helicoil inserts, etc.)
class PostMachining(Item):
    tool_type = models.CharField(max_length=50, choices=choices.ToolType.choices, default=choices.ToolType.POST_MACHINING)
    class Meta:
        ordering = ['code']
        verbose_name_plural = 'Post machining items'

class NonAbstractProduct:
    non_abstract_list = [
        ChamferMill,
        BallMill,
        FaceMill,
        ThreadMill,
        RadiusMill,
        LollipopMill,
        TSlotMill,
        MillingBody,
        CircularSaw,
        Drill,
        SpotDrill,
        Reamer,
        Tap,
        CenterDrill,
        U_Drill,
        GeneralCutter,
        GroovingExternalCutter,
        ThreadExternalCutter,
        BoringCutter,
        SolidBoringCutter,
        GroovingInternalCutter,
        SolidGroovingCutter,
        ThreadInternalCutter,
        SolidThreadCutter,
        MillingInsert,
        DrillingInsert,
        TurningInsert,
        ThreadInsert,
        GroovingInsert,
        EquipmentMilling,
        EquipmentTurning,
        MeasurementTool,
        ThreadGauge,
        Gauge,
        MeasuringPin,
        MillingHolder,
        Collet,
        Workholding,
        Shim,
        Screw,
        PostMachining,
        Screwdriver,
        Key,
        Wrench,
        EndMill,
        ChamferMill,
        BallMill,
        FaceMill,
        ThreadMill,
        RadiusMill,
        LollipopMill,
        TSlotMill,
        MillingBody,
        CircularSaw,
        Drill,
        SpotDrill,
        Reamer,
        Tap,
        CenterDrill,
        U_Drill,
        GeneralCutter,
        GroovingExternalCutter,
        ThreadExternalCutter,
        BoringCutter,
        SolidBoringCutter,
        GroovingInternalCutter,
        SolidGroovingCutter,
        ThreadInternalCutter,
        SolidThreadCutter,
        MillingInsert,
        DrillingInsert,
        TurningInsert,
        ThreadInsert,
        GroovingInsert,
        Screwdriver,
        Key,
        Wrench
        ]
    matching_dict = {
        'Insert turning': TurningInsert,
        'Insert thread': ThreadInsert,
        'Insert cutoff': GroovingInsert,
        'Insert drilling': DrillingInsert,
        'Insert milling': MillingInsert,
        'General cutter': GeneralCutter,
        'Boring cutter': BoringCutter,
        'Solid boring cutter': SolidBoringCutter,
        'Solid grooving cutter': SolidGroovingCutter,
        'Grooving external cutter': GroovingExternalCutter,
        'Grooving internal cutter': GroovingInternalCutter,
        'Solid thread cutter': SolidThreadCutter,
        'Thread external cutter': ThreadExternalCutter,
        'Thread internal cutter': ThreadInternalCutter,
        'Drill': Drill,
        'Tap': Tap,
        'Spot drill': SpotDrill,
        'Reamer': Reamer,
        'Center drill': CenterDrill,
        'U-Drill': U_Drill,
        'Mill': EndMill,
        'Face mill': FaceMill,
        'Chamfer mill': ChamferMill,
        'Ball mill': BallMill,
        'Radius mill': RadiusMill,
        'T-Slot mill': TSlotMill,
        'Circular saw': CircularSaw,
        'Lollipop mill': LollipopMill,
        'Milling body': MillingBody,
        'Screw': Screw,
        'Screwdriver': Screwdriver,
        'Key': Key,
        'Wrench': Wrench,
        'Shim': Shim,
        'Post machining': PostMachining,
        'Collet': Collet,
        'Gauge': Gauge,
        'Thread gauge': ThreadGauge,
        'Measuring pin': MeasuringPin,
        'Equipment turning': EquipmentTurning,
        'Equipment milling': EquipmentMilling,
        'Measurement tool': MeasurementTool,
        'Milling holder': MillingHolder
        }


# Product factory class
class ProductFactory():
    def get_product(self, product: Product=None, tool_type_str: str=None):
        # Determine the tool type
        if product:
            tool_type = product.tool_type
        elif tool_type_str:
            tool_type = tool_type_str
        else:
            logger.error('No product or tool type provided')
            return Product()
        if tool_type == choices.ToolType.END_MILL:
            return EndMill()
        elif tool_type == choices.ToolType.DRILL:
            return Drill()
        elif tool_type == choices.ToolType.TAP:
            return Tap()
        elif tool_type == choices.ToolType.INSERT_TURNING:
            return TurningInsert()
        elif tool_type == choices.ToolType.COLLET:
            return Collet()
        elif tool_type == choices.ToolType.INSERT_THREAD:
            return ThreadInsert()
        elif tool_type == choices.ToolType.SPOT_DRILL:
            return SpotDrill()
        elif tool_type == choices.ToolType.CHAMFER_MILL:
            return ChamferMill()
        elif tool_type == choices.ToolType.REAMER:
            return Reamer()
        elif tool_type == choices.ToolType.INSERT_GROOVING:
            return GroovingInsert()
        elif tool_type == choices.ToolType.BALL_MILL:
            return BallMill()
        elif tool_type == choices.ToolType.INSERT_MILLING:
            return MillingInsert()
        elif tool_type == choices.ToolType.THREAD_MILL:
            return ThreadMill()
        elif tool_type == choices.ToolType.BORING_CUTTER:
            return BoringCutter()
        elif tool_type == choices.ToolType.RADIUS_MILL:
            return RadiusMill()
        elif tool_type == choices.ToolType.INSERT_DRILLING:
            return DrillingInsert()
        elif tool_type == choices.ToolType.CENTER_DRILL:
            return CenterDrill()
        elif tool_type == choices.ToolType.U_DRILL:
            return U_Drill()
        elif tool_type == choices.ToolType.LOLLIPOP_MILL:
            return LollipopMill()
        elif tool_type == choices.ToolType.TSLOT_MILL:
            return TSlotMill()
        elif tool_type == choices.ToolType.MILLING_HOLDER:
            return MillingHolder()
        elif tool_type == choices.ToolType.CIRCULAR_SAW:
            return CircularSaw()
        elif tool_type == choices.ToolType.POST_MACHINING:
            return PostMachining()
        elif tool_type == choices.ToolType.MEASURING:
            return MeasurementTool()
        elif tool_type == choices.ToolType.EQUIPMENT_TURNING:
            return EquipmentTurning()
        elif tool_type == choices.ToolType.EQUIPMENT_MILLING:
            return EquipmentMilling()
        elif tool_type == choices.ToolType.MILLING_BODY:
            return MillingBody()
        elif tool_type == choices.ToolType.GENERAL_CUTTER:
            return GeneralCutter()
        elif tool_type == choices.ToolType.SOLID_BORING_CUTTER:
            return SolidBoringCutter()
        elif tool_type == choices.ToolType.GROOVING_EXTERNAL_CUTTER:
            return GroovingExternalCutter()
        elif tool_type == choices.ToolType.GROOVING_INTERNAL_CUTTER:
            return GroovingInternalCutter()
        elif tool_type == choices.ToolType.KEY:
            return Key()
        elif tool_type == choices.ToolType.SCREWDRIVER:
            return Screwdriver()
        elif tool_type == choices.ToolType.SHIM:
            return Shim()
        elif tool_type == choices.ToolType.SCREW:
            return Screw()
        elif tool_type == choices.ToolType.FACE_MILL:
            return FaceMill()
        elif tool_type == choices.ToolType.WRENCH:
            return Wrench()
        elif tool_type == choices.ToolType.THREAD_EXTERNAL_CUTTER:
            return ThreadExternalCutter()
        elif tool_type == choices.ToolType.THREAD_INTERNAL_CUTTER:
            return ThreadInternalCutter()
        elif tool_type == choices.ToolType.SOLID_THREAD_CUTTER:
            return SolidThreadCutter()
        elif tool_type == choices.ToolType.SOLID_GROOVING_CUTTER:
            return SolidGroovingCutter()
        else:
            logger.error(f'No product for {product.manufacturer} : {product.tool_type}')
            return Product()
               
    @staticmethod
    def set_attributes_from_json(product: Product, json_object: dict):
        for key, in json_object.items():
            if key in product.__dict__:
                setattr(product, key,)

    def create_from_json(self, json_object):
        try:
            # Construct a general Product object
            general_product = Product()
            general_product.tool_type = json_object.get("tool_type", defaults.DefaultProduct.TOOL_TYPE)

            # Use get_product method to get the specific product type
            specific_product = self.get_product(general_product)
            
            # Set attributes from JSON object
            self.set_attributes_from_json(specific_product, json_object)

            # Return the constructed specific product object
            return specific_product
        except Exception as e:
            print(f"Failed to create product: {e}")
            return None

# constructor is used to write all parameters to the product from the dataframe
class ProductConstructor():
    
    @abstractmethod
    def construct_product(self, product: Product, df: DataFrame):
        return product
    

class Label(models.Model):
    template = models.CharField(max_length=50)
    attributes = models.JSONField()

    def __str__(self):
        res = f'{self.template}: '
        for attribute in self.attributes:
            res = res + f'{attribute}={self.attributes[attribute]}'
        return res

    class Meta:
        verbose_name_plural = 'Labels'
