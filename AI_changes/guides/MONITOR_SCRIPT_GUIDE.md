# Monitor G5 Script Guide

This document describes how the Monitor G5 Python script works and communicates with the Django web application.

## Overview

The monitoring script (`D:\Projects\Monitor G51`) runs continuously and:
1. Connects to Monitor G5 manufacturing system via REST API
2. Fetches current and next operations for each machine
3. Sends operation data to Django web application
4. Runs every 2 minutes (120 seconds)

## Key Files

| File | Purpose |
|------|---------|
| `update_watcher.py` | Main script - fetches operations and updates Django |
| `operation_client.py` | HTTP client - sends data to Django endpoints |
| `auth_session.py` | Authentication - handles CSRF tokens and sessions |
| `monitor_handler.py` | Monitor G5 API - queries manufacturing data |

## Data Flow

```
Monitor G5 System                    Django Web App
     │                                    │
     │  Query operations                  │
     ├────────────────►                   │
     │                                    │
     │  Operation data                    │
     │◄────────────────                   │
     │                                    │
     │         POST /monitoring/update-current-monitor-operation/
     │────────────────────────────────────────────────────────────►
     │                                    │
     │         POST /monitoring/update-next-monitor-operation/
     │────────────────────────────────────────────────────────────►
     │                                    │
```

## Django Endpoints Called

### 1. Update Current Operation
```
POST /monitoring/update-current-monitor-operation/
```

Called when an operation is currently running on a machine.

**Finds record by:** `machine_pk` + `is_in_progress=True`

**Payload:**
```json
{
    "machine_pk": 5,
    "monitor_operation_id": "1356903283169489935",
    "name": "PART-ABC-123",
    "quantity": 100,
    "currently_made_quantity": 45,
    "is_setup": false,
    "material": "Steel 304",
    "report_number": "REP-001",
    "location": "WIP-A1",
    "priority": 1,
    "planned_start_date": "2025-01-15",
    "planned_finish_date": "2025-01-20",
    "drawing_image_base64": "base64-encoded-pdf..."
}
```

### 2. Update Next Operation
```
POST /monitoring/update-next-monitor-operation/
```

Called for the operation queued to run next.

**Finds record by:** `machine_pk` + `is_in_progress=False` + lowest priority

**Payload:** Same structure as current operation.

## Key Fields Explained

### monitor_operation_id
- Unique ID from Monitor G5 system
- **Changes when a different operation is assigned**
- Used to detect when monitor changes operations

### is_setup
- `true` = Machine is being set up (no production reports yet)
- `false` = Production has started (at least one report exists)

**How it's determined:**
```python
# Query ManufacturingOrderOperationReportings for this operation
if reports_exist:
    is_setup = False  # Production mode
else:
    is_setup = True   # Setup mode
```

### currently_made_quantity
- Number of parts already produced
- Fetched from `ManufacturingOrderOperations.ReportedQuantity`

### priority
- Lower number = higher priority
- Used to determine next operation order

## Monitor G5 API Queries

### Get Active Operation (Status 1 or 4)
```
GET Manufacturing/ManufacturingOrderOperations
?$filter=WorkCenterId eq '{wc_id}' and (Status eq 1 or Status eq 4)
&$select=Id,PartId,PlannedQuantity,ReportedQuantity,...
```

### Get Queued Operations
```
GET Manufacturing/ManufacturingOrderOperations
?$filter=WorkCenterId eq '{wc_id}' and WorkshopOperationStatus eq '0'
&$orderby=Priority
&$select=Id,PartId,PlannedQuantity,...
```

### Check Production Reports (for is_setup)
```
GET Manufacturing/ManufacturingOrderOperationReportings
?$filter=OperationId eq '{operation_id}'
&$orderby=ReportingTimestamp desc
&$top=1
&$select=ReportingTimestamp
```

### Get Part Name
```
GET Inventory/Parts('{part_id}')
?$select=Number
```

### Get Drawing PDF
```
GET Manufacturing/ManufacturingOrderOperations('{operation_id}')/GetRelatedDrawingPdf
```

## Machine Types

### Standalone Machines
- Single machine = single work center
- One current operation, one next operation

### Work Center Groups
- Multiple machines share one work center
- Script distributes operations across machines in the group

## Configuration

### Authentication
```python
LOGIN_DATA = {
    'username': 'monitor_user',
    'password': '...',
    'base_url': 'http://localhost:8000'  # or Azure URL
}
```

### Check Interval
```python
time.sleep(120)  # 2 minutes between checks
```

## Adding Operation Pool Sync (TODO)

To populate the dropdown for manual assignment, the script should call:

```
POST /monitoring/api/sync-operation-pool/
```

**Payload:**
```json
{
    "operations": [
        {
            "monitor_operation_id": "1356903283169489935",
            "part_name": "PART-ABC",
            "report_id": "REP-001",
            "quantity": 100
        },
        ...
    ]
}
```

**When to call:**
- On script startup
- Daily at 7:00 AM

**What to send:**
- All available operations from all work centers
- Both active (Status 1, 4) and queued operations

## Troubleshooting

### Script not updating Django
1. Check authentication - CSRF token may be expired
2. Verify base_url is correct
3. Check Monitor G5 connection

### Operations showing wrong data
1. Verify `monitor_operation_id` is being sent
2. Check if record exists with matching `machine_pk` and `is_in_progress`

### is_setup always true/false
1. Check ManufacturingOrderOperationReportings query
2. Verify operation ID is correct
3. Check if reports exist in Monitor G5

## Related Documentation

- [2025-12-22.md](../implemented/2025-12-22.md) - Manual operation assignment implementation
- [API_AUTHENTICATION.md](../implemented/API_AUTHENTICATION.md) - Authentication details