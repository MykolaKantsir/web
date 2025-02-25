from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Drawing, Dimension, MeasuredValue, Protocol

# Create your views here.
#@login_required
def index(request):
    return render(request, 'measuring/index_content.html')

# Add new template view
#@login_required
def new_template(request):
    return render(request, 'measuring/new_template.html')

# Measure view
#@login_required
def measure_view(request, drawing_id=None):
    """
    Renders the measurement page. If a drawing_id is provided, the frontend
    will fetch the drawing and its dimensions via JavaScript.
    """
    return render(request, 'measuring/measure.html', {'drawing_id': drawing_id})

# Get drawing data
#@login_required
def get_drawing_data(request, drawing_id):
    """
    API endpoint that returns the drawing and its dimensions as JSON.
    """
    drawing = get_object_or_404(Drawing, id=drawing_id)
    
    # Serialize drawing
    drawing_data = {
        "id": drawing.id,
        "filename": drawing.filename,
        "drawing_image_base64": drawing.drawing_image_base64,
        "flip_angle": drawing.flip_angle,
        "pages_count": drawing.pages_count,
        "url": drawing.url,
        "created_at": drawing.created_at.isoformat(),
        "updated_at": drawing.updated_at.isoformat(),
    }

    # Serialize related dimensions
    dimensions = [
        {
            "id": dim.id,
            "x": dim.x,
            "y": dim.y,
            "width": dim.width,
            "height": dim.height,
            "value": dim.value,
            "min_value": dim.min_value,
            "max_value": dim.max_value,
            "is_vertical": dim.is_vertical,
            "page": dim.page,
            "type_selection": dim.type_selection,
        }
        for dim in drawing.dimensions.all()
    ]

    return JsonResponse({"drawing": drawing_data, "dimensions": dimensions})

#@login_required
@csrf_exempt  # Keep CSRF exemption for now
def create_drawing(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            drawing = Drawing.objects.create(
                filename=data["filename"],
                drawing_image_base64=data["drawing_image_base64"],
                flip_angle=data["flip_angle"],
                pages_count=data["pages_count"],
                url=data["url"]
            )
            return JsonResponse({"success": True, "drawing_id": drawing.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

#@login_required
@csrf_exempt
def save_measurement(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        measured_value = float(data.get("measuredValue", 0))
        dimension_id = data.get("dimensionId")
        drawing_id = data.get("drawingId")
        protocol_id = data.get("protocolId", None)

        if measured_value <= 0 or not dimension_id or not drawing_id:
            return JsonResponse({"success": False, "error": "Invalid input data"}, status=400)

        # Get or create the protocol
        if protocol_id:
            protocol = get_object_or_404(Protocol, id=protocol_id)
        else:
            drawing = get_object_or_404(Drawing, id=drawing_id)
            protocol = Protocol.objects.create(drawing=drawing)

        # Get the dimension
        dimension = get_object_or_404(Dimension, id=dimension_id)

        # Create a new measured value
        measured_value_obj = MeasuredValue.objects.create(
            dimension=dimension,
            value=measured_value,
        )

        # Ensure the measured value is linked to the protocol
        protocol.measured_values.add(measured_value_obj)
        protocol.save()

        return JsonResponse({
            "success": True,
            "protocolId": protocol.id,
            "dimensionId": dimension.id
        })

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

# @login_required
@csrf_exempt  # Keep CSRF exemption for now
def create_or_update_dimension(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            drawing = Drawing.objects.get(id=data["drawing_id"])

            # ✅ Check if the dimension exists (new creation if empty)
            if "dimension_id" in data and data["dimension_id"]:
                # 🔄 Update existing dimension
                dimension = Dimension.objects.get(id=data["dimension_id"], drawing=drawing)
                dimension.value = data["value"]
                dimension.min_value = data["min_value"]
                dimension.max_value = data["max_value"]
                dimension.is_vertical = data["is_vertical"]
                dimension.page = data["page"]
                dimension.type_selection = data["type_selection"]
                dimension.save()
                created = False
            else:
                # 🆕 Create a new dimension
                dimension = Dimension.objects.create(
                    drawing=drawing,
                    x=data["x"],
                    y=data["y"],
                    width=data["width"],
                    height=data["height"],
                    value=data["value"],
                    min_value=data["min_value"],
                    max_value=data["max_value"],
                    is_vertical=data["is_vertical"],
                    page=data["page"],
                    type_selection=data["type_selection"]
                )
                created = True

            return JsonResponse({
                "success": True,
                "dimension_id": dimension.id,
                "message": "Created" if created else "Updated"
            })

        except Drawing.DoesNotExist:
            return JsonResponse({"success": False, "error": "Drawing not found"}, status=404)
        except Dimension.DoesNotExist:
            return JsonResponse({"success": False, "error": "Dimension not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)
