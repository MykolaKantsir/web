# Next Jobs View - TODO and Implementation Notes

## Completed Features ✓

### Airport-Style Table View
- ✓ Five-column layout: Machine (20%), Job (25%), Material (20%), Quantity (15%), Location (20%)
- ✓ Airport board aesthetic with monospace font and industrial colors
- ✓ Color palette matching current jobs view
  - Deep Koamaru (#1a337e) for row backgrounds
  - Cadet Blue (#5F9EA0) for borders
  - Iron to Kimberly gradient (#505962 to #716F81) for container background
- ✓ Responsive design with media queries for smaller screens

### View Switching
- ✓ Keyboard navigation (Arrow Left/Right) to toggle between card and table views
- ✓ Default view set to table (airport-style)
- ✓ Preserved original card view functionality

### Auto-Scroll Functionality
- ✓ Smooth scrolling (1px per frame at 60 FPS)
- ✓ Pause at top and bottom (3 seconds)
- ✓ Bidirectional scrolling (down then up)
- ✓ Hidden scrollbar for clean appearance
- ✓ Auto-scroll only active in table view

### "No Operation" Warning
- ✓ Red border styling for rows with "No operation" jobs
- ✓ Red gradient background (Deep Koamaru to dark red)
- ✓ Pulsing animation effect
- ✓ JavaScript-based class application for flexibility
- ✓ Data attribute (data-job-name) for dynamic styling

### Integration
- ✓ AJAX polling preserved (120 second intervals)
- ✓ Kiosk scaling for Android/TV devices
- ✓ CSRF token handling
- ✓ Loading and error overlays

## Files Modified/Created

### New Files
1. `monitoring/static/css/next_jobs_table.css` - Complete airport styling (239 lines)
2. `monitoring/templates/monitoring/next_jobs_table.html` - Table structure template

### Modified Files
1. `monitoring/templates/monitoring/next_jobs.html` - Added view containers and CSS link
2. `monitoring/static/js/next_jobs.js` - Complete rewrite with view switching and auto-scroll

## Pending Features / Future Extensions

### Row Checkmark Feature
- [ ] Add checkmark column to table (e.g., 10% width, adjust other columns accordingly)
- [ ] Add checkbox or button for marking jobs as "prepared" or "ready"
- [ ] Visual indication when job is checked (green highlight, checkmark icon)
- [ ] Persist checkmark state (requires backend model field)
- [ ] Sync checkmark state with database via AJAX
- [ ] Clear checkmarks when job changes or completes
- [ ] Optional: Add "checked by" user attribution
- [ ] Optional: Add timestamp for when job was checked

### Potential Enhancements
- [ ] Filter view to show only unchecked jobs
- [ ] Add search/filter functionality for specific machines or jobs
- [ ] Click row to expand with additional job details
- [ ] Add estimated setup time field
- [ ] Color-code rows by material type or priority
- [ ] Add job priority indicators
- [ ] Notification sound when new job appears
- [ ] Export current job list to PDF/Excel

## Technical Notes

### Color Scheme
- Primary background: #1a337e (Deep Koamaru)
- Border accent: #5F9EA0 (Cadet Blue)
- Warning red: #dc3545
- Dark red: #5a1a1a

### Data Attributes
- `data-machine-pk`: Machine primary key
- `data-job-monitor-operation-id`: Operation ID for updates
- `data-job-name`: Job name for conditional styling

### Auto-Scroll Configuration
```javascript
const SCROLL_SPEED = 1;        // pixels per frame
const PAUSE_DURATION = 3000;   // milliseconds
const SCROLL_FPS = 60;         // frames per second
```

### CSS Class Structure
- `.airport-board` - Main container
- `.board-header` - Fixed header row
- `.board-body` - Scrollable content area
- `.board-row` - Individual job row
- `.row-no-operation` - Red warning styling
- `.board-cell` - Individual cell
- `.machine-col`, `.job-col`, etc. - Column widths

## Implementation Guidelines for Checkmark Feature

### Backend (Django)
1. Add `is_prepared` boolean field to Monitor_operation model
2. Create migration for new field
3. Add view endpoint for toggling prepared state (e.g., `/monitoring/toggle-next-job-prepared/`)
4. Update API to accept machine_pk and job_monitor_operation_id
5. Return success/failure status

### Frontend (HTML)
1. Add new column to `.board-header`: `<div class="header-cell checkmark-col">READY</div>`
2. Add corresponding cell to `.board-row` with checkbox or button
3. Adjust column widths (e.g., checkmark: 10%, reduce other columns proportionally)

### Frontend (CSS)
1. Add `.checkmark-col { flex: 0 0 10%; justify-content: center; }`
2. Add styling for checked state: `.board-row.row-checked { background: ...; }`
3. Add checkbox/button styling for large touch targets
4. Add animation for check/uncheck action

### Frontend (JavaScript)
1. Add click event listener to checkmark cells
2. Send AJAX request to toggle prepared state
3. Update UI immediately (optimistic update)
4. Handle success/failure responses
5. Apply/remove `.row-checked` class
6. Update checkmark icon/button state

### Data Flow
```
User clicks checkmark
  → JavaScript captures click
  → AJAX POST to /monitoring/toggle-next-job-prepared/
  → Django updates Monitor_operation.is_prepared
  → Return success response
  → JavaScript updates UI (add/remove class)
  → Visual feedback (animation, color change)
```

## Notes
- View switching preserves all functionality from original implementation
- JavaScript uses IIFE pattern for encapsulation
- No changes needed to Django views or models (except for checkmark feature)
- Compatible with existing AJAX polling system