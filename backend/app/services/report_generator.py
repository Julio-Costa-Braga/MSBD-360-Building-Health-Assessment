import io
import base64
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
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
    "bedroom": "Quarto", "living_room": "Sala de Estar", "kitchen": "Cozinha",
    "bathroom": "Banheiro", "office": "Escritório", "hallway": "Corredor",
    "basement": "Porão", "attic": "Sótão", "other": "Outro",
}

PILLAR_LABELS = {
    "thermal": "Condições Térmicas", "humidity": "Humidade e Condensação",
    "ventilation": "Ventilação", "materials": "Estado dos Materiais",
    "lighting": "Iluminação", "visual": "Evidências Visuais",
}

CATEGORY_LABELS = {
    ISACategory.EXCELLENT: "Excelente", ISACategory.ACCEPTABLE: "Aceitável",
    ISACategory.NEEDS_INTERVENTION: "Necessita Intervenção", ISACategory.HIGH_RISK: "Risco Elevado",
}

SUB_LOCATION_LABELS = {
    "wall_1": "Parede 1", "wall_2": "Parede 2", "wall_3": "Parede 3",
    "wall_4": "Parede 4", "ceiling": "Teto", "floor": "Chão", "": "Geral",
}


def _cat_color(cat):
    mapping = {
        ISACategory.EXCELLENT: EXCELLENT, ISACategory.ACCEPTABLE: ACCEPTABLE,
        ISACategory.NEEDS_INTERVENTION: NEEDS_INT, ISACategory.HIGH_RISK: HIGH_RISK,
    }
    if isinstance(cat, str):
        return mapping.get(cat, colors.grey)
    return mapping.get(cat, colors.grey)


def _score_bar(score):
    if score >= 80:
        return EXCELLENT
    if score >= 60:
        return ACCEPTABLE
    if score >= 40:
        return NEEDS_INT
    return HIGH_RISK


def _build_room_list_widget(rooms_data: list[dict], isa_result: dict):
    """Build a compact room list for the executive summary."""
    rows = [["Cômodo", "Tipo", "ISA", "Classificação", "Alertas"]]
    for room in rooms_data:
        r_id = room["id"]
        room_isa = next((r for r in isa_result["rooms"] if r["room_id"] == r_id), None)
        if not room_isa:
            continue
        score = room_isa["overall_score"]
        cat = room_isa["category"]
        sc = _score_bar(score)
        cat_lbl = CATEGORY_LABELS.get(cat, cat.value if hasattr(cat, "value") else str(cat))
        alerts_count = len(room_isa.get("alerts", []))
        alert_text = f"{alerts_count} alerta(s)" if alerts_count else "—"
        rows.append([
            Paragraph(f"{room['name']}", ParagraphStyle("rl", fontSize=7, spaceAfter=0)),
            Paragraph(ROOM_TYPE_LABELS.get(room.get("room_type", ""), room.get("room_type", "")), ParagraphStyle("rt", fontSize=7, spaceAfter=0)),
            Paragraph(f"<b>{score:.0f}</b>", ParagraphStyle("rs", fontSize=8, textColor=sc, alignment=TA_CENTER, spaceAfter=0)),
            Paragraph(cat_lbl, ParagraphStyle("rc", fontSize=6, textColor=colors.grey, spaceAfter=0)),
            Paragraph(alert_text, ParagraphStyle("ra", fontSize=6, textColor=HIGH_RISK if alerts_count else colors.grey, spaceAfter=0)),
        ])
    t = Table(rows, colWidths=[80, 60, 35, 80, 55])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def generate_report(inspection: dict, isa_result: dict, rooms_data: list[dict] | None = None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        leftMargin=2*cm, rightMargin=2*cm,
        title=f"MSBD-360 - Relatório #{inspection['id']}",
        author="MSBD-360",
    )

    cat_lbl_style = ParagraphStyle("CatLbl", fontSize=14, leading=16, alignment=TA_CENTER, spaceAfter=0)
    body_s = ParagraphStyle("Body", fontSize=9, leading=12, spaceAfter=4)
    pname_s = ParagraphStyle("PName", fontSize=8, leading=10, textColor=colors.grey, spaceAfter=0)
    pscore_s = ParagraphStyle("PScore", fontSize=8, leading=10, textColor=BRAND_COLOR, alignment=TA_CENTER, spaceAfter=0)
    alert_s = ParagraphStyle("Alert", fontSize=7, leading=9, textColor=HIGH_RISK, spaceAfter=0)

    elements = []

    # ---- COVER / HEADER ----
    header_data = [
        [Paragraph("MSBD-360", ParagraphStyle("hdr", fontSize=28, textColor=BRAND_COLOR, spaceAfter=0)),
         Paragraph(f"Relatório #{inspection['id']}", ParagraphStyle("hdr2", fontSize=12, textColor=ACCENT_COLOR, alignment=TA_RIGHT, spaceAfter=0))],
        [Paragraph("Building Health Assessment — Diagnóstico Ambiental Interior",
                   ParagraphStyle("subhdr", fontSize=9, textColor=colors.grey, spaceAfter=0)),
         ""],
    ]
    header_tbl = Table(header_data, colWidths=[350, 150])
    header_tbl.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 2.5, BRAND_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("SPAN", (0, 1), (1, 1)),
    ]))
    elements.append(header_tbl)
    elements.append(Spacer(1, 0.3*cm))

    # ---- INSPECTION INFO ----
    info_data = [
        ["Cliente:", inspection["client_name"], "Inspetor:", inspection["inspector_name"]],
        ["Endereço:", inspection["property_address"], "Data:", inspection["inspection_date"]],
    ]
    info_tbl = Table(info_data, colWidths=[50, 180, 50, 120])
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
    elements.append(Paragraph("Resumo Executivo", ParagraphStyle("h2", fontSize=15, leading=18, spaceAfter=6, textColor=BRAND_COLOR)))
    overall = isa_result["overall_score"]
    cat = isa_result["category"]
    cat_color = _cat_color(cat)
    cat_label = CATEGORY_LABELS.get(cat, cat.value if hasattr(cat, "value") else str(cat))

    # Big ISA score card
    score_card = Table(
        [[Paragraph(f"{overall:.0f}", ParagraphStyle("bigscore", fontSize=42, leading=46, textColor=cat_color, alignment=TA_CENTER, spaceAfter=0)),
          Paragraph("ISA GERAL", ParagraphStyle("biglbl", fontSize=8, leading=10, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=0)),
          Paragraph(f"{cat_label}", ParagraphStyle("bigcat", fontSize=22, leading=26, textColor=cat_color, alignment=TA_CENTER, spaceAfter=0)),
          Paragraph("Classificação", ParagraphStyle("bigcatlbl", fontSize=8, leading=10, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=0))]],
        colWidths=[90, 90, 160, 100],
    )
    score_card.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (1, 0), 1.5, colors.HexColor("#e2e8f0")),
        ("BOX", (2, 0), (3, 0), 1.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#f8fafc")),
        ("BACKGROUND", (2, 0), (3, 0), colors.HexColor("#f8fafc")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(score_card)
    elements.append(Spacer(1, 0.3*cm))

    # Summary stats
    room_count = len(isa_result["rooms"])
    measured_rooms = sum(1 for r in isa_result["rooms"] if r.get("overall_score", 0) > 0)
    total_alerts = sum(len(r.get("alerts", [])) for r in isa_result["rooms"])
    sum_row = Table(
        [[Paragraph(f"<b>{room_count}</b>", ParagraphStyle("sr", fontSize=14, textColor=BRAND_COLOR, alignment=TA_CENTER, spaceAfter=0)),
          Paragraph("Cômodos", ParagraphStyle("sl", fontSize=6, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=0)),
          Paragraph(f"<b>{overall:.0f}</b>", ParagraphStyle("sr", fontSize=14, textColor=_score_bar(overall), alignment=TA_CENTER, spaceAfter=0)),
          Paragraph("ISA Geral", ParagraphStyle("sl", fontSize=6, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=0)),
          Paragraph(f"<b>{cat_label}</b>", ParagraphStyle("sr", fontSize=14, textColor=_score_bar(overall), alignment=TA_CENTER, spaceAfter=0)),
          Paragraph("Classificação", ParagraphStyle("sl", fontSize=6, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=0)),
          Paragraph(f"<b>{total_alerts}</b>", ParagraphStyle("sr", fontSize=14, textColor=HIGH_RISK if total_alerts > 0 else colors.grey, alignment=TA_CENTER, spaceAfter=0)),
          Paragraph("Alertas", ParagraphStyle("sl", fontSize=6, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=0))]],
        colWidths=[50, 50, 50, 50, 80, 50, 40, 40],
    )
    sum_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (2, 0), (3, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (4, 0), (5, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (6, 0), (7, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(sum_row)
    elements.append(Spacer(1, 0.3*cm))

    # Room list summary table
    elements.append(Paragraph("Resumo dos Cômodos", ParagraphStyle("h3", fontSize=11, leading=14, spaceAfter=4, textColor=ACCENT_COLOR)))
    elements.append(_build_room_list_widget(rooms_data or [], isa_result))
    elements.append(Spacer(1, 0.4*cm))

    # ---- ISA BY ROOM TYPE ----
    if isa_result.get("by_type"):
        elements.append(Paragraph("ISA por Tipo de Cômodo", ParagraphStyle("h2", fontSize=14, leading=18, textColor=BRAND_COLOR, spaceBefore=8)))
        type_data = [["Tipo", "ISA Médio", "Classificação", "Cômodos"]]
        for rt, info in isa_result["by_type"].items():
            rt_label = ROOM_TYPE_LABELS.get(rt, rt)
            avg_score = info["average_score"]
            rt_color = _score_bar(avg_score)
            type_data.append([
                Paragraph(f"<b>{rt_label}</b>", body_s),
                Paragraph(f"<b>{avg_score:.0f}</b>", ParagraphStyle("b", fontSize=10, textColor=rt_color, alignment=TA_CENTER)),
                Paragraph(CATEGORY_LABELS.get(info["category"], info["category"]), body_s),
                Paragraph(", ".join(r["room_name"] for r in info["rooms"]), body_s),
            ])
        type_tbl = Table(type_data, colWidths=[100, 60, 100, 140])
        type_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(type_tbl)
        elements.append(Spacer(1, 0.3*cm))

    elements.append(PageBreak())

    # ---- DETAILED ROOM REPORTS ----
    elements.append(Paragraph("Detalhamento por Cômodo", ParagraphStyle("h2", fontSize=16, leading=20, textColor=BRAND_COLOR, spaceBefore=0)))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_COLOR, spaceAfter=8))

    for idx, room in enumerate(isa_result["rooms"], 1):
        room_color = _cat_color(room["category"])
        room_cat_label = CATEGORY_LABELS.get(room["category"], room["category"])
        room_data = next((rd for rd in (rooms_data or []) if rd["id"] == room["room_id"]), None)

        # Room header
        rh_tbl = Table(
            [[Paragraph(f"<b>{idx}. {room['room_name']}</b>",
                       ParagraphStyle("rh", fontSize=13, textColor=colors.white, spaceAfter=0)),
              Paragraph(f"ISA: {room['overall_score']:.0f} — {room_cat_label}",
                       ParagraphStyle("rh2", fontSize=9, textColor=colors.white, spaceAfter=0, alignment=TA_RIGHT))]],
            colWidths=[250, 250],
        )
        rh_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), room_color),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (0, 0), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))
        elements.append(rh_tbl)

        # Pillar scores
        pillar_data = [["Pilar", "Pontuação", "Barra", "Detalhes"]]
        for pk, pv in room["pillars"].items():
            plabel = PILLAR_LABELS.get(pk, pk.capitalize())
            pscore = pv["score"]
            pcolor = _score_bar(pscore)
            bar_count = max(1, int(pscore / 20))
            bar = "█" * bar_count + "░" * (5 - bar_count)
            pillar_data.append([
                Paragraph(f"{plabel}", pname_s),
                Paragraph(f"<b>{pscore:.0f}</b>", pscore_s),
                Paragraph(f'<font color="{pcolor.hexval()}">{bar}</font>',
                         ParagraphStyle("bar", fontSize=9, spaceAfter=0)),
                Paragraph(pv["details"], ParagraphStyle("det", fontSize=7, textColor=colors.grey, spaceAfter=0)),
            ])

        ptbl = Table(pillar_data, colWidths=[120, 50, 100, 130])
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

        # Sub-location breakdown
        sub_locs = room.get("sub_locations", {})
        if sub_locs:
            elements.append(Spacer(1, 0.2*cm))
            elements.append(Paragraph("Detalhamento por Local de Medição",
                                     ParagraphStyle("subh", fontSize=9, leading=11, textColor=ACCENT_COLOR, spaceBefore=4, spaceAfter=3)))
            sl_data = [["Local", "ISA", "Térmica", "Humidade", "Ventilação", "Materiais", "Iluminação"]]
            for sloc, sl in sub_locs.items():
                sl_label = SUB_LOCATION_LABELS.get(sloc, sloc)
                sl_p = sl.get("pillars", {})
                sl_data.append([
                    Paragraph(f"<b>{sl_label}</b>", ParagraphStyle("sln", fontSize=7, spaceAfter=0)),
                    Paragraph(f"<b>{sl['overall_score']:.0f}</b>", ParagraphStyle("sls", fontSize=7, textColor=_score_bar(sl['overall_score']), spaceAfter=0)),
                    Paragraph(f"{sl_p.get('thermal', {}).get('score', 0):.0f}", ParagraphStyle("slv", fontSize=7, spaceAfter=0)),
                    Paragraph(f"{sl_p.get('humidity', {}).get('score', 0):.0f}", ParagraphStyle("slv", fontSize=7, spaceAfter=0)),
                    Paragraph(f"{sl_p.get('ventilation', {}).get('score', 0):.0f}", ParagraphStyle("slv", fontSize=7, spaceAfter=0)),
                    Paragraph(f"{sl_p.get('materials', {}).get('score', 0):.0f}", ParagraphStyle("slv", fontSize=7, spaceAfter=0)),
                    Paragraph(f"{sl_p.get('lighting', {}).get('score', 0):.0f}", ParagraphStyle("slv", fontSize=7, spaceAfter=0)),
                ])
            sl_tbl = Table(sl_data, colWidths=[70, 35, 45, 50, 50, 50, 50])
            sl_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.2, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ]))
            elements.append(sl_tbl)

            # Alerts for this room
            room_alerts = room.get("alerts", [])
            if room_alerts:
                elements.append(Spacer(1, 0.15*cm))
                for alert in room_alerts:
                    elements.append(Paragraph(f"⚠ {alert}", alert_s))

        # Photos for this room
        if room_data:
            room_photos = [p for p in room_data.get("photos", []) if p.get("photo_data")]
            if room_photos:
                elements.append(Spacer(1, 0.3*cm))
                elements.append(Paragraph("Registo Fotográfico",
                                         ParagraphStyle("phh", fontSize=9, leading=11, textColor=ACCENT_COLOR, spaceBefore=2, spaceAfter=3)))
                for p in room_photos[:4]:
                    try:
                        img_data = p["photo_data"]
                        if "," in img_data:
                            img_data = img_data.split(",")[1]
                        img_bytes = base64.b64decode(img_data)
                        img = Image(io.BytesIO(img_bytes), width=120, height=90)
                        caption = p.get("caption") or p.get("photo_type", "foto")
                        photo_block = Table(
                            [[img],
                             [Paragraph(f"<i>{caption}</i>", ParagraphStyle("pc", fontSize=6, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=0))]],
                            colWidths=[120],
                        )
                        photo_block.setStyle(TableStyle([
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ]))
                        elements.append(photo_block)
                        elements.append(Spacer(1, 0.15*cm))
                    except Exception:
                        pass

        elements.append(Spacer(1, 0.4*cm))

    # ---- FOOTER ----
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=4))
    elements.append(Paragraph(
        f"MSBD-360 — Building Health Assessment  |  Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Documento confidencial",
        ParagraphStyle("footer", fontSize=7, leading=9, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER, spaceAfter=0),
    ))

    doc.build(elements)
    buf.seek(0)
    return buf.read()
