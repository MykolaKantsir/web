# Plan: Add Template Download (JSON + CSV) to New Template Page

## Context
The measuring app has download functionality (JSON, CSV, PDF) on the **measure page** for exporting protocol results, but the **new_template page** has no download options. The goal is to let users download dimension data (values + coordinates) as JSON and CSV right from the template creation page, via buttons in the existing navigation panel.

## Data Structure

### JSON format
```json
{
  "drawing": "filename.pdf",
  "drawing_id": 1,
  "dimensions": [
    {
      "dimension_number": 1,
      "nominal_value": 25.0,
      "min_value": 24.8,
      "max_value": 25.2,
      "type_selection": 2,
      "x": 100,
      "y": 200,
      "width": 50,
      "height": 30,
      "is_vertical": false,
      "page": 1
    }
  ]
}
```

### CSV format
| Drawing | Dimension Number | Nominal Value | Min | Max | Type | X | Y | Width | Height | Is Vertical | Page |
|---------|-----------------|---------------|-----|-----|------|---|---|-------|--------|-------------|------|

## Files to Modify

### 1. Backend: `measuring/views.py`
- Add new view function `download_template(request)`
- Accept GET param `drawing_id` (required) and `format` (`json` or `csv`)
- Query `Drawing` and its related `Dimension` objects (ordered by id)
- Build data with: dimension_number, value, min_value, max_value, type_selection, x, y, width, height, is_vertical, page
- For JSON: return `JsonResponse` with the structure above
- For CSV: return `HttpResponse` with `text/csv` content type, filename `template_{drawing_filename}.csv`
- Reuse the same pattern as existing `download_protocol()` view

### 2. Backend: `measuring/urls.py`
- Add URL pattern: `path("api/download_template/", views.download_template, name="download_template")`

### 3. Frontend template: `measuring/templates/measuring/new_template.html`
- Add download dropdown (JSON + CSV buttons) to the existing navigation panel section
- Use same dropdown pattern as `measure.html` lines 42-52
- Buttons: `id="download-template-json"` and `id="download-template-csv"`

### 4. Frontend JS: `measuring/static/js/new_template.js` (or a small new handler)
- Add click handlers for the two download buttons
- Read `drawing_id` from the image element's attribute (same as existing code does)
- Trigger download via `window.location.href = /measuring/api/download_template/?drawing_id=${drawingId}&format=json`
- Disable/hide buttons if no drawing has been saved yet (no drawing_id available)

## Implementation Notes
- Follow the existing pattern in `download_protocol()` for CSV writer setup and JSON response
- The `drawing_id` is set on the image element after the first crop (via `sendDrawingData()`), so downloads are only available after at least one dimension is saved
- No new models or migrations needed — this reads existing Drawing + Dimension data

## Verification
1. Create a new template with a few dimensions
2. Click JSON download button → verify file contains all dimensions with coordinates
3. Click CSV download button → verify CSV has correct headers and rows
4. Verify buttons are disabled/hidden before any dimension is saved
5. Open downloaded JSON in a text editor and CSV in a spreadsheet to confirm structure
