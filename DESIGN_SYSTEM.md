# Gaston V1 Design System

This document defines the color palette, typography, and design patterns used throughout the Gaston V1 monitoring application.

## Color Palette

### Primary Colors

#### Deep Blue (Primary Brand)
- **Hex:** `#1a337e`
- **Name:** Deep Koamaru
- **Usage:** Primary headers, navigation backgrounds, status row backgrounds, table headers
- **Examples:** Airport board headers, machine row backgrounds, card headers

#### Light Background
- **Hex:** `#f3f7f9`
- **Name:** Light Blue-Gray
- **Usage:** Page backgrounds, card overlays
- **Examples:** Dashboard background, modal overlays

#### Mid-Tone Gray
- **Hex:** `#bbbfbe`
- **Name:** Taupe-Gray
- **Usage:** Card backgrounds, neutral surfaces
- **Examples:** Machine card bodies in card view

### Accent Colors

#### Cadet Blue (Borders & Accents)
- **Hex:** `#5F9EA0`
- **Usage:** Borders, hover effects, accent lines, focus indicators
- **Examples:** Airport board borders, table borders, hover shadows

#### Gradient Background (Airport Boards)
- **Colors:** `#505962` (Iron) → `#716F81` (Kimberly)
- **Usage:** Full-page background for airport-style views
- **CSS:** `linear-gradient(135deg, #505962 0%, #716F81 100%)`

### Status Colors

#### Success / Active / Running
- **Primary:** `#28a745` (Bootstrap Green)
- **Gradient:** `#2d5a3f` → `#1a337e`
- **Usage:** Active machines, running jobs, successful operations
- **Glow:** `box-shadow: 0 0 10px rgba(40, 167, 69, 0.4);`

#### Warning / Setup / Stopped
- **Primary:** `#FFA500` (Orange)
- **Dark:** `#FF8C00` (Dark Orange)
- **Usage:** Setup operations, stopped machines, pending states
- **Glow:** `box-shadow: 0 0 10px rgba(255, 165, 0, 0.4);`

#### Error / Alarm / Critical
- **Primary:** `#dc3545` (Red)
- **Usage:** Errors, alarms, critical status with pulse animation
- **Glow:** `box-shadow: 0 0 10px rgba(220, 53, 69, 0.5);`
- **Animation:** Pulsing red border (2s ease-in-out infinite)

#### Info / Hold / Paused
- **Primary:** `#007bff` (Bootstrap Blue)
- **Usage:** Feed-hold status, paused operations, informational messages
- **Glow:** `box-shadow: 0 0 10px rgba(0, 123, 255, 0.4);`

#### Amber / Gold (Semi-Automatic)
- **Primary:** `#FFD700` (Gold)
- **Dark:** `#7a6a1a`
- **Usage:** Semi-automatic operations
- **Gradient:** Gold to dark amber

#### Offline / Disabled
- **Gradient:** `#1a1e2e` → `#2a2e3e` (Dark Blue-Gray)
- **Border:** `#3a3a3a`
- **Usage:** Offline machines, disabled states
- **Opacity:** 0.7

### Text Colors

#### Primary Text
- **Hex:** `#1a1a1a`
- **Usage:** Headings, primary labels, high-emphasis text

#### Secondary Text
- **Hex:** `#333`
- **Usage:** Body text, labels, normal content

#### Light Text (High Contrast)
- **Hex:** `#ffffff`
- **Usage:** Text on dark backgrounds, airport board text
- **Enhancement:** Text-shadow for glow effect on status rows

#### Muted Text
- **Hex:** `#666`
- **Usage:** Subtitles, hints, secondary information, descriptive text

#### Placeholder / Disabled Text
- **Hex:** `#999`
- **Usage:** Placeholder text, disabled inputs

## Typography

### Font Families

#### System Font Stack (Default)
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
```
- **Usage:** Forms, planning pages, cards, general UI

#### Monospace (Airport Boards)
```css
font-family: 'Courier New', Courier, monospace;
```
- **Usage:** Airport-style table views for authenticity

### Font Sizes

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| H1 Headers | 24px-28px | 700 | Page titles |
| H2 Section Headers | 18px | 600 | Section titles |
| Machine Name (Large) | 24px | 900 | Prominent machine labels |
| Body Text | 14px-16px | 400 | Normal content |
| Small Text | 11px-13px | 400 | Hints, details |
| Status Badges | 16px-22px | 700 | Status indicators |

### Font Weight Scale
- **400:** Regular body text
- **500:** Medium (labels)
- **600:** Semi-bold (section headers)
- **700:** Bold (badges, emphasis)
- **900:** Black (machine names)

## Design Patterns

### Shadows & Elevation

#### Small Cards
```css
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
```

#### Hover Elevation
```css
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
```

#### Board Rows
```css
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
```

### Glow Effects (Status-based)

```css
/* Green - Active */
box-shadow: 0 0 10px rgba(40, 167, 69, 0.4);

/* Orange - Warning */
box-shadow: 0 0 10px rgba(255, 165, 0, 0.4);

/* Red - Error/Alarm */
box-shadow: 0 0 10px rgba(220, 53, 69, 0.5);

/* Blue - Info */
box-shadow: 0 0 10px rgba(0, 123, 255, 0.4);
```

### Border Radius

| Element | Radius |
|---------|--------|
| Buttons, Cards | 8px-12px |
| Small Elements (badges, inputs) | 4px-6px |

### Spacing Scale

| Size | Value | Usage |
|------|-------|-------|
| XS | 4px | Tight spacing |
| SM | 8px | Compact spacing |
| MD | 12px | Default spacing |
| LG | 16px | Comfortable spacing |
| XL | 20px | Section padding |
| 2XL | 24px | Large section padding |
| 3XL | 32px | Major section breaks |
| 4XL | 40px | Page-level padding |

### Animations

#### Slide-in
```css
animation: slideIn 0.5s ease-out;
```

#### Alarm Pulse
```css
animation: alarmPulse 2s ease-in-out infinite;
```

#### Warning Pulse
```css
animation: warningPulse 2s ease-in-out infinite;
```

#### Hover Transitions
```css
transition: all 0.2s-0.3s ease;
```

## Responsive Breakpoints

| Breakpoint | Width | Usage |
|------------|-------|-------|
| Mobile | < 480px | Phone portrait |
| Tablet | 480px-768px | Tablet portrait |
| Desktop Small | 768px-1024px | Tablet landscape, small desktop |
| Desktop Medium | 1024px-1200px | Standard desktop |
| Desktop Large | 1200px-1600px | Large desktop |
| Full HD | 1600px+ | Large monitors |

## Component Guidelines

### Buttons
- **Primary Action:** `#1a337e` background, white text
- **Secondary Action:** `#5F9EA0` background, white text
- **Danger:** `#dc3545` background, white text
- **Hover:** Slight darkening + elevation increase
- **Border Radius:** 8px
- **Padding:** 12px 16px (mobile: 14px 12px for touch targets)

### Cards
- **Background:** White (`#ffffff`)
- **Border:** 2px solid `#e0e0e0`
- **Border Radius:** 12px
- **Shadow:** `0 2px 8px rgba(0, 0, 0, 0.1)`
- **Hover:** Border color to accent, slight elevation

### Status Badges
- **Border Radius:** 4px
- **Padding:** 4px 8px
- **Font Size:** 11px-16px
- **Font Weight:** 600-700
- **Background:** Color-coded based on status

### Form Inputs
- **Border:** 2px solid `#e0e0e0`
- **Focus Border:** `#5F9EA0` or `#0066cc`
- **Border Radius:** 8px
- **Padding:** 12px 16px
- **Font Size:** 16px (prevents zoom on iOS)
- **Background:** White

## Usage Examples

### Creating a Status Row (Airport Board Style)
```css
.board-row {
  background: linear-gradient(90deg, #2d5a3f 0%, #1a337e 100%);
  border: 2px solid #5F9EA0;
  color: #ffffff;
  font-family: 'Courier New', Courier, monospace;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  padding: 12px 15px;
}
```

### Creating a Planning Page Card
```css
.planning-card {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.planning-card:hover {
  border-color: #5F9EA0;
  box-shadow: 0 4px 12px rgba(95, 158, 160, 0.15);
}
```

### Creating a Status Badge
```css
.badge-active {
  background: #e3f2fd;
  color: #1565c0;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}
```

## Notes for AI-Assisted Development

When creating new pages or components:

1. **Use the primary color palette** - Deep Blue (#1a337e) for headers, Cadet Blue (#5F9EA0) for accents
2. **Status colors should be semantic** - Green for success, Orange for warning, Red for errors, Blue for info
3. **Always use the system font stack** unless creating airport-style boards (use monospace)
4. **Mobile-first approach** - Start with mobile styles, enhance for larger screens
5. **Touch targets** - Minimum 48px height for interactive elements on touch devices
6. **Consistent spacing** - Use the spacing scale (12px, 16px, 20px, 24px)
7. **Shadows for elevation** - Use defined shadow values for consistency
8. **Border radius** - 8-12px for cards/buttons, 4-6px for small elements
9. **Hover effects** - 0.2-0.3s transitions for smooth interactions
10. **Status glows** - Use box-shadow glows with appropriate colors and opacity

## File Locations

- Design System Documentation: `/DESIGN_SYSTEM.md` (this file)
- CSS Files: `/monitoring/static/css/`
- Templates: `/monitoring/templates/monitoring/`
