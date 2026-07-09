"""
Generates PDF reports using ReportLab.
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.utils.enums import ISACategory


def _color_for_category(cat: ISACategory) -> colors.Color:
    mapping = {
        ISACategory.EXCELLENT: colors.HexColor("#22c55e"),
        ISACategory.ACCEPTABLE: colors.HexColor("#eab308"),
        ISACategory.NEEDS_INTERVENTION: colors.HexColor("#f97316"),
        ISACategory.HIGH_RISK: colors.HexColor("#ef4444"),
    }
    return mapping.get(cat, colors.grey)


def generate_report(inspection: dict, isa_result: dict, logo_path: str | None = None) -> bytes:
    """Generate a PDF report byte stream."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []

    if logo_path:
        try:
            img = Image(logo_path, width=120*mm, height=30*mm)
            elements.append(img)
        except Exception:
            pass

    elements.append(Paragraph("MSBD-360 — Building Health Assessment", styles["Title"]))
    elements.append(Paragraph(f"Relatório de Inspeção #{inspection['id']}", styles["Heading2"]))
    elements.append(Spacer(1, 6*mm))

    info_data = [
        ["Cliente", inspection["client_name"]],
        ["Endereço", inspection["property_address"]],
        ["Inspetor", inspection["inspector_name"]],
        ["Data", inspection["inspection_date"]],
    ]
    info_table = Table(info_data, colWidths=[100, 300])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6*mm))

    overall = isa_result["overall_score"]
    cat = isa_result["category"]
    cat_color = _color_for_category(cat)
    elements.append(Paragraph(
        f"ISA Geral: <b>{overall}</b> / 100  "
        f'<font color="{cat_color.hexval()}">({cat.value})</font>',
        styles["Heading1"],
    ))
    elements.append(Spacer(1, 6*mm))

    for room in isa_result["rooms"]:
        room_color = _color_for_category(room["category"])
        elements.append(Paragraph(
            f'<font color="{room_color.hexval()}">■</font> '
            f"{room['room_name']} — ISA: {room['overall_score']} "
            f"({room['category'].value})",
            styles["Heading3"],
        ))

        pillar_data = [["Pilar", "Pontuação", "Detalhes"]]
        for pk, pv in room["pillars"].items():
            pillar_data.append([pk.capitalize(), f"{pv['score']:.1f}", pv["details"]])
        ptable = Table(pillar_data, colWidths=[100, 80, 220])
        ptable.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(ptable)
        elements.append(Spacer(1, 4*mm))

    doc.build(elements)
    buf.seek(0)
    return buf.read()
