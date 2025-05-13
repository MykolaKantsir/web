from django.db import models
from django.utils import timezone

class Drawing(models.Model):
    filename = models.CharField(max_length=255)  # Name of the drawing file
    drawing_image_base64 = models.TextField(blank=True, null=True)  # Base64-encoded image of the drawing
    flip_angle = models.FloatField(default=0)  # Angle of the drawing, use if the orientation is vertical
    pages_count = models.IntegerField(default=1)  # Number of pages in the drawingS
    url = models.URLField(blank=True, null=True)  # URL of the drawing
    created_at = models.DateTimeField(default=timezone.now)  # Date and time of creation
    updated_at = models.DateTimeField(auto_now=True)  # Date and time of last update

    def __str__(self):
        return self.filename

class Page(models.Model):
    drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE, related_name="pages")
    page_number = models.IntegerField()  # Page number of the drawing
    page_image_base64 = models.TextField(blank=True, null=True)  # Base64-encoded image of the page

    def __str__(self):
        return f"Page {self.page_number} for {self.drawing.filename}"

class MonittorInformation(models.Model):
    drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE, related_name="monitor_informations")
    path = models.CharField(max_length=255)  # Path of the drawing file
    # Monitor operation number and monitor order number are used to have 
    # an additional option to get the drawing file, it can be any
    # order or operatio that use this drawing file
    monitor_operation_number = models.IntegerField(blank=True, null=True)  # Monitor operation number
    monitor_order_number = models.IntegerField(blank=True, null=True)  # Monitor order number

class Dimension(models.Model):
    drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE, related_name="dimensions")
    x = models.FloatField()  # X coordinate of cropped area
    y = models.FloatField()  # Y coordinate of cropped area
    width = models.FloatField()  # Width of the cropped area
    height = models.FloatField()  # Height of the cropped area
    value = models.CharField(max_length=50, blank=True, null=True)  # OCR-recognized value
    min_value = models.FloatField(blank=True, null=True)  # Minimum tolerance value
    max_value = models.FloatField(blank=True, null=True)  # Maximum tolerance value
    is_vertical = models.BooleanField(default=False)  # Whether the dimension is vertical
    page = models.IntegerField(default=1)  # Page number of the dimension
    type_selection = models.IntegerField(choices=[(1, "Shaft"), (2, "Bilateral"), (3, "Hole")], default=1)  # Type of dimension

    def __str__(self):
        return f"{self.value} for {self.drawing.filename}"
    
class DrawingView(models.Model):
    drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE, related_name="views")
    x = models.FloatField()  # X coordinate of cropped area
    y = models.FloatField()  # Y coordinate of cropped area
    width = models.FloatField()  # Width of the cropped area
    height = models.FloatField()  # Height of the cropped area
    view_number = models.IntegerField()  # View number of the drawing

    def __str__(self):
        return f"View {self.view_number} for {self.drawing.filename}"

class MeasuredValue(models.Model):
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE, related_name="measured_values")
    value = models.FloatField()  # Measured value
    measured_at = models.DateTimeField(default=timezone.now)  # Date and time of measurement

    def __str__(self):
        return f"{self.value} for {self.dimension.value}"

class Protocol(models.Model):
    drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE, related_name="protocols")
    measured_values = models.ManyToManyField(MeasuredValue, related_name="protocols")  # Measured values
    monitor_operaion_number = models.IntegerField(blank=True, null=True)  # Monitor operation number
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f"Protocol for {self.drawing.filename}"
