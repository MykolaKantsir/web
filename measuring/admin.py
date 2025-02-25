from django.contrib import admin
from .models import Dimension, Drawing, Protocol, MeasuredValue


# Register other models
admin.site.register(Dimension)
admin.site.register(Drawing)
admin.site.register(Protocol)
admin.site.register(MeasuredValue)