# Android TV Display Setup Guide

## Device Information

**Device Model:** TV Stick (SkyworthDigital)
**Android Version:** 11 (TV) (SDK 30)
**Screen Resolution:** 1280×720 px (HD/720p)
**Browser:** Fully Kiosk Browser 1.57.1
**Device Pixel Ratio:** 1.33125007152557

---

## Problem Summary

When displaying Django web pages on Android TV via Fully Kiosk Browser, the page would only show half the screen (scale 0.5), leaving a large gray area at the bottom.

### Root Cause

1. **Viewport meta tag ignored:** Fully Kiosk Browser ignores `<meta name="viewport" content="width=1920">`
2. **Incorrect dimension source:** Using `window.innerWidth/innerHeight` gave scaled viewport dimensions (1024×576) instead of actual screen size
3. **Wrong design target:** Page was designed for 1920×1080 (Full HD) but TV is actually 1280×720 (HD)
4. **CSS viewport units:** Using `100vh` referenced the incorrect viewport height instead of scaled body height

---

## Solution Implementation

### 1. JavaScript Scaling Function

**File:** `monitoring/static/js/next_jobs.js` (lines 244-398)

**Key Changes:**

```javascript
function scaleForKioskLayout() {
    // Design dimensions match actual TV resolution
    const DESIGN_WIDTH = 1280;   // Changed from 1920
    const DESIGN_HEIGHT = 720;   // Changed from 1080

    const isKioskDevice = /Android|SmartTV|TV|AFTT|AFTM/i.test(navigator.userAgent);

    if (isKioskDevice) {
        // Use device pixel ratio to get actual screen dimensions
        const dpr = window.devicePixelRatio || 1;
        const actualWidth = window.screen.width * dpr;   // Use screen, not viewport
        const actualHeight = window.screen.height * dpr; // Use screen, not viewport

        // Calculate scale
        const scaleW = actualWidth / DESIGN_WIDTH;
        const scaleH = actualHeight / DESIGN_HEIGHT;
        const scale = Math.min(scaleW, scaleH);

        // Apply CSS transform
        body.style.transformOrigin = "top left";
        body.style.transform = `scale(${scale})`;
        body.style.width = DESIGN_WIDTH + "px";
        body.style.height = DESIGN_HEIGHT + "px";
        body.style.overflow = "hidden";
    }
}
```

**Why This Works:**

- **Device Pixel Ratio:** Multiplies `window.screen.width/height` by DPR to get true physical pixels
  - `962 × 1.33 = 1280px`
  - `541 × 1.33 = 720px`
- **Screen vs Viewport:** `window.screen` gives OS-level dimensions, not browser viewport
- **Matching Design:** Setting DESIGN_WIDTH/HEIGHT to 1280×720 results in scale ≈ 1.0

### 2. CSS Height Fix

**File:** `monitoring/static/css/next_jobs_table.css` (line 22)

**Change:**
```css
.airport-board {
  width: 100%;
  height: 100%;  /* Changed from 100vh */
  /* ... */
}
```

**Why:** `100vh` uses viewport height (576px), but we need parent (body) height (720px)

---

## Fully Kiosk Browser Settings

### Recommended Settings

Navigate to: **Settings → Web Zoom and Scaling**

| Setting | Value | Reason |
|---------|-------|--------|
| **Enable Zoom** | OFF | Prevent manual zoom interfering with scaling |
| **Load in Overview Mode** | OFF | Prevent automatic downscaling |
| **Use Wide Viewport** | ON | Support HTML viewport metatag |
| **Initial Scale** | 100% | Default scaling |
| **Set Font Size** | 100% | Default font size |
| **View in Desktop Mode** | ON | Force desktop rendering (not mobile) |
| **Reset Zoom After Each Page** | OFF | Maintain consistent state |

### Kiosk Mode Settings

For production deployment, configure:
- **Kiosk Mode:** ON
- **Start URL:** `http://[server-ip]:8000/monitoring/next-jobs/`
- **Motion Detection:** OFF
- **Screen Brightness:** 102 (or as needed)

---

## Implementation Checklist

When adding a new page for Android TV display:

### 1. HTML Template
```html
<meta name="viewport" content="width=1920, initial-scale=1, maximum-scale=1, user-scalable=no">
```
Keep this meta tag (even though ignored), as it helps with desktop browsers.

### 2. JavaScript (add to page's JS file)

```javascript
function scaleForKioskLayout() {
    const DESIGN_WIDTH = 1280;
    const DESIGN_HEIGHT = 720;

    const isKioskDevice = /Android|SmartTV|TV|AFTT|AFTM/i.test(navigator.userAgent);

    if (!isKioskDevice) {
        return;
    }

    function applyScale() {
        const body = document.body;

        // Reset transform first
        body.style.transform = 'none';
        body.style.width = '';
        body.style.height = '';
        void body.offsetHeight; // Force reflow

        // Calculate with device pixel ratio
        const dpr = window.devicePixelRatio || 1;
        const actualWidth = window.screen.width * dpr;
        const actualHeight = window.screen.height * dpr;

        const scaleW = actualWidth / DESIGN_WIDTH;
        const scaleH = actualHeight / DESIGN_HEIGHT;
        const scale = Math.min(scaleW, scaleH);

        // Apply transform
        body.style.transformOrigin = "top left";
        body.style.transform = `scale(${scale})`;
        body.style.width = DESIGN_WIDTH + "px";
        body.style.height = DESIGN_HEIGHT + "px";
        body.style.overflow = "hidden";
    }

    // Apply multiple times at different delays for reliability
    function applyScaleMultiple() {
        setTimeout(applyScale, 100);
        setTimeout(applyScale, 500);
        setTimeout(applyScale, 1000);
    }

    window.addEventListener("resize", applyScale);
    document.addEventListener("DOMContentLoaded", applyScaleMultiple);
    applyScaleMultiple(); // Immediate attempt
}

// Initialize
scaleForKioskLayout();
```

### 3. CSS Considerations

**Important:** Avoid using viewport units (`vh`, `vw`) for main containers!

❌ **Don't use:**
```css
.main-container {
  height: 100vh;  /* Will use incorrect viewport height */
}
```

✅ **Use instead:**
```css
.main-container {
  height: 100%;  /* Uses parent (body) height */
}

/* Ensure parents have height */
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}
```

### 4. Design Dimensions

Design your page layout for **1280×720 pixels** when targeting this Android TV device.

**Grid layouts example:**
- 5 columns × 2 rows = 10 cards (as in next_jobs)
- Each card: ~256px wide × ~360px tall (accounting for gaps)

---

## Testing Checklist

Before deploying to production:

1. ✅ Test initial page load - should fill entire screen
2. ✅ Test automatic reload (every 2 minutes) - should remain full screen
3. ✅ Test manual reload - should remain full screen
4. ✅ Check browser console for any errors
5. ✅ Verify scale calculation in console: `scale ≈ 1.0`
6. ✅ Test auto-scroll functionality (if applicable)
7. ✅ Test on desktop browser (should still work normally)

---

## Troubleshooting

### Problem: Page shows only half screen

**Check:**
1. Console shows scale < 1.0
2. Verify `DESIGN_WIDTH/HEIGHT` match screen resolution
3. Ensure using `window.screen.width * dpr`, not `window.innerWidth`

### Problem: Gray area at bottom

**Check:**
1. Main container using `100vh` instead of `100%`
2. Parent elements have `height: 100%` set
3. Body dimensions set correctly in JS

### Problem: Scale not applying on reload

**Check:**
1. Multiple application attempts (100ms, 500ms, 1000ms delays)
2. Cache cleared in Fully Kiosk Browser
3. Django server restarted after JS changes

### Problem: Content looks blurry

**Check:**
1. Scale should be close to 1.0 (not 0.5 or 0.667)
2. Device pixel ratio being used correctly
3. CSS transform `scale()` rendering quality

---

## Device Detection Regex

The following user agent patterns trigger Android TV mode:

```javascript
const isKioskDevice = /Android|SmartTV|TV|AFTT|AFTM/i.test(navigator.userAgent);
```

**Matches:**
- `Android` - Generic Android devices
- `SmartTV` - Smart TV browsers
- `TV` - TV devices (includes "TV Stick")
- `AFTT` - Amazon Fire Tablet
- `AFTM` - Amazon Fire TV Stick

**Current Device User Agent:**
```
Mozilla/5.0 (Linux; Android 11; TV Stick Build/RTT0.210...
```

---

## Files Modified

| File | Changes | Purpose |
|------|---------|---------|
| `monitoring/static/js/next_jobs.js` | Lines 245-246, 357-367 | Set design dimensions to 1280×720, use screen with DPR |
| `monitoring/static/css/next_jobs_table.css` | Line 22 | Changed `100vh` to `100%` |

---

## Additional Notes

- **Other screen resolutions:** If deploying to different TV resolutions (e.g., 1920×1080), update `DESIGN_WIDTH/HEIGHT` accordingly
- **Multiple displays:** Consider detecting actual screen resolution and adjusting dynamically
- **Future improvement:** Could make design dimensions configurable via Django settings
- **Browser compatibility:** This solution is specific to Fully Kiosk Browser on Android TV; regular browsers will bypass the scaling

---

## Contact & Support

For issues or questions about Android TV display setup, refer to this document or check:
- Fully Kiosk Browser documentation
- Browser console logs (scale calculation)
- Django server logs

**Last Updated:** 2026-01-18
**Tested With:** Fully Kiosk Browser 1.57.1 on Android 11 TV Stick (1280×720)
