from django.contrib import admin
from .models import MaterialToBeMachined, EndMill, ChamferMill, BallMill, FaceMill, ThreadMill
from .models import RadiusMill, LollipopMill, TSlotMill, CircularSaw, MillingBody
from .models import Drill, Reamer, SpotDrill, Tap, CenterDrill
from .models import GeneralCutter, BoringCutter, GroovingExternalCutter
from .models import GroovingInternalCutter, SolidGroovingCutter, SolidBoringCutter
from .models import ThreadExternalCutter, ThreadInternalCutter, SolidThreadCutter
from .models import MillingInsert, DrillingInsert, TurningInsert, ThreadInsert, GroovingInsert
from .models import EquipmentMilling, EquipmentTurning, MeasuringEquipment, MillingHolder
from .models import Collet, Workholding, Shim, Screw, PostMachining
from .models import Screwdriver, Key, Wrench
from .models import Order, WeekOrders, Comment, ProductToBeAdded

# Register your models here.


# class MaterialToBeMachinedAdmin(admin.ModelAdmin):
#     model = MaterialToBeMachined
#     list_display = ('name', 'colour', 'group')

admin.site.register(MaterialToBeMachined)
admin.site.register(EndMill)
admin.site.register(ChamferMill)
admin.site.register(BallMill)
admin.site.register(FaceMill)
admin.site.register(ThreadMill)
admin.site.register(RadiusMill)
admin.site.register(LollipopMill)
admin.site.register(TSlotMill)
admin.site.register(CircularSaw)
admin.site.register(MillingBody)
admin.site.register(Drill)
admin.site.register(Reamer)
admin.site.register(SpotDrill)
admin.site.register(CenterDrill)
admin.site.register(Tap)
admin.site.register(GeneralCutter)
admin.site.register(BoringCutter)
admin.site.register(GroovingExternalCutter)
admin.site.register(GroovingInternalCutter)
admin.site.register(SolidGroovingCutter)
admin.site.register(SolidBoringCutter)
admin.site.register(ThreadExternalCutter)
admin.site.register(ThreadInternalCutter)
admin.site.register(SolidThreadCutter)
admin.site.register(MillingInsert)
admin.site.register(DrillingInsert)
admin.site.register(TurningInsert)
admin.site.register(ThreadInsert)
admin.site.register(GroovingInsert)
admin.site.register(EquipmentMilling)
admin.site.register(EquipmentTurning)
admin.site.register(MeasuringEquipment)
admin.site.register(MillingHolder)
admin.site.register(Collet)
admin.site.register(Workholding)
admin.site.register(Shim)
admin.site.register(Screw)
admin.site.register(PostMachining)
admin.site.register(Screwdriver)
admin.site.register(Key)
admin.site.register(Wrench)
admin.site.register(Comment)
admin.site.register(ProductToBeAdded)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_date', 'content_type', 'quantity', 'status')  # Adjust fields as needed
    search_fields = ['id']  # Define searchable fields

@admin.register(WeekOrders)
class WeekOrdersAdmin(admin.ModelAdmin):
    autocomplete_fields = ['orders']
