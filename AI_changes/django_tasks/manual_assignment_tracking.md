# Django Task: Manual Assignment Tracking Endpoint

## Context

The Monitor G5 Python script now tracks reporting progress (quantity updates) for operations that admins manually assign to machines. This document contains the requirements for the Django endpoint needed to support this functionality.

## Related Documentation

- [MONITOR_SCRIPT_GUIDE.md](../guides/MONITOR_SCRIPT_GUIDE.md) - How the Monitor G5 script works
- [MANUAL_OVERRIDE_LOGIC.md](D:\Projects\Monitor G5\update_watcher\docs\MANUAL_OVERRIDE_LOGIC.md) - How manual overrides work
- Script implementation: `D:\Projects\Monitor G5\update_watcher\update_watcher.py` (lines 168-265)
- Script client: `D:\Projects\Monitor G5\update_watcher\operation_client.py` (lines 142-175)

## Problem Statement

When an admin manually overrides and assigns an operation to a machine via the Django planning interface:
- The operation is stored in `MachineOperationAssignment.manual_current_operation` or `manual_next_operation`
- The operation is NOT tracked by Monitor G5's automatic work center assignment
- The script needs to know which operations are manually assigned so it can track their reporting progress

## Required Endpoint

### GET /monitoring/api/manual-assignments/

Returns a list of all manually assigned operations across all machines.

#### Authentication
- Requires authenticated session (same as other monitoring API endpoints)
- Script uses `AuthSession` with CSRF token

#### Request Headers
```http
X-Requested-With: XMLHttpRequest
```

#### Response Format

**Success (200 OK):**
```json
{
    "assignments": [
        {
            "machine_pk": 5,
            "monitor_operation_id": "1372462048115913939",
            "operation_type": "current"
        },
        {
            "machine_pk": 7,
            "monitor_operation_id": "1356903283169489935",
            "operation_type": "next"
        }
    ]
}
```

**Empty result (200 OK):**
```json
{
    "assignments": []
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `machine_pk` | Integer | Primary key of the Machine |
| `monitor_operation_id` | String | Unique operation ID from Monitor G5 system |
| `operation_type` | String | Either `"current"` or `"next"` |

#### Logic

Query `MachineOperationAssignment` model for all machines and return:
- Operations in `manual_current_operation` field (if not null) → `operation_type: "current"`
- Operations in `manual_next_operation` field (if not null) → `operation_type: "next"`

#### Suggested Implementation

```python
# In monitoring/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import MachineOperationAssignment

@require_http_methods(["GET"])
def get_manual_assignments(request):
    """
    Returns list of manually assigned operations for tracking reporting progress.

    The Monitor G5 script calls this endpoint every 2 minutes to get the list of
    operations that admins manually assigned to machines. The script then tracks
    reporting progress (quantity updates) for these operations.

    Response format:
    {
        "assignments": [
            {
                "machine_pk": 5,
                "monitor_operation_id": "1372462048115913939",
                "operation_type": "current"  // or "next"
            }
        ]
    }
    """
    assignments = []

    # Query all MachineOperationAssignment records with manual overrides
    for assignment in MachineOperationAssignment.objects.select_related(
        'machine', 'manual_current_operation', 'manual_next_operation'
    ).all():

        # Check for manual current operation assignment
        if assignment.manual_current_operation:
            assignments.append({
                'machine_pk': assignment.machine.pk,
                'monitor_operation_id': assignment.manual_current_operation.monitor_operation_id,
                'operation_type': 'current'
            })

        # Check for manual next operation assignment
        if assignment.manual_next_operation:
            assignments.append({
                'machine_pk': assignment.machine.pk,
                'monitor_operation_id': assignment.manual_next_operation.monitor_operation_id,
                'operation_type': 'next'
            })

    return JsonResponse({'assignments': assignments})
```

#### URL Routing

Add to `monitoring/urls.py`:

```python
path('api/manual-assignments/', views.get_manual_assignments, name='get_manual_assignments'),
```

## How It Works

### Data Flow

```
Every 2 minutes:

1. Script → Django: GET /monitoring/api/manual-assignments/
   Response: [{machine_pk, monitor_operation_id, operation_type}, ...]

2. For each assignment:
   Script → Monitor G5: Query ManufacturingOrderOperations.ReportedQuantity

3. Compare with last known quantity:
   If changed → Script → Django: POST /monitoring/update-{type}-monitor-operation/
                         Payload: {machine_pk, monitor_operation_id, currently_made_quantity}
```

### Script Behavior

The script (`track_manual_assignments()` function):
1. Calls this endpoint to get list of manual assignments
2. For each assignment, queries Monitor G5 for `ReportedQuantity`
3. Compares with last tracked quantity
4. Sends update to Django **only if quantity changed**
5. Uses existing update endpoints:
   - `POST /monitoring/update-current-monitor-operation/`
   - `POST /monitoring/update-next-monitor-operation/`

### Update Payload

The script sends minimal payloads with only the changed field:

```json
{
    "machine_pk": 5,
    "monitor_operation_id": "1372462048115913939",
    "currently_made_quantity": 45
}
```

**Note:** The script does NOT track `is_setup` for manually assigned operations (per requirements).

## Database Models Reference

### MachineOperationAssignment

Located in `monitoring/models.py`:

```python
class MachineOperationAssignment(models.Model):
    machine = models.OneToOneField(Machine, on_delete=models.CASCADE, related_name='operation_assignment')

    # Manual overrides
    manual_current_operation = models.ForeignKey(Monitor_operation, null=True, blank=True, on_delete=models.SET_NULL, related_name='manual_current_assignments')
    manual_next_operation = models.ForeignKey(Monitor_operation, null=True, blank=True, on_delete=models.SET_NULL, related_name='manual_next_assignments')

    # Other fields...
    manual_current_is_idle = models.BooleanField(default=False)
    manual_next_is_idle = models.BooleanField(default=False)
    saved_monitor_current_op_id = models.CharField(max_length=255, null=True, blank=True)
    saved_monitor_next_op_id = models.CharField(max_length=255, null=True, blank=True)
```

### Monitor_operation

Located in `monitoring/models.py`:

```python
class Monitor_operation(models.Model):
    monitor_operation_id = models.CharField(max_length=255, unique=False)  # From Monitor G5
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='monitor_operations')
    name = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    currently_made_quantity = models.IntegerField(default=0)  # ← Updated by script
    is_setup = models.BooleanField(default=True)
    is_in_progress = models.BooleanField(default=False)
    is_in_pool = models.BooleanField(default=False)  # For manual assignment dropdown
    # ... other fields
```

## Testing

### Test Cases

1. **No manual assignments:**
   - Endpoint should return `{"assignments": []}`
   - Script should continue without errors

2. **Single manual assignment:**
   - Create manual current operation assignment via admin
   - Endpoint should return that assignment
   - Script should track and send quantity updates

3. **Multiple manual assignments:**
   - Create manual assignments on multiple machines
   - Endpoint should return all assignments
   - Script should track each independently

4. **Both current and next assigned:**
   - Manually assign both current and next operations to same machine
   - Endpoint should return 2 entries for that machine
   - Script should track both separately

### Manual Testing Steps

1. **Setup:**
   - Start Monitor G5 script
   - Have some operations available in Monitor G5

2. **Create manual assignment:**
   - Go to `/monitoring/planning/<machine_id>/`
   - Search and select an operation as manual override
   - Save

3. **Verify endpoint:**
   ```bash
   # Should return the manually assigned operation
   curl http://localhost:8000/monitoring/api/manual-assignments/
   ```

4. **Verify tracking:**
   - Report parts in Monitor G5 for that operation
   - Check script logs: Should show "📊 Manual assignment updated: Op XXX → Y parts"
   - Check Django database: `currently_made_quantity` should be updated

5. **Verify change detection:**
   - Report more parts in Monitor G5
   - Check script logs: Should detect and send update only when quantity changes
   - Verify no duplicate updates when quantity hasn't changed

### Expected Log Messages

When the script tracks manual assignments, you should see:

```
INFO: 🔍 Checking 2 manually assigned operations...
INFO: 📊 Starting to track manual assignment: Op 1372462048115913939 (Machine 5)
INFO: ✅ Current operation update successful.
INFO: 📊 Manual assignment updated: Op 1372462048115913939 → 45 parts (was 0)
INFO: �� Manual assignment updated: Op 1372462048115913939 → 80 parts (was 45)
```

## Error Handling

The script is designed to handle errors gracefully:
- If endpoint returns non-200 status → logs warning, continues with other operations
- If Monitor G5 query fails → logs warning, continues with other assignments
- If Django update fails → logs error, continues tracking (will retry next cycle)

## Performance Considerations

- Endpoint is called every 2 minutes (same frequency as normal operation updates)
- Query should be efficient: use `select_related()` to avoid N+1 queries
- Response size is typically small (< 20 assignments in most cases)

## Security Considerations

- Endpoint should require authentication (same as other monitoring API endpoints)
- No sensitive data exposed (only operation IDs and machine PKs)
- Read-only operation (GET request)

## Future Enhancements (Not Implemented Now)

1. **Track `is_setup` for manual assignments:**
   - Would require querying `ManufacturingOrderOperationReportings`
   - Similar to how it's done for normal operations

2. **Cleanup stale quantities:**
   - Remove entries from `manual_operation_quantities` dict for operations no longer manually assigned
   - Would prevent dict from growing indefinitely

3. **Add filtering:**
   - Filter by machine_pk to reduce payload size
   - Only return assignments for active machines

## Questions to Verify Before Implementation

1. **Does the `MachineOperationAssignment` model have the fields mentioned?**
   - `manual_current_operation` (ForeignKey to Monitor_operation)
   - `manual_next_operation` (ForeignKey to Monitor_operation)

2. **Is there an existing endpoint we can reference for authentication pattern?**
   - Example: `/monitoring/api/sync-operation-pool/`

3. **Should the endpoint require special permissions?**
   - Or same as other monitoring endpoints (authenticated users)?

## Implementation Checklist

- [ ] Create `get_manual_assignments()` view in `monitoring/views.py`
- [ ] Add URL route to `monitoring/urls.py`
- [ ] Test with no manual assignments (should return empty list)
- [ ] Test with single manual assignment
- [ ] Test with multiple manual assignments
- [ ] Test with both current and next assigned to same machine
- [ ] Verify script logs show tracking messages
- [ ] Verify database shows updated quantities
- [ ] Test error handling (invalid data, missing fields)

## Contact

If you need clarification or have questions about the Monitor G5 script side:
- Script location: `D:\Projects\Monitor G5\update_watcher\update_watcher.py`
- Implementation: Lines 168-265 (`track_manual_assignments()` function)
- Client method: `operation_client.py` lines 142-175 (`get_manual_assignments()`)
