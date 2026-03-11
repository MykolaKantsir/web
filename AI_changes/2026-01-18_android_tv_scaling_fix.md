# Android TV Scaling Fix - 2026-01-18

## Problem Summary

Next jobs view on Android TV (via Fully Kiosk Browser) was displaying only half the screen with a large gray area at the bottom. Additionally, auto-scroll functionality stopped working after applying the scaling fix.

---

## Device Information

- **Device Model:** TV Stick (SkyworthDigital)
- **Android Version:** 11 (TV) SDK 30
- **Screen Resolution:** 1280×720 px (HD/720p)
- **Browser:** Fully Kiosk Browser 1.57.1
- **Device Pixel Ratio:** 1.33125007152557
- **Reported Screen Dimensions:** 962×541 (before DPR multiplication)

---

## Root Cause Analysis

1. **Viewport meta tag ignored:** Fully Kiosk Browser ignores `<meta name="viewport" content="width=1920">`
2. **Wrong dimension source:** Using `window.innerWidth/innerHeight` gave scaled viewport (1024×576) instead of actual screen
3. **Design mismatch:** Page designed for 1920×1080 but TV is actually 1280×720
4. **CSS viewport units issue:** Using `100vh` referenced incorrect viewport height instead of scaled body height

---

## Solution Implemented

### 1. JavaScript Scaling Fix

**File:** `monitoring/static/js/next_jobs.js`

**Changes:**

```javascript
// Lines 245-246: Changed design dimensions to match TV resolution
const DESIGN_WIDTH = 1280;   // Changed from 1920
const DESIGN_HEIGHT = 720;   // Changed from 1080

// Lines 268-270: Use device pixel ratio with screen dimensions
const dpr = window.devicePixelRatio || 1;
const actualWidth = window.screen.width * dpr;   // Use screen, not viewport
const actualHeight = window.screen.height * dpr; // Use screen, not viewport

// Lines 272-275: Calculate scale
const scaleW = actualWidth / DESIGN_WIDTH;
const scaleH = actualHeight / DESIGN_HEIGHT;
const scale = Math.min(scaleW, scaleH);
```

**Result:** Scale calculation now gives ~1.0 instead of ~0.5

**Math:**
- `962 × 1.33 = 1280px`
- `541 × 1.33 = 720px`
- `1280 / 1280 = 1.0` (perfect fit)

### 2. CSS Height Fix

**File:** `monitoring/static/css/next_jobs_table.css`

**Change (Line 22):**

```css
.airport-board {
  width: 100%;
  height: 100%;  /* Changed from 100vh - use parent height not viewport */
  /* ... */
}
```

**Why:** `100vh` uses viewport height (576px) but we need body height (720px after scaling)

---

## Remaining Issue: Auto-Scroll Not Working

### Status
- ✅ **Desktop browser:** Auto-scroll works perfectly
- ❌ **Android TV:** Auto-scroll not working
- ✅ **Other pages on same device:** Dashboard auto-scroll works fine

### Hypothesis
The CSS transform scaling applied to the body might be interfering with scroll detection. The `.board-body` element's `scrollHeight - clientHeight` calculation may return 0 or near-zero due to the scaling transform.

### Debug Code Added (Temporary)

**File:** `monitoring/static/js/next_jobs.js` (Lines 96-102)

```javascript
function startAutoScroll() {
    stopAutoScroll();

    // Debug: Check if scrolling is possible
    if (boardBody) {
        const scrollHeight = boardBody.scrollHeight;
        const clientHeight = boardBody.clientHeight;
        const maxScroll = scrollHeight - clientHeight;
        console.log(`[AUTO-SCROLL] Starting: scrollHeight=${scrollHeight}, clientHeight=${clientHeight}, maxScroll=${maxScroll}`);
    }

    const intervalDelay = 1000 / SCROLL_FPS;
    autoScrollInterval = setInterval(performScroll, intervalDelay);
}
```

**Next Step:** Check console logs on Android TV to see if `maxScroll` is 0.

---

## Files Modified

### Production Changes
1. **monitoring/static/js/next_jobs.js**
   - Lines 245-246: Set DESIGN_WIDTH=1280, DESIGN_HEIGHT=720
   - Lines 257-282: Cleaned up applyScale() - removed debug overlay
   - Lines 268-270: Use `window.screen * dpr` instead of `window.innerWidth`
   - Lines 96-102: Added auto-scroll debug logging (TEMPORARY)

2. **monitoring/static/css/next_jobs_table.css**
   - Line 22: Changed `height: 100vh` to `height: 100%`

### Documentation Created
3. **monitoring/docs/ANDROID_TV_SETUP.md** (NEW)
   - Complete setup guide for Android TV displays
   - Device detection patterns
   - Fully Kiosk Browser settings
   - Implementation checklist
   - Troubleshooting guide

---

## Test Results

### ✅ Fixed Issues
1. Screen now fills entire display (no gray area)
2. Scale calculation correct: ~1.0003 (essentially perfect)
3. Content renders at correct size
4. No visual distortion

### ❌ Remaining Issues
1. Auto-scroll not working on Android TV
   - Works in desktop browser
   - Works on dashboard page (same device)
   - Likely related to CSS transform scaling

---

## Auto-Scroll Configuration

**Current Settings:**
- **SCROLL_SPEED:** 1px per frame
- **SCROLL_FPS:** 60 frames per second
- **PAUSE_DURATION:** 3000ms (3 seconds at top/bottom)

**How it should work:**
1. Page loads in table view
2. After 3 second pause, scrolls down slowly
3. When reaches bottom, pauses 3 seconds
4. Scrolls back up
5. When reaches top, pauses 3 seconds
6. Repeats indefinitely

**Scroll Detection Logic:**
```javascript
const currentScroll = boardBody.scrollTop;
const maxScroll = boardBody.scrollHeight - boardBody.clientHeight;
```

If `maxScroll <= 0`, there's nothing to scroll (content fits in viewport).

---

## Next Steps / TODO

1. **Check Console Logs:**
   - View `[AUTO-SCROLL] Starting:` log on Android TV
   - Determine if `maxScroll` is 0 or positive

2. **If maxScroll is 0:**
   - Content fits in viewport (no scrolling needed)
   - Options:
     a. Increase row padding/height to force overflow
     b. Adjust DESIGN_HEIGHT to make viewport smaller
     c. Disable auto-scroll if content fits

3. **If maxScroll is positive but scroll still not working:**
   - CSS transform may be preventing scrollTop changes
   - Try alternative scroll methods:
     - `element.scrollBy()` instead of `scrollTop`
     - Apply transform to inner container, not body
     - Use `translate` instead of `scale`

4. **Alternative Approaches:**
   - Apply scaling to `.airport-board` instead of `body`
   - Use CSS `zoom` property instead of `transform: scale()`
   - Implement custom scroll using `transform: translateY()`

5. **Remove Debug Logging:**
   - Once issue identified, remove console.log from startAutoScroll()

---

## Fully Kiosk Browser Recommended Settings

**Web Zoom and Scaling:**
- Enable Zoom: OFF
- Load in Overview Mode: OFF
- Use Wide Viewport: ON
- Initial Scale: 100%
- Set Font Size: 100%
- View in Desktop Mode: ON
- Reset Zoom After Each Page: OFF

---

## Person Tracking Implementation (Completed Earlier)

**Files Modified:**
1. `monitoring/models.py` (Lines 1042-1059)
   - Added JSONField columns: employee_ids, employee_names, employee_django_user_ids

2. `monitoring/views.py` (Lines 1197-1221)
   - Updated update_current_monitor_operation to handle person data

3. `monitoring/templates/monitoring/current_jobs_table.html` (Lines 24-28)
   - Display employee names below machine name

4. `monitoring/static/css/current_jobs_table.css` (Lines 205-211)
   - Styled employee names (light steel blue, 16px)

---

## Session Summary

**Duration:** ~2 hours
**Main Achievement:** Fixed Android TV half-screen issue
**Remaining Work:** Fix auto-scroll functionality

**Key Learning:**
- Fully Kiosk Browser ignores viewport meta tag
- Must use `window.screen.width/height * devicePixelRatio` for accurate dimensions
- Avoid `100vh` in scaled layouts - use `100%` instead

---

## Contact

For continuation tomorrow, refer to:
1. This file for current status
2. `monitoring/docs/ANDROID_TV_SETUP.md` for implementation details
3. Console logs on Android TV for auto-scroll debugging

**Last Updated:** 2026-01-18 20:30
**Status:** Partial solution - display fixed, auto-scroll pending investigation
