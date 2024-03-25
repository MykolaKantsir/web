from django.contrib import admin
from .models import Machine, Job, Cycle, Machine_state, Day_activity_log, Archived_cycle

# ModelAdmin for Cycle with search_fields defined
@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    search_fields = ['id', 'machine__name']  # Adjust these fields based on what makes sense for your model

# ModelAdmin for Machine with autocomplete_fields
@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    autocomplete_fields = ['active_cycle', 'previous_cycle']

# ModelAdmin for Job with autocomplete_fields
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    autocomplete_fields = ['full_cycle']

# Register other models
admin.site.register(Machine_state)
admin.site.register(Day_activity_log)
admin.site.register(Archived_cycle)