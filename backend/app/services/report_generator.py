import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.utils.enums import ISACategory

BRAND_COLOR = colors.HexColor("#1e293b")
ACCENT_COLOR = colors.HexColor("#334155")
EXCELLENT = colors.HexColor("#22c55e")
ACCEPTABLE = colors.HexColor("#eab308")
NEEDS_INT = colors.HexColor("#f97316")
HIGH_RISK = colors.HexColor("#ef4444")

ROOM_TYPE_LABELS = {
    "bedroom": "Quarto",
    "living_room": "Sala de Estar",
    "kitchen": "Cozinha",
    "bathroom": "Banheiro",
    "office": "Escritório",
    "hallway": "Corredor",
    "basement": "Porão",
    "attic": "Sótão",
    "other": "Outro",
}

PILLAR_LABELS = {
    "thermal": "Condições Térmicas",
    "humidity": "Humidade e Condensação",
    "ventilation": "Ventilação",
    "materials": "Estado dos Materiais",
    "lighting": "Iluminação",
    "visual": "Evidências Visuais",
}

CATEGORY_LABELS = {
    ISACategory.EXCELLENT: "Excelente",
    ISACategory.ACCEPTABLE: "Aceitável",
    ISACategory.NEEDS_INTERVENTION: "Necessita Intervenção",
    ISACategory.HIGH_RISK: "Risco Elevado",
}


def _cat_color(cat):
    mapping = {
        ISACategory.EXCELLENT: EXCELLENT,
        ISACategory.ACCEPTABLE: ACCEPTABLE,
        ISACategory.NEEDS_INTERVENTION: NEEDS_INT,
        ISACategory.HIGH_RISK: HIGH_RISK,
    }
    if isinstance(cat, str):
        return mapping.get(cat, colors.grey)
    return mapping.get(cat, colors.grey)


def _score_bar(score):
    """Return a colored bar based on score percentage."""
    if score >= 80:
        return EXCELLENT
    if score >= 60:
        return ACCEPTABLE
    if score >= 40:
        return NEEDS_INT
    return HIGH_RISK


def _build_header():
    return Table(
        [[Paragraph("<b>MSBD-360</b>", ParagraphStyle("brand", fontSize=22, textColor=colors.white, spaceAfter=0)),
          Paragraph("Building Health Assessment", ParagraphStyle("sub", fontSize=10, textColor=colors.HexColor("#94a3b8"), spaceAfter=0))]],
        colWidths=[200, 300],
    )


def generate_report(inspection: dict, isa_result: dict, logo_path: str | None = None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        leftMargin=2*cm, rightMargin=2*cm,
        title=f"MSBD-360 - Relatório #{inspection['id']}",
        author="MSBD-360",
    )

    styles = {
        "title": ParagraphStyle("Title", fontSize=22, leading=26, spaceAfter=4, textColor=BRAND_COLOR, spaceBefore=0),
        "subtitle": ParagraphStyle("Subtitle", fontSize=11, leading=14, spaceAfter=12, textColor=ACCENT_COLOR, spaceBefore=0),
        "h2": ParagraphStyle("H2", fontSize=14, leading=18, spaceAfter=6, textColor=BRAND_COLOR, spaceBefore=16),
        "h3": ParagraphStyle("H3", fontSize=11, leading=14, spaceAfter=4, textColor=ACCENT_COLOR, spaceBefore=10),
        "body": ParagraphStyle("Body", fontSize=9, leading=12, spaceAfter=4),
        "score": ParagraphStyle("Score", fontSize=32, leading=36, spaceAfter=0, alignment=TA_CENTER),
        "score_label": ParagraphStyle("ScoreLabel", fontSize=9, leading=11, spaceAfter=0, alignment=TA_CENTER, textColor=colors.grey),
        "footer": ParagraphStyle("Footer", fontSize=7, leading=9, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER),
        "pillar_name": ParagraphStyle("PName", fontSize=8, leading=10, textColor=colors.grey),
        "pillar_score": ParagraphStyle("PScore", fontSize=8, leading=10, textColor=BRAND_COLOR, alignment=TA_CENTER),
    }

    elements = []

    # ---- HEADER ----
    header_data = [
        [Paragraph("MSBD-360", ParagraphStyle("hdr", fontSize=26, textColor=BRAND_COLOR, spaceAfter=0)),
         Paragraph(f"Relatório #{inspection['id']}", ParagraphStyle("hdr2", fontSize=11, textColor=ACCENT_COLOR, alignment=TA_RIGHT, spaceAfter=0))],
    ]
    header_tbl = Table(header_data, colWidths=[300, 200])
    header_tbl.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 2, BRAND_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_tbl)
    elements.append(Spacer(1, 0.3*cm))

    # ---- INSPECTION INFO ----
    info_data = [
        ["Cliente:", inspection["client_name"], "Inspetor:", inspection["inspector_name"]],
        ["Endereço:", inspection["property_address"], "Data:", inspection["inspection_date"]],
    ]
    info_tbl = Table(info_data, colWidths=[55, 175, 55, 115])
    info_tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (0, -1), ACCENT_COLOR),
        ("TEXTCOLOR", (2, 0), (2, -1), ACCENT_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(info_tbl)
    elements.append(Spacer(1, 0.5*cm))

    # ---- EXECUTIVE SUMMARY ----
    elements.append(Paragraph("Resumo Executivo", styles["h2"]))
    overall = isa_result["overall_score"]
    cat = isa_result["category"]
    cat_color = _cat_color(cat)
    cat_label = CATEGORY_LABELS.get(cat, cat.value if hasattr(cat, 'value') else str(cat))

    score_table_data = [
        [Paragraph(f"{overall:.0f}", styles["score"]),
         Paragraph("ISA Geral", styles["score_label"]),
         Paragraph(f"{cat_label}", ParagraphStyle("CatLabel", fontSize=14, leading=16, textColor=cat_color, alignment=TA_CENTER, spaceAfter=0)),
         Paragraph("Classificação", ParagraphStyle("ClLabel", fontSize=9, leading=11, textColor=colors.grey, alignment=TA_CENTER))],
    ]
    score_tbl = Table(score_table_data, colWidths=[80, 80, 140, 100])
    score_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (1, 0), 1, colors.HexColor("#e2e8f0")),
        ("BOX", (2, 0), (3, 0), 1, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#f8fafc")),
        ("BACKGROUND", (2, 0), (3, 0), colors.HexColor("#f8fafc")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(score_tbl)
    elements.append(Spacer(1, 0.3*cm))

    rooms_count = len(isa_result["rooms"])
    measured = sum(1 for r in isa_result["rooms"] if r.get("measurements_taken", r.get("overall_score", 0) > 0))
    summary_data = [
        [f"{rooms_count}", "Cômodos Avaliados"],
        [f"{overall:.0f}", "ISA Geral"],
        [f"{cat_label}", "Classificação"],
    ]
    summary_tbl = Table(summary_data, colWidths=[60, 240, 60, 240] if False else [100, 100, 100])
    # simpler: horizontal row
    summary_tbl = Table(
        [[Paragraph(f"<b>{rooms_count}</b>", ParagraphStyle("sm", fontSize=16, textColor=BRAND_COLOR, alignment=TA_CENTER)),
          Paragraph("Cômodos", ParagraphStyle("sm2", fontSize=7, textColor=colors.grey, alignment=TA_CENTER)),
          Paragraph(f"<b>{overall:.0f}</b>", ParagraphStyle("sm3", fontSize=16, textColor=_score_bar(overall), alignment=TA_CENTER)),
          Paragraph("ISA Geral", ParagraphStyle("sm4", fontSize=7, textColor=colors.grey, alignment=TA_CENTER)),
          Paragraph(f"<b>{cat_label}</b>", ParagraphStyle("sm5", fontSize=16, textColor=_score_bar(overall), alignment=TA_CENTER)),
          Paragraph("Classificação", ParagraphStyle("sm6", fontSize=7, textColor=colors.grey, alignment=TA_CENTER))]],
        colWidths=[60, 60, 60, 60, 100, 60],
    )
    summary_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (2, 0), (3, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (4, 0), (5, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_tbl)
    elements.append(Spacer(1, 0.3*cm))

    # ---- ISA BY ROOM TYPE (if available) ----
    if isa_result.get("by_type"):
        elements.append(Paragraph("ISA por Tipo de Cômodo", styles["h2"]))
        type_data = [["Tipo", "ISA Médio", "Classificação", "Cômodos"]]
        for rt, info in isa_result["by_type"].items():
            rt_label = ROOM_TYPE_LABELS.get(rt, rt)
            avg_score = info["average_score"]
            rt_color = _cat_color(info["category"])
            rt_cat_label = CATEGORY_LABELS.get(info["category"], info["category"])
            room_names = ", ".join(r["room_name"] for r in info["rooms"])
            type_data.append([
                Paragraph(f"<b>{rt_label}</b>", styles["body"]),
                Paragraph(f"<b>{avg_score:.0f}</b>", ParagraphStyle("b", fontSize=9, textColor=rt_color)),
                Paragraph(rt_cat_label, styles["body"]),
                Paragraph(room_names, styles["body"]),
            ])
        type_tbl = Table(type_data, colWidths=[100, 60, 100, 140])
        type_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(type_tbl)
        elements.append(Spacer(1, 0.3*cm))

    elements.append(PageBreak())

    # ---- DETAILED ROOM REPORTS ----
    elements.append(Paragraph("Detalhamento por Cômodo", styles["h2"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=BRAND_COLOR, spaceAfter=6))

    for idx, room in enumerate(isa_result["rooms"], 1):
        room_color = _cat_color(room["category"])
        room_cat_label = CATEGORY_LABELS.get(room["category"], room["category"])

        room_header = Table(
            [[Paragraph(f"<b>{idx}. {room['room_name']}</b>", ParagraphStyle("rh", fontSize=12, textColor=colors.white, spaceAfter=0)),
              Paragraph(f"ISA: {room['overall_score']:.0f} — {room_cat_label}", ParagraphStyle("rh2", fontSize=9, textColor=colors.white, spaceAfter=0, alignment=TA_RIGHT))]],
            colWidths=[250, 250],
        )
        room_header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), room_color),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (0, 0), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(room_header)

        # Pillar scores
        pillar_table_data = [["Pilar", "Pontuação", "Barra", "Detalhes"]]
        for pk, pv in room["pillars"].items():
            plabel = PILLAR_LABELS.get(pk, pk.capitalize())
            pscore = pv["score"]
            pcolor = _score_bar(pscore)
            bar_count = max(1, int(pscore / 20))
            bar = "█" * bar_count + "░" * (5 - bar_count)
            pillar_table_data.append([
                Paragraph(f"{plabel}", styles["pillar_name"]),
                Paragraph(f"<b>{pscore:.0f}</b>", styles["pillar_score"]),
                Paragraph(f'<font color="{pcolor.hexval()}">{bar}</font>', ParagraphStyle("bar", fontSize=8, spaceAfter=0)),
                Paragraph(pv["details"], ParagraphStyle("det", fontSize=7, textColor=colors.grey, spaceAfter=0)),
            ])

        ptbl = Table(pillar_table_data, colWidths=[120, 50, 100, 130])
        ptbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), ACCENT_COLOR),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(ptbl)
        elements.append(Spacer(1, 0.3*cm))

    # ---- FOOTER ----
    elements.append(Spacer(1, 1*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=4))
    elements.append(Paragraph(
        f"MSBD-360 — Building Health Assessment  |  Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Documento confidencial",
        styles["footer"],
    ))

    doc.build(elements)
    buf.seek(0)
    return buf.read()
