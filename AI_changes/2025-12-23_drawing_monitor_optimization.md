# Drawing Monitor Optimization - December 23, 2025

## Summary

Implemented client-side drawing preloading and cursor test functionality for the drawing monitor system. Fixed async compatibility issues with Daphne ASGI server.

---

## Changes Made

### 1. Client-Side Drawing Preloading (Bandwidth Optimization)

**Problem**: During morning meetings, cursor updates every 0.1 seconds across ~30 operations. With 20 tablets connected, sending 400KB base64 images each time creates ~80MB/second bandwidth.

**Solution**: Preload all drawings on page load (~12MB once), then WebSocket only sends `operation_id` (~50 bytes).

**Files Modified**:
- `monitoring/views.py` - Added `get_all_drawings()` endpoint
- `monitoring/urls.py` - Added URL pattern `/api/drawing/all/`
- `monitoring/consumers.py` - Removed `drawing_base64` from WebSocket messages
- `monitoring/static/js/drawing_monitor.js` - Added preloading and cache lookup

**Bandwidth Comparison**:
| Scenario | Before | After |
|----------|--------|-------|
| Initial page load | ~0 | ~12MB |
| Per cursor change | 400KB | ~50 bytes |
| 10 changes/sec, 20 tablets | 80MB/sec | 1KB/sec |

---

### 2. Cursor Test Page

**New files**:
- `monitoring/templates/monitoring/cursor_test.html`
- `monitoring/views.py` - Added `cursor_test()` view
- `monitoring/urls.py` - Added `/cursor-test/` URL

**Features**:
- PgUp/PgDown keyboard navigation
- Escape to deactivate cursor
- Click to select operation
- **300ms debounce** - Visual updates are instant, API calls only fire after cursor stays on row for 300ms

---

### 3. Drawing Monitor Display Improvements

**Changes**:
- Removed header with operation name (drawing only)
- Drawing now fills entire screen (`width: 100vw; height: 100vh; object-fit: contain`)
- Maintains aspect ratio while maximizing screen usage

---

### 4. Fixed Daphne/ASGI Async Error

**Problem**: `SynchronousOnlyOperation` error on first page load - database query at module import time in `views.py` line 37.

**Solution**: Changed from module-level initialization to lazy initialization:
- `machines_data` is now initialized on first request, not at import
- Uses double-checked locking pattern for thread safety
- Added lazy cache initialization in `dashboard()` and `mobile_dashboard()` views

---

### 5. Deployment Updates

- Updated GitHub Actions workflow to Python 3.12 (required by `autobahn==25.12.2`)
- Added `STATIC_ROOT` to settings.py for Azure deployment

---

## API Endpoints

### Drawing Monitor
- `GET /monitoring/api/drawing/all/` - Get all drawings for preloading
- `POST /monitoring/api/drawing/set-cursor/` - Set active cursor position
- `GET /monitoring/api/drawing/cursor-status/` - Get current cursor status
- `GET /monitoring/drawing-monitor/` - Drawing display page
- `GET /monitoring/cursor-test/` - Cursor test controller page

### Operation Pool Sync (Already Existed)
- `POST /monitoring/api/sync-operation-pool/` - Sync daily operation pool from Monitor G5

**Request Body**:
```json
{
    "operations": [
        {
            "monitor_operation_id": "OP-001",
            "report_id": "REP-001",
            "part_name": "Part A",
            "quantity": 100
        }
    ]
}
```

**Response**:
```json
{
    "success": true,
    "created": 5,
    "updated": 10,
    "removed_from_pool": 2
}
```

---

## Next Steps (for monitoring script)

1. Call `/monitoring/api/sync-operation-pool/` each morning with the day's operations
2. Use the cursor test page to verify drawing monitor works correctly
3. The drawing monitor tablets will preload all drawings on startup and respond instantly to cursor changes
