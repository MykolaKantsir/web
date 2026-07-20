"""Vector overlay generator for measurement drawings.

Reads a source PDF from `PDFs/` and a matching `template data/*.json`, then
writes a new PDF where each dimension area has a thin stroked frame with a
dimension number, plus a small metadata block in the top-left corner. The
original vector content of the source PDF is preserved.

Coordinates in the JSON are expressed in the *rasterized pixel* space produced
by `pdf.js` at `scale: 1.5` (see upload_file.js). They map to PDF points by
dividing by `PDF_JS_SCALE`. pdf.js viewport and PyMuPDF page.rect both use a
top-left origin, so no Y flip is required.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import fitz  # PyMuPDF


PDF_JS_SCALE = 1.5

# Style knobs. These are the "CSS" of the overlay — one place for all visual
# choices so the look can be tweaked without touching the layout code.
ORANGE = (1.0, 0.5, 0.0)  # #FF8000

STYLE = {
    "frame_color": ORANGE,
    "frame_width": 1.8,
    "number_color": ORANGE,
    "number_size": 11,
    "number_fontname": "hebo",  # Helvetica-Bold
    "number_offset_y": 2,       # points above frame top-left
    "meta_color": (0, 0, 0),
    "meta_size": 9,
    "meta_pad": 8,
    "meta_line_gap": 12,
    "meta_bg": (1, 1, 1),
    "meta_bg_opacity": 0.85,
}


def overlay_drawing(src_pdf: Path, template_json: Path, out_pdf: Path) -> None:
    template = json.loads(template_json.read_text(encoding="utf-8"))
    doc = fitz.open(src_pdf)

    try:
        for dim in template["dimensions"]:
            page_idx = dim.get("page", 1) - 1
            if not (0 <= page_idx < len(doc)):
                continue

            page = doc[page_idx]
            x = dim["x"] / PDF_JS_SCALE
            y = dim["y"] / PDF_JS_SCALE
            w = dim["width"] / PDF_JS_SCALE
            h = dim["height"] / PDF_JS_SCALE

            rect = fitz.Rect(x, y, x + w, y + h)
            page.draw_rect(
                rect,
                color=STYLE["frame_color"],
                width=STYLE["frame_width"],
                fill=None,
            )

            num = str(dim["dimension_number"])
            page.insert_text(
                fitz.Point(x, y - STYLE["number_offset_y"]),
                num,
                fontsize=STYLE["number_size"],
                color=STYLE["number_color"],
                fontname=STYLE["number_fontname"],
            )

        _draw_metadata(doc[0], template)
        doc.save(out_pdf, garbage=3, deflate=True)
    finally:
        doc.close()


def _draw_metadata(page: fitz.Page, template: dict) -> None:
    lines = [
        f"Drawing: {template['drawing']}",
        f"Drawing ID: {template['drawing_id']}",
        f"Date: {date.today().isoformat()}",
    ]

    pad = STYLE["meta_pad"]
    size = STYLE["meta_size"]
    gap = STYLE["meta_line_gap"]

    text_width = max(fitz.get_text_length(line, fontname="helv", fontsize=size) for line in lines)
    box = fitz.Rect(pad, pad, pad + text_width + 2 * pad, pad + gap * len(lines) + pad)

    page.draw_rect(
        box,
        color=None,
        fill=STYLE["meta_bg"],
        fill_opacity=STYLE["meta_bg_opacity"],
        width=0,
    )

    y = box.y0 + pad + size
    for line in lines:
        page.insert_text(
            fitz.Point(box.x0 + pad, y),
            line,
            fontsize=size,
            color=STYLE["meta_color"],
            fontname="helv",
        )
        y += gap


def _default_template_json(pdf_path: Path, template_dir: Path) -> Path:
    stem = pdf_path.stem
    candidate = template_dir / f"template_{stem}.json"
    if candidate.exists():
        return candidate
    for p in template_dir.glob(f"template_{stem}*.json"):
        return p
    raise FileNotFoundError(f"No template JSON for {pdf_path.name} in {template_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pdf", type=Path, help="Source PDF (from PDFs/)")
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Template JSON (auto-detected from template_<stem>.json if omitted)",
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=Path(r"D:\Projects\RISE AI project\template data"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output PDF (defaults to overlay_<stem>.pdf next to source)",
    )
    args = parser.parse_args()

    src = args.pdf.resolve()
    tpl = (args.template or _default_template_json(src, args.template_dir)).resolve()
    if args.out:
        out = args.out.resolve()
    else:
        out_dir = src.parent / "overlays"
        out_dir.mkdir(exist_ok=True)
        out = out_dir / f"overlay_{src.stem}.pdf"

    overlay_drawing(src, tpl, out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
