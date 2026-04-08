from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
import os
import uuid

router = APIRouter(prefix="/export", tags=["export"])

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ExportRequest(BaseModel):
    paper: dict

@router.post("/pdf")
async def export_pdf(request: ExportRequest):
    paper = request.paper
    filename = f"{OUTPUT_DIR}/paper_{uuid.uuid4().hex[:8]}.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "PaperTitle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.black
    )
    author_style = ParagraphStyle(
        "Authors",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    abstract_style = ParagraphStyle(
        "Abstract",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=9,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leftIndent=0.5*inch,
        rightIndent=0.5*inch,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=10,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.black
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14,
    )
    keyword_style = ParagraphStyle(
        "Keywords",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=9,
        alignment=TA_LEFT,
        spaceAfter=12,
        leftIndent=0.5*inch,
    )

    story = []

    # Title
    if paper.get("Title"):
        story.append(Paragraph(paper["Title"], title_style))
        story.append(Spacer(1, 6))

    # Authors
    if paper.get("Authors"):
        story.append(Paragraph(paper["Authors"], author_style))
        story.append(Spacer(1, 6))

    # Abstract
    if paper.get("Abstract"):
        story.append(Paragraph(paper["Abstract"], abstract_style))

    # Keywords
    if paper.get("Keywords"):
        story.append(Paragraph(f"<i>Keywords—</i>{paper['Keywords']}", keyword_style))
        story.append(Spacer(1, 12))

    # Main sections
    sections = ["Introduction", "Methodology", "Results", "Conclusion", "Acknowledgment", "References"]

    for section in sections:
        if paper.get(section):
            lines = paper[section].split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                # First line is the heading
                if i == 0 or line.startswith(("I.", "II.", "III.", "IV.", "V.", "ACKNOWLEDGMENT", "REFERENCES")):
                    story.append(Paragraph(line, heading_style))
                else:
                    story.append(Paragraph(line, body_style))

    doc.build(story)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=f"research_paper.pdf"
    )