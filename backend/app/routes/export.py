import os
import uuid
import json
import subprocess
import tempfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, FrameBreak,
    NextPageTemplate, PageTemplate, Frame
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus.doctemplate import BaseDocTemplate
from reportlab.lib import colors

router = APIRouter(prefix="/export", tags=["export"])

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Path to the Node.js DOCX generator (place it at backend/generate_ieee_docx.js)
DOCX_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "generate_ieee_docx.js")

SECTION_ORDER = [
    "Title", "Authors", "Abstract", "Keywords",
    "Introduction", "Methodology", "Results",
    "Conclusion", "Acknowledgment", "References"
]


class ExportRequest(BaseModel):
    paper: dict


# ── IEEE PDF Layout ───────────────────────────────────────────────────────────

class IEEEDocTemplate(BaseDocTemplate):
    """A4 with full-width title block, then two-column body."""

    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        page_w, page_h = A4
        lm = rm = 19 * mm
        tm = bm = 25 * mm
        col_gap = 6 * mm
        col_w = (page_w - lm - rm - col_gap) / 2

        title_frame = Frame(lm, bm, page_w - lm - rm, page_h - tm - bm,
                            id="title", showBoundary=0)
        left_frame  = Frame(lm, bm, col_w, page_h - tm - bm,
                            id="left", showBoundary=0)
        right_frame = Frame(lm + col_w + col_gap, bm, col_w, page_h - tm - bm,
                            id="right", showBoundary=0)

        self.addPageTemplates([
            PageTemplate(id="title_page", frames=[title_frame]),
            PageTemplate(id="two_col",    frames=[left_frame, right_frame]),
        ])


@router.post("/pdf")
async def export_pdf(request: ExportRequest):
    paper = request.paper
    filename = f"{OUTPUT_DIR}/paper_{uuid.uuid4().hex[:8]}.pdf"

    doc = IEEEDocTemplate(filename, pagesize=A4,
                          rightMargin=19*mm, leftMargin=19*mm,
                          topMargin=25*mm, bottomMargin=25*mm)

    S = getSampleStyleSheet()

    def style(name, parent="Normal", **kw):
        return ParagraphStyle(name, parent=S[parent], **kw)

    ts = style("Title",    fontName="Times-Bold",       fontSize=16, alignment=TA_CENTER, spaceAfter=5,  leading=20)
    au = style("Author",   fontName="Times-Roman",      fontSize=10, alignment=TA_CENTER, spaceAfter=10, leading=13)
    ab = style("Abstract", fontName="Times-Italic",     fontSize=9,  alignment=TA_JUSTIFY, spaceAfter=7, leading=12, leftIndent=12, rightIndent=12)
    kw = style("Keywords", fontName="Times-Roman",      fontSize=9,  alignment=TA_JUSTIFY, spaceAfter=12, leading=12, leftIndent=12, rightIndent=12)
    h1 = style("H1",       fontName="Times-Bold",       fontSize=10, alignment=TA_CENTER, spaceBefore=10, spaceAfter=4, leading=13)
    h2 = style("H2",       fontName="Times-BoldItalic", fontSize=10, alignment=TA_LEFT,   spaceBefore=6,  spaceAfter=3, leading=13)
    bd = style("Body",     fontName="Times-Roman",      fontSize=10, alignment=TA_JUSTIFY, spaceAfter=5,  leading=13)
    rf = style("Ref",      fontName="Times-Roman",      fontSize=9,  alignment=TA_JUSTIFY, spaceAfter=3,  leading=12, leftIndent=18, firstLineIndent=-18)

    story = []

    # ── Full-width title block ─────────────────────────────────────────────
    if paper.get("Title"):
        story.append(Paragraph(paper["Title"], ts))
    if paper.get("Authors"):
        story.append(Paragraph(paper["Authors"], au))
    if paper.get("Abstract"):
        txt = paper["Abstract"]
        if not txt.startswith("Abstract"):
            txt = "Abstract—" + txt
        story.append(Paragraph(txt, ab))
    if paper.get("Keywords"):
        story.append(Paragraph(f"<b><i>Keywords</i></b>—{paper['Keywords']}", kw))

    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.black, spaceAfter=8))
    story.append(NextPageTemplate("two_col"))
    story.append(FrameBreak())

    # ── Two-column body ────────────────────────────────────────────────────
    for section in SECTION_ORDER:
        if section in ("Title", "Authors", "Abstract", "Keywords"):
            continue
        if not paper.get(section):
            continue
        for i, raw in enumerate(paper[section].split("\n")):
            line = raw.strip()
            if not line:
                continue
            if (i == 0 or any(line.startswith(p) for p in
                    ("I.", "II.", "III.", "IV.", "V.", "VI.",
                     "ACKNOWLEDGMENT", "REFERENCES"))):
                story.append(Paragraph(line, h1))
            elif len(line) > 2 and line[1] == "." and line[0].isupper():
                story.append(Paragraph(line, h2))
            elif line.startswith("["):
                story.append(Paragraph(line, rf))
            else:
                story.append(Paragraph(line, bd))

    doc.build(story)
    return FileResponse(filename, media_type="application/pdf",
                        filename="research_paper_ieee.pdf")


# ── IEEE DOCX Export (via Node.js + docx-js) ─────────────────────────────────

@router.post("/docx")
async def export_docx(request: ExportRequest):
    paper = request.paper

    tmp_json = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    json.dump(paper, tmp_json, ensure_ascii=False)
    tmp_json.close()

    output_path = f"{OUTPUT_DIR}/paper_{uuid.uuid4().hex[:8]}.docx"
    script_path = os.path.abspath(DOCX_SCRIPT)

    if not os.path.exists(script_path):
        raise HTTPException(
            status_code=500,
            detail=f"DOCX generator not found. Expected at: {script_path}"
        )

    result = subprocess.run(
        ["node", script_path, tmp_json.name, output_path],
        capture_output=True, text=True, timeout=30
    )
    os.unlink(tmp_json.name)

    if result.returncode != 0 or not os.path.exists(output_path):
        raise HTTPException(
            status_code=500,
            detail=f"DOCX generation failed: {result.stderr or result.stdout}"
        )

    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="research_paper_ieee.docx"
    )