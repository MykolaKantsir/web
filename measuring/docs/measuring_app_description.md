# Measuring App — Complete Description

## 1. What Is This App?

The Measuring App is a web-based quality control system for industrial drawings. It allows operators to:
1. **Create measurement templates** from technical drawings (PDF or image files)
2. **Perform measurements** against those templates and record results
3. **Export data** in multiple formats (JSON, CSV, PDF) for reporting and archival

The app replaces manual paper-based measurement protocols with a digital workflow that includes automatic tolerance calculation, OCR-based value recognition, and structured data export.

---

## 2. User Perspective

### 2.1 Landing Page (`/measuring/`)

The user sees two options:
- **"Add New Template"** — define measurement points on a drawing
- **"Measure"** — record actual measurements against an existing template

### 2.2 Creating a Template (`/measuring/new_template/`)

**Goal:** Define which dimensions on a drawing need to be measured, along with their nominal values and tolerances.

**Step-by-step flow:**

1. **Upload a drawing** — The user selects a PDF or image file (PNG, JPEG). PDFs are automatically converted to images. The user can rotate the drawing 90 degrees if needed.

2. **Crop a dimension** — Using a crop tool (Cropper.js), the user selects a rectangular area around a dimension value on the drawing. This area defines where the dimension appears visually.

3. **OCR recognition** — The cropped area is automatically sent to Tesseract.js (client-side OCR), which attempts to read the nominal value (e.g., "52", "47.8").

4. **Tolerance calculation** — Based on the recognized value and a selected tolerance level (Coarse / Medium / Fine, following ISO 2768), the app automatically calculates min and max bounds. For example, a value of 52 with Medium tolerance in the 30-120mm range gets min=51.7 and max=52.3.

5. **Manual adjustments** — The user can:
   - Edit the nominal value if OCR was incorrect (press Enter to recalculate tolerances and save)
   - Manually override min/max values (press Enter to save without recalculating)
   - Select a dimension type: Shaft, Bilateral, or Hole

6. **Repeat** — The user crops more dimensions. Each one is immediately saved to the database. The drawing shows red rectangles with numbers marking all previously cropped areas.

7. **Download template data** — At any point after the first dimension is saved, the user can download:
   - **JSON** — structured file with all dimension data and coordinates
   - **CSV** — spreadsheet-compatible table with the same data
   - **Empty Form** — PDF of the drawing with white boxes over each dimension area and numbers (blank form for hand-written measurements)
   - **Overlay PDF** — PDF of the drawing with transparent frames around dimension areas and numbers (original drawing content visible)

**Key behaviors:**
- The drawing is saved to the database on the first crop (as base64, not as a file on disk)
- Each dimension is saved individually as it's created or edited
- Rotation is disabled after the first crop to prevent coordinate misalignment
- Only the most recently uploaded drawing is kept — uploading a new file replaces the previous one

### 2.3 Measuring (`/measuring/measure/` or `/measuring/measure/<drawing_id>/`)

**Goal:** Record actual measured values for each dimension defined in a template, compare against tolerances, and export results.

**Step-by-step flow:**

1. **Select a drawing** — If no drawing_id is in the URL, the user sees a search panel. They can search by filename, URL, or monitor operation/order number. On match, they're redirected to the measurement page for that drawing.

2. **Protocol selection** — If unfinished measurement protocols exist for this drawing, a modal appears listing them with their measured count. The user can continue an existing protocol or start a new one.

3. **Drawing and table load** — The drawing is rendered on a canvas with all dimensions marked (orange rectangles with numbers). A table on the right shows all dimensions with their nominal values, min, max, and an empty "Measured Value" column.

4. **Enter measurements** — The user clicks a dimension (either in the table or directly on the drawing). The input field at the top shows the expected value and tolerance range as a placeholder. The user types the measured value and presses Enter.

5. **Validation and feedback:**
   - The measured value is saved to the current protocol
   - The table cell turns **green** if within tolerance, **red** if outside
   - If a value was already recorded for this dimension in the current protocol, a confirmation dialog asks whether to replace it
   - The next unmeasured dimension is automatically selected

6. **Finish protocol** — Once all dimensions are measured, the "Finish Protocol" button becomes active. Clicking it marks the protocol as complete and shows a "Protocol Finished" banner.

7. **Download results** — At any time, the user can download:
   - **JSON** — all protocol data with measurements
   - **CSV** — flat table with one row per measurement
   - **PDF** — formatted report with tables (generated server-side using ReportLab)
   - **Overlay PDF** — drawing with measured values rendered in dimension boxes
   - **Empty Form** — blank form for printing

---

## 3. Technical Architecture

### 3.1 Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django (Python) |
| Database | PostgreSQL |
| Frontend | HTML/CSS/JavaScript (vanilla), Bootstrap 5 |
| Image cropping | Cropper.js |
| OCR | Tesseract.js (client-side) |
| PDF import | pdf.js (client-side PDF-to-image) |
| PDF export (tables) | ReportLab (server-side) |
| PDF export (overlays) | jsPDF (client-side) |

### 3.2 Data Storage

All drawing images are stored as **base64-encoded strings** in the PostgreSQL database (`TextField`). There is no media file server — no `FileField` or `ImageField` is used. This simplifies deployment but means each drawing adds a large text entry to the database.

### 3.3 Data Models

```
Drawing
  ├── filename (CharField)
  ├── drawing_image_base64 (TextField) — full base64 image
  ├── flip_angle (FloatField)
  ├── pages_count (IntegerField)
  ├── url (URLField, optional)
  ├── created_at, updated_at
  │
  ├── Dimension (many)
  │     ├── x, y, width, height (FloatField) — crop region coordinates
  │     ├── value (CharField) — nominal value from OCR
  │     ├── min_value, max_value (FloatField) — tolerance bounds
  │     ├── is_vertical (BooleanField)
  │     ├── page (IntegerField)
  │     └── type_selection (IntegerField: 1=Shaft, 2=Bilateral, 3=Hole)
  │
  ├── Protocol (many)
  │     ├── is_finished (BooleanField)
  │     ├── monitor_operation_number (IntegerField, optional)
  │     └── measured_values (ManyToMany → MeasuredValue)
  │
  ├── Page (many) — individual pages for multi-page drawings
  ├── DrawingView (many) — defined views/sections
  └── MonitorInformation (many) — links to monitoring system

MeasuredValue
  ├── dimension (ForeignKey → Dimension)
  ├── value (FloatField) — actual measured value
  └── measured_at (DateTimeField)
```

**Key relationships:**
- A Drawing has many Dimensions (the template)
- A Drawing has many Protocols (measurement sessions)
- A Protocol links to many MeasuredValues through M2M
- Each MeasuredValue references the Dimension it measures

### 3.4 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `api/create_drawing/` | POST | Save new drawing (base64 image + metadata) |
| `api/drawing/<id>/` | GET | Fetch drawing + all its dimensions |
| `api/create_or_update_dimension/` | POST | Create or update a dimension |
| `api/find_drawing/` | GET | Search for drawing by filename/URL/monitor number |
| `api/save_measurement/` | POST | Record a measured value in a protocol |
| `api/check_unfinished_protocols/` | GET | List incomplete protocols for a drawing |
| `api/get_protocol_data/` | GET | Fetch all measurements from a protocol |
| `api/finish_protocol/` | POST | Mark protocol as complete |
| `api/download_template/` | GET | Export template dimensions as JSON or CSV |
| `api/download_protocol/` | GET | Export measurement results (JSON/CSV/PDF/overlay) |
| `api/empty_protocol_form/` | GET | Get drawing + dimension coords for empty form PDF |

### 3.5 Frontend Architecture

The frontend is organized as a set of JavaScript manager modules, each responsible for a specific concern. There is no build system or framework — all scripts are loaded directly via `<script>` tags.

**Template creation page — scripts:**

| Module | Responsibility |
|--------|---------------|
| `upload_file.js` | File upload, PDF-to-image conversion, rotation, sessionStorage |
| `cropper_manager.js` | Initializes Cropper.js on the uploaded image |
| `new_template.js` | Orchestrates crop → OCR → save flow |
| `table_manager.js` | Dimension table rows, tolerance calculation (ISO 2768), save to DB |
| `drawing_manager.js` | Red rectangle marking on drawing canvas, preview rendering |
| `text_recognition.js` | Tesseract.js OCR wrapper |
| `django_communicator.js` | All fetch/POST calls to Django API |
| `templateDownloadManager.js` | Download button handlers (JSON/CSV/Empty Form/Overlay PDF) |
| `drawingOverlayRenderer.js` | Client-side PDF generation using jsPDF |

**Measurement page — scripts:**

| Module | Responsibility |
|--------|---------------|
| `measure.js` | Main entry point — initializes all managers in sequence |
| `protocolManager.js` | Checks for unfinished protocols, shows selection modal |
| `measureDrawingManager.js` | Renders drawing on canvas, marks dimensions, click detection |
| `measureTableManager.js` | Populates dimension table, color-codes measured values |
| `measureInputManager.js` | Input field handling, measurement submission, auto-advance |
| `measurePreviewManager.js` | Preview on hover (stub implementation) |
| `navigationPanelManager.js` | Download button handlers for measurement results |
| `drawingOverlayRenderer.js` | Shared PDF generation (same as template page) |
| `django_communicator.js` | Shared API communication (same as template page) |

### 3.6 Data Flow Diagrams

**Template Creation:**
```
User uploads PDF/image
  → upload_file.js converts to base64, stores in sessionStorage
  → cropper_manager.js initializes Cropper.js on the image

User crops a dimension area
  → new_template.js:handleCrop()
    → Tesseract.js OCR reads the cropped region
    → table_manager.js:addRow() creates table row with value + calculated tolerances
    → drawing_manager.js:markCropped() draws red rectangle + number on image
    → (first crop only) django_communicator.js:sendDrawingData() → POST api/create_drawing/
    → (if valid) table_manager.js:saveDimension() → POST api/create_or_update_dimension/

User edits value and presses Enter
  → table_manager.js:handleValueChange() recalculates min/max → saveDimension()

User edits min or max and presses Enter
  → table_manager.js:handleMinMaxChange() → saveDimension() (no recalculation)

User clicks Download → JSON/CSV
  → templateDownloadManager.js → GET api/download_template/?format=json|csv
  → Browser downloads file

User clicks Download → Empty Form / Overlay PDF
  → templateDownloadManager.js → GET api/empty_protocol_form/
  → drawingOverlayRenderer.js renders canvas → jsPDF generates PDF → browser download
```

**Measurement:**
```
User navigates to /measuring/measure/<drawing_id>/
  → measure.js initializes
    → protocolManager.checkAndSelectProtocol() → GET api/check_unfinished_protocols/
      → (if found) shows modal, user selects or creates new
    → django_communicator.getDrawingData() → GET api/drawing/<id>/
    → measureDrawingManager.init() renders drawing + dimension overlays on canvas
    → measureTableManager.populateTable() fills table with dimensions
    → (if protocol selected) getProtocolData() loads existing measurements

User clicks dimension (table row or canvas click)
  → measureInputManager.selectDimension() highlights row, primes input field

User enters value and presses Enter
  → measureInputManager.submitMeasurement()
    → django_communicator.sendMeasurement() → POST api/save_measurement/
    → (if duplicate) confirm dialog → re-submit with replace=true
    → measureTableManager updates cell (green=pass, red=fail)
    → Auto-selects next unmeasured dimension

User clicks Finish Protocol
  → measureInputManager.finishCurrentProtocol()
    → django_communicator.finishProtocol() → POST api/finish_protocol/
    → UI disabled, "Protocol Finished" banner shown

User clicks Download
  → navigationPanelManager → GET api/download_protocol/?format=...
  → JSON/CSV: browser download; PDF: ReportLab server-side; Overlay: jsPDF client-side
```

---

## 4. Tolerance Calculation (ISO 2768)

The app uses the ISO 2768 general tolerance standard with three levels:

| Nominal Range (mm) | Coarse (C) | Medium (M) | Fine (F) |
|--------------------|-----------:|----------:|--------:|
| 0 – 3              | +/- 0.2    | +/- 0.1   | +/- 0.05 |
| 3 – 6              | +/- 0.3    | +/- 0.1   | +/- 0.05 |
| 6 – 30             | +/- 0.5    | +/- 0.2   | +/- 0.1  |
| 30 – 120           | +/- 0.8    | +/- 0.3   | +/- 0.15 |
| 120 – 400          | +/- 1.2    | +/- 0.5   | +/- 0.2  |
| 400 – 1000         | +/- 2.0    | +/- 0.8   | +/- 0.3  |
| 1000 – 2000        | +/- 3.0    | +/- 1.2   | +/- 0.5  |
| 2000 – 4000        | +/- 4.0    | +/- 2.0   | +/- 0.5  |

The tolerance level is selected via radio buttons (C/M/F) in the navigation panel. The selected level applies to all subsequent crops. Users can manually override min/max for individual dimensions.

---

## 5. Export Formats

### 5.1 Template Exports (from New Template page)

**JSON** — structured data with coordinates:
```json
{
  "drawing": "130-M0093-2792-C.pdf",
  "drawing_id": 21,
  "dimensions": [
    {
      "dimension_number": 1,
      "nominal_value": "52",
      "min_value": 51.7,
      "max_value": 52.3,
      "type_selection": 2,
      "x": 217.63, "y": 139.96,
      "width": 54.63, "height": 52.53,
      "is_vertical": false,
      "page": 1
    }
  ]
}
```

**CSV** — flat table:
```
Drawing, Drawing ID, Dimension Number, Nominal Value, Min, Max, Type, X, Y, Width, Height, Is Vertical, Page
```

**Empty Form PDF** — drawing image with white-filled rectangles over dimension areas and dimension numbers outside each box. Meant for printing and hand-writing measurements.

**Overlay PDF** — drawing image with transparent rectangular frames around dimension areas and dimension numbers. Original drawing content remains visible — shows where dimensions are located without hiding the drawing.

### 5.2 Measurement Exports (from Measure page)

**JSON:**
```json
{
  "protocols": [{
    "protocol_id": 1,
    "drawing": "130-M0093-2792-C.pdf",
    "protocol_datetime": "2026-03-10T12:00:00",
    "measurements": [
      {
        "dimension_number": 1,
        "nominal_value": "52",
        "min_value": 51.7,
        "max_value": 52.3,
        "measured_value": 52.05
      }
    ]
  }]
}
```

**CSV:**
```
Protocol ID, Drawing, Protocol Datetime, Dimension Number, Nominal Value, Min, Max, Measured Value
```

**PDF** — formatted report with tables (server-side, ReportLab). One table per protocol with headers, alternating row colors, drawing name and date.

**Overlay PDF** — drawing image with measured values rendered inside white boxes at each dimension location. Includes metadata overlay (drawing name, protocol ID, date) in the top-left corner.

**Empty Form** — same as template version, blank boxes for hand measurement.

---

## 6. File Naming Conventions

All downloaded files include the drawing name (without the original file extension):

| Type | Filename Pattern |
|------|-----------------|
| Template JSON | `template_{drawing_name}.json` |
| Template CSV | `template_{drawing_name}.csv` |
| Empty Form PDF | `empty_form_{drawing_name}.pdf` |
| Overlay PDF | `overlay_{drawing_name}.pdf` |
| Protocol JSON | `protocols.json` |
| Protocol CSV | `protocols.csv` |
| Protocol PDF | `protocols.pdf` |
| Protocol Overlay PDF | `overlay_{drawing_name}.pdf` |

---

## 7. External Libraries

| Library | Version | Purpose | Where Used |
|---------|---------|---------|------------|
| Cropper.js | — | Interactive image cropping | Template creation |
| Tesseract.js | — | Client-side OCR (text recognition) | Template creation |
| pdf.js | — | PDF to image conversion | File upload |
| jsPDF | — | Client-side PDF generation | Empty form + overlay exports |
| ReportLab | — | Server-side PDF generation | Protocol PDF export |
| Bootstrap 5 | — | UI components and layout | All pages |
| jQuery | — | DOM utilities (legacy) | Base template |

---

## 8. Session & State Management

**Browser sessionStorage** (template page only):
- `uploadedImage` — current drawing image (base64, possibly with crop markings)
- `flipAngle` — current rotation angle

**DOM attributes used as state:**
- `#image[drawing-id]` — database ID of current drawing (set after first crop)
- `<tr>[dimension-id]` — database ID of each dimension row
- `<body>[data-drawing-id]` — drawing ID on measurement page
- `<input>[data-protocolId]` — current protocol ID during measurement
- `<input>[data-dimensionId]` — currently selected dimension ID

**No server-side sessions** are used for app state — all state is maintained client-side or derived from database queries.
