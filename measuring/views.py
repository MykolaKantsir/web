import json
import csv
from io import BytesIO
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
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

#@login_required
@csrf_exempt
def check_unfinished_protocols(request):
    drawing_id = request.GET.get("drawing_id")
    if not drawing_id:
        return JsonResponse({"error": "Missing drawing_id"}, status=400)

    try:
        drawing = Drawing.objects.get(id=drawing_id)
    except Drawing.DoesNotExist:
        return JsonResponse({"error": "Drawing not found"}, status=404)

    unfinished_protocols = (
        Protocol.objects
        .filter(drawing=drawing, is_finished=False)
        .prefetch_related("measured_values")
    )

    data = []
    for protocol in unfinished_protocols:
        data.append({
            "id": protocol.id,
            "created_at": protocol.created_at.isoformat() if hasattr(protocol, "created_at") else None,
            "measured_count": protocol.measured_values.count(),
        })

    return JsonResponse({"protocols": data})

#@login_required
@csrf_exempt
def get_protocol_data(request):
    protocol_id = request.GET.get("protocol_id")

    if not protocol_id:
        return JsonResponse({"error": "Missing protocol_id"}, status=400)

    try:
        protocol = Protocol.objects.prefetch_related("measured_values__dimension").get(id=protocol_id)
    except Protocol.DoesNotExist:
        return JsonResponse({"error": "Protocol not found"}, status=404)

    data = {
        "protocol": {
            "id": protocol.id,
            "measured_values": []
        }
    }

    for mv in protocol.measured_values.all():
        data["protocol"]["measured_values"].append({
            "dimension_id": mv.dimension.id,
            "value": float(mv.value),
        })

    return JsonResponse(data)

#@login_required
@csrf_exempt
@require_POST
def finish_protocol(request):
    try:
        data = json.loads(request.body)
        protocol_id = data.get("protocol_id")
        if not protocol_id:
            return JsonResponse({"error": "Missing protocol_id"}, status=400)

        protocol = Protocol.objects.get(id=protocol_id)
        protocol.is_finished = True
        protocol.save()

        return JsonResponse({"success": True})
    except Protocol.DoesNotExist:
        return JsonResponse({"error": "Protocol not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

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
        for dim in drawing.dimensions.all().order_by("id")
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
    try:
        data = json.loads(request.body.decode("utf-8"))
        dimension_id = data.get("dimensionId")
        measured_value = data.get("measuredValue")
        drawing_id = data.get("drawingId")
        protocol_id = data.get("protocolId")
        replace_existing = data.get("replace", False)

        if not (dimension_id and measured_value is not None and drawing_id):
            return JsonResponse({"error": "Missing data"}, status=400)

        dimension = Dimension.objects.get(id=dimension_id)
        drawing = Drawing.objects.get(id=drawing_id)

        if protocol_id:
            protocol = Protocol.objects.get(id=protocol_id)
        else:
            protocol = Protocol.objects.create(drawing=drawing)

        # Check for existing value for this dimension in this protocol
        existing_mv = protocol.measured_values.filter(dimension=dimension).first()

        if existing_mv and not replace_existing:
            return JsonResponse({
                "success": False,
                "duplicate": True,
                "existing_value": existing_mv.value,
                "dimensionId": dimension.id,
                "protocolId": protocol.id
            })

        if existing_mv and replace_existing:
            protocol.measured_values.remove(existing_mv)
            existing_mv.delete()

        # Save new measured value
        measured_value_obj = MeasuredValue.objects.create(
            dimension=dimension,
            value=measured_value,
        )
        protocol.measured_values.add(measured_value_obj)

        return JsonResponse({
            "success": True,
            "protocolId": protocol.id,
            "dimensionId": dimension.id
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

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

# @login_required
@csrf_exempt
def download_protocol(request):
    format_type = request.GET.get("format")
    protocol_ids = request.GET.get("protocol_id")
    drawing_id = request.GET.get("drawing_id")
    latest = request.GET.get("latest") == "true"
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if not format_type or format_type not in ["csv", "json", "pdf", "overlay_pdf"]:
        return JsonResponse({"error": "Invalid or missing format parameter"}, status=400)

    protocols = Protocol.objects.all()

    if protocol_ids:
        try:
            ids = [int(pid) for pid in protocol_ids.split(",") if pid.strip().isdigit()]
            protocols = protocols.filter(id__in=ids)
        except ValueError:
            return JsonResponse({"error": "Invalid protocol_id list"}, status=400)

    elif drawing_id:
        try:
            drawing = Drawing.objects.get(id=drawing_id)
        except Drawing.DoesNotExist:
            return JsonResponse({"error": "Drawing not found"}, status=404)

        protocols = protocols.filter(drawing=drawing)

        if latest:
            protocols = protocols.order_by("-id")[:1]

        if date_from:
            protocols = protocols.filter(drawing__created_at__date__gte=parse_date(date_from))
        if date_to:
            protocols = protocols.filter(drawing__created_at__date__lte=parse_date(date_to))

    else:
        return JsonResponse({"error": "Please provide either protocol_id or drawing_id"}, status=400)

    protocols = protocols.prefetch_related("measured_values__dimension")

    if not protocols.exists():
        return JsonResponse({"error": "No matching protocols found"}, status=404)

    compiled_protocols = []

    for protocol in protocols:
        measured_values = protocol.measured_values.select_related("dimension").all().order_by("dimension__id")
        if not measured_values:
            continue

        protocol_datetime = min(mv.measured_at for mv in measured_values)

        measurements = []
        for idx, mv in enumerate(measured_values, start=1):
            dim = mv.dimension
            measurements.append({
                "dimension_number": idx,
                "nominal_value": dim.value,
                "min_value": dim.min_value,
                "max_value": dim.max_value,
                "measured_value": mv.value
            })

        compiled_protocols.append({
            "protocol_id": protocol.id,
            "drawing": protocol.drawing.filename,
            "protocol_datetime": protocol_datetime.isoformat(),
            "measurements": measurements
        })

    if format_type == "json":
        return JsonResponse({"protocols": compiled_protocols})

    elif format_type == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="protocols.csv"'

        writer = csv.writer(response)
        writer.writerow(["Protocol ID", "Drawing", "Protocol Datetime",
                         "Dimension Number", "Nominal Value", "Min", "Max", "Measured Value"])

        for entry in compiled_protocols:
            for m in entry["measurements"]:
                writer.writerow([
                    entry["protocol_id"],
                    entry["drawing"],
                    entry["protocol_datetime"],
                    m["dimension_number"],
                    m["nominal_value"],
                    m["min_value"],
                    m["max_value"],
                    m["measured_value"]
                ])
        return response

    elif format_type == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        styleN = styles["Normal"]

        for entry in compiled_protocols:
            elements.append(Paragraph(f"<b>Drawing:</b> {entry['drawing']}", styleN))
            elements.append(Paragraph(f"<b>Protocol ID:</b> {entry['protocol_id']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {entry['protocol_datetime']}", styleN))
            elements.append(Spacer(1, 6))

            table_data = [["#", "Nominal", "Min", "Max", "MV"]]
            for m in entry["measurements"]:
                table_data.append([
                    str(m["dimension_number"]),
                    m["nominal_value"],
                    str(m["min_value"]),
                    str(m["max_value"]),
                    str(m["measured_value"])
                ])

            table = Table(table_data, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ]))

            for i in range(1, len(table_data)):
                bg_color = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
                table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), bg_color)]))

            elements.append(table)
            elements.append(Spacer(1, 12))

        doc.build(elements)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf', headers={
            "Content-Disposition": 'attachment; filename="protocols.pdf"'
        })
    
    elif format_type == "overlay_pdf":
        overlay_data = []

        for protocol in protocols:
            measured_values = protocol.measured_values.select_related("dimension").all().order_by("dimension__id")
            if not measured_values:
                continue

            protocol_datetime = min(mv.measured_at for mv in measured_values)
            drawing_base64 = protocol.drawing.drawing_image_base64 or ""

            dimensions = []
            for idx, mv in enumerate(measured_values, start=1):
                dim = mv.dimension
                dimensions.append({
                    "dimension_number": idx,
                    "x": dim.x,
                    "y": dim.y,
                    "width": dim.width,
                    "height": dim.height,
                    "nominal_value": dim.value,
                    "min_value": dim.min_value,
                    "max_value": dim.max_value,
                    "measured_value": mv.value,
                    "is_vertical": dim.is_vertical
                })

            overlay_data.append({
                "protocol_id": protocol.id,
                "drawing": protocol.drawing.filename,
                "drawing_image_base64": drawing_base64,
                "protocol_datetime": protocol_datetime.isoformat(),
                "dimensions": dimensions
            })

        return JsonResponse({"protocols": overlay_data})

# @login_required    
@csrf_exempt
def empty_protocol_form(request):
    drawing_id = request.GET.get("drawing_id")
    numbering = request.GET.get("numbering", "false").lower() == "true"

    if not drawing_id:
        return JsonResponse({"error": "Missing drawing_id"}, status=400)

    try:
        drawing = Drawing.objects.get(id=drawing_id)
    except Drawing.DoesNotExist:
        return JsonResponse({"error": "Drawing not found"}, status=404)

    dimensions = drawing.dimensions.all().order_by("id")

    dimension_data = []
    for index, dim in enumerate(dimensions, start=1):
        item = {
            "x": dim.x,
            "y": dim.y,
            "width": dim.width,
            "height": dim.height,
            "is_vertical": dim.is_vertical,
        }
        if numbering:
            item["dimension_number"] = index
        dimension_data.append(item)

    return JsonResponse({
        "drawing": drawing.filename,
        "drawing_image_base64": drawing.drawing_image_base64 or "",
        "dimensions": dimension_data
    })