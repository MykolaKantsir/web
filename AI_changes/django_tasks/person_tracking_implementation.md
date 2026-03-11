# Person Tracking Implementation Guide for Django Backend

## Overview

This document outlines the required changes to Django models and views to support person (employee) tracking functionality integrated with the Monitor G5 update watcher script.

The update watcher script now sends person data with operation updates, allowing the Django backend to track which employees are working on which operations.

---

## 1. Data Flow

```
Monitor G5 SQL Database (ActiveWorkRecordingInformation)
    ↓
update_watcher.py (database_handler.py queries database)
    ↓
Person data processed (display names with deduplication)
    ↓
Payload sent to Django: {employee_ids, employee_names, employee_django_user_ids}
    ↓
Django Backend (models & views need updates)
    ↓
Display in Web UI
```

---

## 2. Current Payload Format

The update watcher script sends the following payload to Django endpoints:

### Endpoints:
- `POST /monitoring/update-current-monitor-operation/`
- `POST /monitoring/update-next-monitor-operation/`

### Example Payload (with person data):

```json
{
  "machine_pk": 5,
  "monitor_operation_id": "1372462048115913939",
  "name": "PART-123",
  "quantity": 100,
  "currently_made_quantity": 55,
  "material": "Steel",
  "report_number": "R-456",
  "location": "Warehouse A",
  "priority": 1,
  "is_setup": false,
  "drawing_image_base64": "data:image/png;base64,...",

  // NEW FIELDS - Person tracking data
  "employee_ids": ["1200609522843616835", "661018612037422389"],
  "employee_names": ["Marian", "Andriy Z"],
  "employee_django_user_ids": [5, 12]
}
```

### Field Descriptions:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `employee_ids` | List[str] or null | Monitor G5 Employee IDs from Person table | `["1200609522843616835"]` |
| `employee_names` | List[str] or null | Display names with deduplication applied | `["Marian"]`, `["Andriy Z", "Andriy T"]` |
| `employee_django_user_ids` | List[int] or null | Django User IDs from mapping file | `[5, 12]` or `[None, None]` |

**Important Notes:**
- All three fields are **lists** to support multiple employees per operation
- All three fields can be **null** if no employees are assigned
- `employee_django_user_ids` can contain `null` values for unmapped employees
- Display names use deduplication: "Andriy Z", "Andriy T" (last initial), or "Andriy Le" (first 2 letters if collision)

---

## 3. Model Changes Required

### File: `D:\Projects\Gaston Web\web\monitoring\models.py`

#### 3.1. Add Person Tracking Fields to `Monitor_operation` Model

**Location:** Around line 1027 (Monitor_operation class)

**Add these fields after existing fields:**

```python
class Monitor_operation(models.Model):
    # ... existing fields ...

    # Person tracking fields (added for employee assignment tracking)
    employee_ids = models.JSONField(
        blank=True,
        null=True,
        help_text="List of Monitor G5 Employee IDs working on this operation"
    )
    employee_names = models.JSONField(
        blank=True,
        null=True,
        help_text="List of deduplicated display names (e.g., ['Andriy Z', 'Fredrik F'])"
    )
    employee_django_user_ids = models.JSONField(
        blank=True,
        null=True,
        help_text="List of Django User IDs mapped from Monitor Employee IDs"
    )
```

**Why JSONField?**
- Supports lists natively (no serialization/deserialization needed)
- Supports null values within lists
- Efficient querying with PostgreSQL (if you migrate in future)
- Easy to work with in templates and REST APIs

**Alternative (TextField with JSON serialization):**
If you prefer TextField for compatibility:

```python
employee_ids = models.TextField(
    blank=True,
    null=True,
    help_text="JSON list of Monitor G5 Employee IDs"
)
employee_names = models.TextField(
    blank=True,
    null=True,
    help_text="JSON list of deduplicated display names"
)
employee_django_user_ids = models.TextField(
    blank=True,
    null=True,
    help_text="JSON list of Django User IDs"
)
```

With this approach, you'd need to serialize/deserialize in views:
```python
import json
monitor_operation.employee_ids = json.dumps(employee_ids_list)
# Later:
employee_ids_list = json.loads(monitor_operation.employee_ids) if monitor_operation.employee_ids else []
```

**Recommendation:** Use `JSONField` for cleaner code and better Django integration.

---

## 4. View Changes Required

### File: `D:\Projects\Gaston Web\web\monitoring\views.py`

#### 4.1. Update `update_current_monitor_operation` View

**Location:** Around line 1153

**Modify the `allowed_fields` list and add person field handling:**

```python
def update_current_monitor_operation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        machine_pk = data.get('machine_pk')
        monitor_operation_id = data.get('monitor_operation_id')

        if not machine_pk:
            return JsonResponse({'error': 'Machine PK is required'}, status=400)

        # Try to find operation by monitor_operation_id first
        if monitor_operation_id:
            monitor_operation = Monitor_operation.objects.filter(
                monitor_operation_id=monitor_operation_id
            ).first()
        else:
            monitor_operation = Monitor_operation.objects.filter(
                machine_id=machine_pk,
                is_in_progress=True
            ).first()

        if not monitor_operation:
            return JsonResponse({'error': 'Monitor operation not found'}, status=404)

        # List of allowed fields to update
        allowed_fields = [
            'monitor_operation_id',
            'name',
            'quantity',
            'material',
            'report_number',
            'planned_start_date',
            'planned_finish_date',
            'location',
            'priority',
            'drawing_image_base64',
            'is_setup',
            'currently_made_quantity',
            # NEW: Person tracking fields
            'employee_ids',
            'employee_names',
            'employee_django_user_ids',
        ]

        integer_fields = ['quantity', 'priority', 'currently_made_quantity']
        date_fields = ['planned_start_date', 'planned_finish_date']
        boolean_fields = ['is_setup']
        # NEW: JSON/list fields
        list_fields = ['employee_ids', 'employee_names', 'employee_django_user_ids']

        # Update only allowed fields
        for field in allowed_fields:
            if field in data:
                value = data[field]

                # Handle integer fields
                if field in integer_fields and value is not None:
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        return JsonResponse({'error': f'Invalid value for {field}'}, status=400)

                # Handle date fields
                elif field in date_fields and value:
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        return JsonResponse({'error': f'Invalid date format for {field}'}, status=400)

                # Handle boolean fields
                elif field in boolean_fields:
                    if isinstance(value, str):
                        value = value.lower() in ['true', '1', 'yes']
                    else:
                        value = bool(value)

                # NEW: Handle list fields (already in correct format from JSON)
                elif field in list_fields:
                    # Value can be None or a list
                    # If using JSONField, no conversion needed
                    # If using TextField, uncomment below:
                    # if value is not None:
                    #     value = json.dumps(value)
                    pass

                setattr(monitor_operation, field, value)

        monitor_operation.save()
        return JsonResponse({'status': 'success', 'message': 'Operation updated successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)
```

#### 4.2. Update `update_next_monitor_operation` View

**Location:** Around line 1079

Apply the **exact same changes** as above to the `update_next_monitor_operation` view:

```python
def update_next_monitor_operation(request):
    # ... same implementation as update_current_monitor_operation ...
    # Just change is_in_progress=False instead of True

    # Add the same allowed_fields, list_fields, and handling logic
```

---

## 5. Database Migration

After updating the model, create and run a migration:

```bash
# Navigate to your Django project directory
cd "D:\Projects\Gaston Web\web"

# Create migration
python manage.py makemigrations monitoring

# Review the migration file
# It should show adding three new JSONField columns

# Apply migration
python manage.py migrate monitoring
```

**Expected Migration Output:**

```python
# monitoring/migrations/XXXX_add_person_tracking.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('monitoring', 'PREVIOUS_MIGRATION'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitor_operation',
            name='employee_ids',
            field=models.JSONField(blank=True, null=True,
                help_text='List of Monitor G5 Employee IDs working on this operation'),
        ),
        migrations.AddField(
            model_name='monitor_operation',
            name='employee_names',
            field=models.JSONField(blank=True, null=True,
                help_text="List of deduplicated display names (e.g., ['Andriy Z', 'Fredrik F'])"),
        ),
        migrations.AddField(
            model_name='monitor_operation',
            name='employee_django_user_ids',
            field=models.JSONField(blank=True, null=True,
                help_text='List of Django User IDs mapped from Monitor Employee IDs'),
        ),
    ]
```

---

## 6. Display in Django Admin (Optional but Recommended)

### File: `D:\Projects\Gaston Web\web\monitoring\admin.py`

**Add custom display for person fields:**

```python
from django.contrib import admin
from .models import Monitor_operation

@admin.register(Monitor_operation)
class MonitorOperationAdmin(admin.ModelAdmin):
    list_display = [
        'machine',
        'name',
        'is_in_progress',
        'get_employees',  # NEW
        'currently_made_quantity',
        'quantity'
    ]

    # NEW: Custom method to display employee names
    def get_employees(self, obj):
        if obj.employee_names:
            return ', '.join(obj.employee_names)
        return 'No employees'

    get_employees.short_description = 'Employees'

    # Show person fields in detail view
    fieldsets = (
        ('Operation Details', {
            'fields': ('monitor_operation_id', 'name', 'quantity', 'material', 'report_number')
        }),
        ('Person Tracking', {
            'fields': ('employee_ids', 'employee_names', 'employee_django_user_ids'),
            'classes': ('collapse',),  # Collapsible section
        }),
        # ... other fieldsets ...
    )
```

---

## 7. Frontend Display (Template Example)

### File: `D:\Projects\Gaston Web\web\monitoring\templates\monitoring\machine_detail.html`

**Display employee names in operation card:**

```html
<div class="operation-card">
    <h3>{{ operation.name }}</h3>
    <p>Status: {{ operation.is_in_progress|yesno:"Current,Next" }}</p>
    <p>Progress: {{ operation.currently_made_quantity }} / {{ operation.quantity }}</p>

    <!-- NEW: Display employees -->
    {% if operation.employee_names %}
        <p class="employees">
            <strong>Employees:</strong>
            {% for name in operation.employee_names %}
                <span class="badge badge-primary">{{ name }}</span>
            {% endfor %}
        </p>
    {% else %}
        <p class="employees text-muted">No employees assigned</p>
    {% endif %}
</div>
```

---

## 8. Testing the Implementation

### 8.1. Manual Test via Django Shell

```python
python manage.py shell

from monitoring.models import Monitor_operation, Machine

# Get a test machine
machine = Machine.objects.get(pk=5)

# Get or create an operation
operation, created = Monitor_operation.objects.get_or_create(
    machine=machine,
    monitor_operation_id="TEST_OP_123",
    defaults={
        'name': 'Test Operation',
        'quantity': 100,
    }
)

# Set person data
operation.employee_ids = ["1200609522843616835", "661018612037422389"]
operation.employee_names = ["Marian", "Andriy Z"]
operation.employee_django_user_ids = [5, None]  # Second person not mapped
operation.save()

# Verify
print(operation.employee_names)  # Should print: ['Marian', 'Andriy Z']
print(operation.employee_django_user_ids)  # Should print: [5, None]
```

### 8.2. Test with update_watcher.py

1. Ensure employee_django_mapping.json has mappings:
```json
{
  "1200609522843616835": 5,
  "661018612037422389": 12
}
```

2. Run the update_watcher script
3. Check Django admin to see person data populated
4. Check logs for successful updates

### 8.3. Test Payload via curl

```bash
curl -X POST http://localhost:8000/monitoring/update-current-monitor-operation/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -d '{
    "machine_pk": 5,
    "monitor_operation_id": "1372462048115913939",
    "name": "Test Part",
    "quantity": 100,
    "currently_made_quantity": 55,
    "is_setup": false,
    "employee_ids": ["1200609522843616835"],
    "employee_names": ["Marian"],
    "employee_django_user_ids": [5]
  }'
```

Expected response:
```json
{
  "status": "success",
  "message": "Operation updated successfully"
}
```

---

## 9. Error Handling

### 9.1. Handle Missing Person Data

The script sends `null` for all person fields when no employees are assigned:

```json
{
  "employee_ids": null,
  "employee_names": null,
  "employee_django_user_ids": null
}
```

**Django handles this automatically** with `blank=True, null=True` on the model fields.

### 9.2. Handle Partial Mappings

Some employees might not have Django user mappings:

```json
{
  "employee_ids": ["123", "456"],
  "employee_names": ["John", "Jane"],
  "employee_django_user_ids": [5, null]
}
```

This is valid and should be stored as-is. You can filter in templates:

```html
{% for user_id in operation.employee_django_user_ids %}
    {% if user_id %}
        <!-- Link to Django user profile -->
        <a href="/admin/auth/user/{{ user_id }}/">{{ operation.employee_names|index:forloop.counter0 }}</a>
    {% else %}
        <!-- Display name only -->
        <span>{{ operation.employee_names|index:forloop.counter0 }} (unmapped)</span>
    {% endif %}
{% endfor %}
```

---

## 10. Summary Checklist

- [ ] **Models.py**: Add 3 JSONField columns to `Monitor_operation`
- [ ] **Run migration**: `python manage.py makemigrations && python manage.py migrate`
- [ ] **Views.py**: Update `update_current_monitor_operation` to handle person fields
- [ ] **Views.py**: Update `update_next_monitor_operation` to handle person fields
- [ ] **Admin.py**: Add person fields display (optional)
- [ ] **Templates**: Display employee names in UI (optional)
- [ ] **Test**: Verify data flows from update_watcher to Django
- [ ] **Test**: Verify null values are handled correctly
- [ ] **Test**: Verify multiple employees per operation works

---

## 11. Advanced: Linking to Django Users

If you want to link employee names to actual Django User accounts in the UI:

```python
# In your template context or view
from django.contrib.auth.models import User

operation = Monitor_operation.objects.get(pk=operation_pk)

# Build list of User objects where mapping exists
users = []
if operation.employee_django_user_ids:
    for user_id in operation.employee_django_user_ids:
        if user_id:  # Skip None values
            try:
                user = User.objects.get(pk=user_id)
                users.append(user)
            except User.DoesNotExist:
                users.append(None)
        else:
            users.append(None)

# Now you can zip names with User objects
employee_data = zip(operation.employee_names or [], users)
```

Template:
```html
{% for name, user in employee_data %}
    {% if user %}
        <a href="{% url 'user_profile' user.pk %}">{{ name }}</a>
    {% else %}
        <span>{{ name }}</span>
    {% endif %}
{% endfor %}
```

---

## 12. Future Enhancements

### 12.1. Add Person History Tracking

Track when employees start/stop working on operations:

```python
class OperationPersonHistory(models.Model):
    operation = models.ForeignKey(Monitor_operation, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=50)
    employee_name = models.CharField(max_length=100)
    django_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
```

### 12.2. Add Employee Performance Metrics

Track production per employee:

```python
class EmployeeProductionMetrics(models.Model):
    employee_id = models.CharField(max_length=50, unique=True)
    total_operations = models.IntegerField(default=0)
    total_parts_produced = models.IntegerField(default=0)
    average_setup_time = models.DurationField(null=True)
```

---

## Appendix A: Complete Model Definition

```python
class Monitor_operation(models.Model):
    # Existing fields
    monitor_operation_id = models.CharField(max_length=50, default='')
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    currently_made_quantity = models.IntegerField(default=0)
    material = models.CharField(max_length=50)
    report_number = models.CharField(max_length=50)
    planned_start_date = models.DateField(default=date(2024, 1, 1))
    planned_finish_date = models.DateField(default=date(2024, 1, 1))
    location = models.CharField(max_length=50, blank=True, default='')
    machine = models.ForeignKey('Machine', on_delete=models.CASCADE, related_name='monitor_operations', null=True, blank=True)
    priority = models.IntegerField(default=0)
    drawing_image_base64 = models.TextField(blank=True, null=True)
    is_in_progress = models.BooleanField(default=False)
    is_setup = models.BooleanField(default=False)
    is_in_pool = models.BooleanField(default=True)

    # NEW: Person tracking fields
    employee_ids = models.JSONField(
        blank=True,
        null=True,
        help_text="List of Monitor G5 Employee IDs working on this operation"
    )
    employee_names = models.JSONField(
        blank=True,
        null=True,
        help_text="List of deduplicated display names (e.g., ['Andriy Z', 'Fredrik F'])"
    )
    employee_django_user_ids = models.JSONField(
        blank=True,
        null=True,
        help_text="List of Django User IDs mapped from Monitor Employee IDs"
    )

    class Meta:
        verbose_name = "Monitor operation"
        verbose_name_plural = "Monitor operations"

    def __str__(self):
        status = "Current" if self.is_in_progress else "Next"
        employees = ', '.join(self.employee_names) if self.employee_names else 'No employees'
        return f"{self.machine.name} | {status} | {self.name} | {employees}"
```

---

**End of Implementation Guide**
