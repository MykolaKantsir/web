from django.contrib.auth.decorators import login_required
import json
import csv
from django.http import JsonResponse, HttpResponse
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

# @login_required
@csrf_exempt
def download_protocol(request):
    format_type = request.GET.get("format")
    protocol_ids = request.GET.get("protocol_id")
    drawing_id = request.GET.get("drawing_id")
    latest = request.GET.get("latest") == "true"
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    # Validate format
    if not format_type or format_type not in ["csv", "json", "pdf"]:
        return JsonResponse({"error": "Invalid or missing format parameter"}, status=400)

    # Start with all protocols
    protocols = Protocol.objects.all()

    # Filter by protocol_id
    if protocol_ids:
        try:
            ids = [int(pid) for pid in protocol_ids.split(",") if pid.strip().isdigit()]
            protocols = protocols.filter(id__in=ids)
        except ValueError:
            return JsonResponse({"error": "Invalid protocol_id list"}, status=400)

    # Filter by drawing_id (+ optional date or latest)
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

    # Prefetch all needed data
    protocols = protocols.prefetch_related("measured_values__dimension")

    if not protocols.exists():
        return JsonResponse({"error": "No matching protocols found"}, status=404)

    # Step 3: Collect and structure data
    compiled_protocols = []

    for protocol in protocols:
        measured_values = protocol.measured_values.all()

        if not measured_values:
            continue

        protocol_datetime = min(mv.measured_at for mv in measured_values)

        measurements = []
        for mv in measured_values:
            dim = mv.dimension
            measurements.append({
                "dimension_number": "",  # Placeholder
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

    # Step 4: Return as JSON
    if format_type == "json":
        return JsonResponse({"protocols": compiled_protocols})

    # Step 5: Return as CSV
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
    
    # Step 5: Return as PDF
    elif format_type == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        from io import BytesIO
        buffer = BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        styleN = styles["Normal"]
        styleH = styles["Heading2"]

        for entry in compiled_protocols:
            # Drawing name
            elements.append(Paragraph(f"<b>Drawing:</b> {entry['drawing']}", styleN))
            elements.append(Paragraph(f"<b>Protocol ID:</b> {entry['protocol_id']} &nbsp;&nbsp;&nbsp; <b>Date:</b> {entry['protocol_datetime']}", styleN))
            elements.append(Spacer(1, 6))

            # Table data
            table_data = [["#", "Nominal", "Min", "Max", "MV"]]
            for i, m in enumerate(entry["measurements"], 1):
                table_data.append([
                    str(i),
                    m["nominal_value"],
                    str(m["min_value"]),
                    str(m["max_value"]),
                    str(m["measured_value"])
                ])

            # Table style
            table = Table(table_data, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ]))

            # Alternating row background
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