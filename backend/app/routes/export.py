import os
import uuid
import re

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.platypus import (
    Paragraph, FrameBreak, NextPageTemplate, PageTemplate, Frame,
    Image as RLImage, Spacer
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus.doctemplate import BaseDocTemplate

router = APIRouter(prefix="/export", tags=["export"])

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# The directory where upload.py saves the images
UPLOAD_DIR = "uploads" 

SECTION_ORDER = [
    "Title", "Authors", "Abstract", "Keywords",
    "Introduction", "Methodology", "Results",
    "Conclusion", "Acknowledgment", "References"
]

class ExportRequest(BaseModel):
    paper: dict

# ── Custom IEEE Layout ────────────────────────────────────────────────────────
class IEEEDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        page_w, page_h = A4
        lm = rm = 19 * mm
        tm = bm = 25 * mm
        col_gap = 6 * mm
        col_w = (page_w - lm - rm - col_gap) / 2

        # Top Frame for Title/Authors ONLY (approx 1.5 inches tall)
        title_h = 40 * mm
        title_frame = Frame(lm, page_h - tm - title_h, page_w - lm - rm, title_h, id="title", showBoundary=0)
        
        # Bottom Frames for the rest of Page 1 (Two Columns)
        col_h_1 = page_h - tm - bm - title_h
        left_frame_1 = Frame(lm, bm, col_w, col_h_1, id="left1", showBoundary=0)
        right_frame_1 = Frame(lm + col_w + col_gap, bm, col_w, col_h_1, id="right1", showBoundary=0)

        # Full Height Frames for Page 2 onwards (Two Columns)
        col_h_full = page_h - tm - bm
        left_frame = Frame(lm, bm, col_w, col_h_full, id="left", showBoundary=0)
        right_frame = Frame(lm + col_w + col_gap, bm, col_w, col_h_full, id="right", showBoundary=0)

        # Register the two page layouts
        self.addPageTemplates([
            PageTemplate(id="FirstPage", frames=[title_frame, left_frame_1, right_frame_1]),
            PageTemplate(id="LaterPages", frames=[left_frame, right_frame]),
        ])


@router.post("/pdf")
async def export_pdf(request: ExportRequest):
    paper = request.paper
    filename = f"{OUTPUT_DIR}/paper_{uuid.uuid4().hex[:8]}.pdf"

    doc = IEEEDocTemplate(filename, pagesize=A4, rightMargin=19*mm, leftMargin=19*mm, topMargin=25*mm, bottomMargin=25*mm)
    S = getSampleStyleSheet()

    def style(name, parent="Normal", **kw):
        return ParagraphStyle(name, parent=S[parent], **kw)

    # Strict IEEE Styles
    ts = style("Title",    fontName="Times-Roman", fontSize=22, alignment=TA_CENTER, spaceAfter=8,  leading=24)
    au = style("Author",   fontName="Times-Roman", fontSize=11, alignment=TA_CENTER, spaceAfter=15, leading=13)
    ab = style("Abstract", fontName="Times-Bold",  fontSize=9,  alignment=TA_JUSTIFY, spaceAfter=8, leading=11)
    kw = style("Keywords", fontName="Times-Bold",  fontSize=9,  alignment=TA_JUSTIFY, spaceAfter=15, leading=11)
    h1 = style("H1",       fontName="Times-Roman", fontSize=10, alignment=TA_CENTER, spaceBefore=12, spaceAfter=6, leading=12)
    h2 = style("H2",       fontName="Times-Italic",fontSize=10, alignment=TA_LEFT,   spaceBefore=6,  spaceAfter=4, leading=12)
    bd = style("Body",     fontName="Times-Roman", fontSize=10, alignment=TA_JUSTIFY, spaceAfter=0,  leading=12)
    rf = style("Ref",      fontName="Times-Roman", fontSize=8,  alignment=TA_JUSTIFY, spaceAfter=3,  leading=10, leftIndent=18, firstLineIndent=-18)
    fg = style("Figure",   fontName="Times-Roman", fontSize=8,  alignment=TA_CENTER, spaceBefore=6,  spaceAfter=12, textColor=colors.darkblue)

    story = []
    
    # Force Page 2+ to use the full-height columns
    story.append(NextPageTemplate("LaterPages"))

    # --- 1. FULL WIDTH TITLE BLOCK ---
    if paper.get("Title"):
        story.append(Paragraph(paper["Title"], ts))
    if paper.get("Authors"):
        story.append(Paragraph(paper["Authors"], au))

    # Force the flow out of the Title Block and into the Left Column
    story.append(FrameBreak())

    # --- 2. TWO-COLUMN CONTENT ---
    if paper.get("Abstract"):
        txt = paper["Abstract"] if paper["Abstract"].startswith("Abstract") else f"Abstract—{paper['Abstract']}"
        story.append(Paragraph(txt, ab))
        
    if paper.get("Keywords"):
        txt = paper["Keywords"] if paper["Keywords"].startswith("Index Terms") else f"Index Terms—{paper['Keywords']}"
        story.append(Paragraph(txt, kw))

    for section in SECTION_ORDER:
        if section in ("Title", "Authors", "Abstract", "Keywords"):
            continue
        if not paper.get(section):
            continue
            
        for i, raw in enumerate(paper[section].split("\n")):
            line = raw.strip()
            if not line:
                continue
            
            # --- NEW: Image Placeholder Logic ---
            img_match = re.search(r'\[IMAGE:\s*(.+?)\]', line, flags=re.IGNORECASE)
            if img_match:
                img_filename = img_match.group(1).strip()
                img_path = os.path.join(UPLOAD_DIR, img_filename)
                
                # Check if image exists on the server
                if os.path.exists(img_path):
                    # 3 inches wide perfectly fits the IEEE column width
                    story.append(RLImage(img_path, width=3*inch, height=2*inch, kind='proportional'))
                    story.append(Spacer(1, 6))
                else:
                    story.append(Paragraph(f"<i>[Missing Image: {img_filename}]</i>", fg))
                
                # Strip the tag from the text line
                line = re.sub(r'\[IMAGE:\s*(.+?)\]', '', line, flags=re.IGNORECASE).strip()
                if not line:
                    continue # Move to next line if there's no text left
            # ------------------------------------
            
            if line.startswith("Fig.") or line.startswith("[Fig.") or line.startswith("Table"):
                story.append(Paragraph(line, fg))
            elif (i == 0 or any(line.startswith(p) for p in
                    ("I.", "II.", "III.", "IV.", "V.", "VI.", "ACKNOWLEDGMENT", "REFERENCES"))):
                story.append(Paragraph(line.upper(), h1))
            elif len(line) > 2 and line[1] == "." and line[0].isupper():
                story.append(Paragraph(line, h2))
            elif line.startswith("["):
                story.append(Paragraph(line, rf))
            else:
                story.append(Paragraph(line, bd))

    doc.build(story)
    return FileResponse(filename, media_type="application/pdf", filename="research_paper_ieee.pdf")