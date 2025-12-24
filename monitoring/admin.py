from django.contrib import admin
from .models import Machine, Job, Cycle, Machine_state, Day_activity_log, Archived_cycle
from .models import Monitor_operation, PushSubscription, MachineSubscription, MachineOperationAssignment

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
admin.site.register(Monitor_operation)
admin.site.register(PushSubscription)
admin.site.register(MachineSubscription)


@admin.register(MachineOperationAssignment)
class MachineOperationAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'machine',
        'manual_current_operation',
        'manual_current_is_idle',
        'manual_next_operation',
        'manual_next_is_idle',
        'manual_override_at',
    ]
    search_fields = ['machine__name']
    raw_id_fields = [
        'manual_current_operation',
        'manual_next_operation',
    ]
    readonly_fields = [
        'saved_monitor_current_op_id',
        'saved_monitor_next_op_id',
        'manual_override_at',
    ]