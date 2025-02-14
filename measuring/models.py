from django.db import models

class Drawing(models.Model):
    filename = models.CharField(max_length=255)  # Name of the drawing file

    def __str__(self):
        return self.filename


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
    type_selection = models.IntegerField(choices=[(1, "Shaft"), (2, "Bilateral"), (3, "Hole")], default=1)  # Type of dimension

    def __str__(self):
        return f"Dimension {self.id} for {self.drawing.filename}"
