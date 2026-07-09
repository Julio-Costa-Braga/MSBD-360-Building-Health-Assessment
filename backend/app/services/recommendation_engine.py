"""
Matches low pillar scores to predefined technical recommendations.
"""

from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.services.isa_calculator import RoomISAResult


PILLAR_RECOMMENDATION_MAP = {
    "thermal": [
        "Melhorar isolamento térmico de paredes e telhado.",
        "Instalar ou reparar sistema de climatização (HVAC).",
        "Utilizar cortinas ou persianas para controle solar.",
        "Vedar fissuras em portas e janelas.",
    ],
    "humidity": [
        "Instalar barreiras de vapor em paredes externas.",
        "Melhorar drenagem do terreno junto à fundação.",
        "Utilizar desumidificadores em ambientes críticos.",
        "Revisar impermeabilização de lajes e coberturas.",
    ],
    "ventilation": [
        "Aumentar a taxa de renovação do ar (abrir janelas ou instalar ventilação mecânica).",
        "Instalar sistema de ventilação com recuperação de calor.",
        "Limpar e manter dutos de ar condicionado.",
        "Reduzir fontes internas de poluição (materiais, produtos químicos).",
    ],
    "materials": [
        "Substituir materiais deteriorados ou com alta absorção de umidade.",
        "Aplicar revestimento impermeabilizante em alvenaria exposta.",
        "Realizar tratamento antifungo em superfícies afetadas.",
        "Reparar infiltrações na origem antes de recuperar revestimentos.",
    ],
    "lighting": [
        "Aumentar iluminação natural com aberturas ou claraboias.",
        "Instalar luminárias LED com distribuição uniforme.",
        "Utilizar pintura clara em paredes para refletir luz.",
        "Complementar iluminação geral com luminárias de tarefa.",
    ],
    "visual": [
        "Realizar vistoria técnica detalhada para identificar causas raiz.",
        "Documentar todas as anomalias visuais com registro fotográfico.",
        "Contratar engenheiro especialista para avaliação estrutural.",
        "Elaborar plano de ação corretiva priorizando riscos imediatos.",
    ],
}


def get_recommendations_for_room(db: Session, room_result: RoomISAResult) -> list[dict]:
    """Get recommendations based on pillar scores."""
    matched = []
    for pillar_key, pillar_result in room_result.pillars.items():
        if pillar_result.score < 60:
            suggestions = PILLAR_RECOMMENDATION_MAP.get(pillar_key, [])
            db_recs = (
                db.query(Recommendation)
                .filter(
                    Recommendation.category == pillar_key,
                    Recommendation.is_active == True,
                )
                .all()
            )
            for rec in db_recs:
                matched.append({
                    "recommendation_id": rec.id,
                    "code": rec.code,
                    "title": rec.title,
                    "description": rec.description,
                    "category": pillar_key,
                    "priority": rec.priority,
                })
            if not db_recs:
                for idx, suggestion in enumerate(suggestions[:2]):
                    matched.append({
                        "recommendation_id": None,
                        "code": f"AUTO-{pillar_key.upper()}-{idx+1}",
                        "title": f"Recomendação para {pillar_key}",
                        "description": suggestion,
                        "category": pillar_key,
                        "priority": "medium" if pillar_result.score >= 40 else "high",
                    })
    return matched
