from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Drawing, Dimension

# Create your views here.
def index(request):
    return render(request, 'measuring/index_content.html')

# Add new template view
def new_template(request):
    return render(request, 'measuring/new_template.html')

# Measure view
def measure(request):
    return render(request, 'measuring/measure.html')

@login_required
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


@login_required
@csrf_exempt  # Keep CSRF exemption for now
def create_or_update_dimension(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            drawing = Drawing.objects.get(id=data["drawing_id"])
            
            dimension, created = Dimension.objects.update_or_create(
                drawing=drawing,
                x=data["x"],
                y=data["y"],
                width=data["width"],
                height=data["height"],
                defaults={
                    "value": data["value"],
                    "min_value": data["min_value"],
                    "max_value": data["max_value"],
                    "is_vertical": data["is_vertical"],
                    "page": data["page"],
                    "type_selection": data["type_selection"]
                }
            )

            return JsonResponse({
                "success": True,
                "dimension_id": dimension.id,
                "message": "Created" if created else "Updated"
            })

        except Drawing.DoesNotExist:
            return JsonResponse({"success": False, "error": "Drawing not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)
