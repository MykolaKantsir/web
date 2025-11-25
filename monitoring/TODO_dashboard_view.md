# Dashboard Airport View - Implementation Notes

## Completed Features ✓

### Airport-Style Table View
- ✓ Two-column layout: Machine (50%) | Status (50%)
- ✓ Airport board aesthetic with monospace font and industrial colors
- ✓ Color palette matching current_jobs and next_jobs views
  - Deep Koamaru (#1a337e) for row backgrounds
  - Cadet Blue (#5F9EA0) for borders
  - Iron to Kimberly gradient (#505962 to #716F81) for container background
- ✓ Large fonts for kiosk readability (machine: 24px, status: 22px)
- ✓ Text-only status badges (no icons)
- ✓ Responsive design with media queries for smaller screens

### Status Color Mapping
All machine statuses are color-coded with distinct gradients:
- **ACTIVE** (green): `linear-gradient(90deg, #2d5a3f 0%, #1a337e 100%)` + green border
- **STOPPED** (orange): `linear-gradient(90deg, #1a337e 0%, #8a4a1a 100%)` + orange border
- **FEED-HOLD** (blue): `linear-gradient(90deg, #1a337e 0%, #2a4a7e 100%)` + blue border
- **ALARM** (red): `linear-gradient(90deg, #1a337e 0%, #5a1a1a 100%)` + red border + pulse animation
- **INTERRUPTED** (gray): `linear-gradient(90deg, #1a1e2e 0%, #2a2e3e 100%)` + gray border
- **SEMI_AUTOMATIC** (amber): `linear-gradient(90deg, #1a337e 0%, #7a6a1a 100%)` + amber border
- **OFFLINE/Unknown** (dark gray): `linear-gradient(90deg, #1a1e2e 0%, #2a2e3e 100%)` + reduced opacity

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

### Real-Time Updates
- ✓ AJAX polling every 2 seconds (preserved from original)
- ✓ Dynamic status class application in JavaScript
- ✓ Both card view and table view updated simultaneously
- ✓ Status text and row styling updated on each poll

## Files Created

### 1. monitoring/templates/monitoring/dashboard_table.html
Airport-style table template with two columns:
```html
<div class="airport-board">
  <div class="board-header">
    <div class="header-cell machine-col">MACHINE</div>
    <div class="header-cell status-col">STATUS</div>
  </div>
  <div class="board-body">
    {% for machine_name in machines %}
    <div class="board-row" data-machine-name="{{ machine_name }}" data-status="">
      <div class="board-cell machine-col">
        <div class="cell-content machine-name">{{ machine_name }}</div>
      </div>
      <div class="board-cell status-col">
        <div class="cell-content">
          <div class="status-badge">
            <span class="status-text">LOADING...</span>
          </div>
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
```

### 2. monitoring/static/css/dashboard_table.css
Complete airport styling (~250 lines) including:
- Airport board container styling
- Header and row layouts
- Status-based row classes (row-active, row-stopped, row-feed-hold, row-alarm, row-interrupted, row-semi-automatic, row-offline)
- Hover effects and animations
- Responsive breakpoints
- Pulse animation for ALARM status

## Files Modified

### 3. monitoring/templates/monitoring/dashboard.html
Added view switching structure:
- `#card-view` div wrapping original card layout (hidden by default)
- `#table-view` div including dashboard_table.html
- Added CSS link for dashboard_table.css
- Added viewport meta tag for kiosk scaling

### 4. monitoring/static/js/dashboard_net.js
Enhanced with IIFE pattern containing:
- View switching state management
- Auto-scroll configuration and functions
- `showCardView()` and `showTableView()` functions
- `handleKeyPress()` for keyboard navigation
- `getStatusClass()` mapping status strings to CSS classes
- `updateTableView()` for real-time table updates
- Integration with existing `updateMachineCards()` function
- Initialization on DOMContentLoaded

## Technical Details

### Data Flow
```
Server (Django) → AJAX poll every 2s → updateMachineCards()
                                              ↓
                     ┌──────────────────────────────────────┐
                     ↓                                      ↓
              Card View Update                    Table View Update
              (update_visual())                   (updateTableView())
                     ↓                                      ↓
              Background colors                  Row classes + status text
```

### Auto-Scroll Configuration
```javascript
const SCROLL_SPEED = 1;        // pixels per frame
const PAUSE_DURATION = 3000;   // milliseconds at top/bottom
const SCROLL_FPS = 60;         // frames per second
```

### Status Mapping Function
```javascript
function getStatusClass(status) {
    const statusUpper = status.toUpperCase().trim();

    if (statusUpper === 'ACTIVE') return 'row-active';
    if (statusUpper === 'STOPPED') return 'row-stopped';
    if (statusUpper === 'FEED-HOLD' || statusUpper === 'FEED_HOLD') return 'row-feed-hold';
    if (statusUpper === 'ALARM') return 'row-alarm';
    if (statusUpper === 'INTERRUPTED') return 'row-interrupted';
    if (statusUpper === 'SEMI_AUTOMATIC' || statusUpper === 'SEMI-AUTOMATIC') return 'row-semi-automatic';

    return 'row-offline';  // Default for unknown statuses
}
```

### CSS Class Structure
- `.airport-board` - Main container with gradient background
- `.board-header` - Fixed header row
- `.board-body` - Scrollable content area with hidden scrollbar
- `.board-row` - Individual machine row (base styling)
- `.row-active`, `.row-stopped`, etc. - Status-specific row styling
- `.board-cell` - Individual cell
- `.machine-col`, `.status-col` - Column width definitions (50% each)
- `.machine-name` - Bold machine name styling
- `.status-badge` - Status text container
- `.status-text` - Status text element

## Keyboard Controls
- **Arrow Right (→)**: Switch from card view to table view
- **Arrow Left (←)**: Switch from table view to card view

## Preserved Functionality
- ✓ Real-time AJAX polling (2-second interval)
- ✓ Card view with all original features
- ✓ Push notification subscription controls (hidden in card view)
- ✓ Background caching architecture in Django views
- ✓ Remaining time visual gradient (card view only)

## Potential Future Enhancements
- [ ] Add click behavior to rows for machine details (when not in kiosk mode)
- [ ] Add third column for active NC program
- [ ] Add fourth column for cycle time
- [ ] Add filter to show only specific statuses
- [ ] Add sound alerts for ALARM status
- [ ] Add timestamp showing last update time

## Notes
- No Django backend changes required
- Uses same IIFE pattern as next_jobs.js for encapsulation
- Compatible with existing push notification system
- Designed for kiosk/TV display (large fonts, auto-scroll, no interaction required)
- Status mapping handles both underscore and hyphen variants (FEED-HOLD, FEED_HOLD)