import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import inspections, measurements, photos, reports, rooms
from app.utils.enums import RecommendationPriority


def _run_migrations():
    try:
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        return
    except Exception as e:
        print(f"[startup] Alembic migration failed: {e}")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[startup] create_all failed (DB may not be ready): {e}")


def _seed_recommendations():
    db = SessionLocal()
    try:
        existing = db.execute(text("SELECT COUNT(*) FROM recommendations")).scalar()
        if existing and existing > 0:
            return

        recs = [
            ("TER-01", "Isolamento Térmico", "Melhorar isolamento térmico de paredes e telhado para reduzir perda de calor.", "thermal", RecommendationPriority.MEDIUM),
            ("TER-02", "Climatização", "Instalar ou reparar sistema de climatização (HVAC) para manter temperatura adequada.", "thermal", RecommendationPriority.HIGH),
            ("TER-03", "Controle Solar", "Utilizar cortinas, persianas ou brises para controle da incidência solar.", "thermal", RecommendationPriority.LOW),
            ("TER-04", "Vedação", "Vedar fissuras em portas e janelas para evitar correntes de ar.", "thermal", RecommendationPriority.MEDIUM),
            ("HUM-01", "Barreira de Vapor", "Instalar barreiras de vapor em paredes externas para evitar condensação interna.", "humidity", RecommendationPriority.HIGH),
            ("HUM-02", "Drenagem", "Melhorar drenagem do terreno junto à fundação para evitar umidade ascendente.", "humidity", RecommendationPriority.HIGH),
            ("HUM-03", "Desumidificação", "Utilizar desumidificadores em ambientes críticos com UR acima de 70%.", "humidity", RecommendationPriority.MEDIUM),
            ("HUM-04", "Impermeabilização", "Revisar impermeabilização de lajes, coberturas e áreas molhadas.", "humidity", RecommendationPriority.HIGH),
            ("VEN-01", "Renovação de Ar", "Aumentar a taxa de renovação do ar abrindo janelas ou instalando ventilação mecânica.", "ventilation", RecommendationPriority.HIGH),
            ("VEN-02", "Ventilação Mecânica", "Instalar sistema de ventilação com recuperação de calor para eficiência energética.", "ventilation", RecommendationPriority.MEDIUM),
            ("VEN-03", "Manutenção HVAC", "Limpar e manter dutos de ar condicionado regularmente.", "ventilation", RecommendationPriority.MEDIUM),
            ("VEN-04", "Fontes de Poluição", "Reduzir fontes internas de poluição como materiais sintéticos e produtos químicos.", "ventilation", RecommendationPriority.LOW),
            ("MAT-01", "Substituição de Materiais", "Substituir materiais deteriorados ou com alta absorção de umidade.", "materials", RecommendationPriority.HIGH),
            ("MAT-02", "Revestimento Impermeável", "Aplicar revestimento impermeabilizante em alvenaria exposta.", "materials", RecommendationPriority.MEDIUM),
            ("MAT-03", "Tratamento Antifungo", "Realizar tratamento antifungo em superfícies afetadas por bolor.", "materials", RecommendationPriority.HIGH),
            ("MAT-04", "Reparo de Infiltrações", "Reparar infiltrações na origem antes de recuperar revestimentos.", "materials", RecommendationPriority.HIGH),
            ("LUX-01", "Iluminação Natural", "Aumentar iluminação natural com aberturas, claraboias ou shafts de luz.", "lighting", RecommendationPriority.MEDIUM),
            ("LUX-02", "Luminárias LED", "Instalar luminárias LED com distribuição uniforme e temperatura de cor adequada.", "lighting", RecommendationPriority.MEDIUM),
            ("LUX-03", "Pintura Clara", "Utilizar pintura clara em paredes e tetos para refletir melhor a luz.", "lighting", RecommendationPriority.LOW),
            ("LUX-04", "Iluminação de Tarefa", "Complementar iluminação geral com luminárias de tarefa em postos de trabalho.", "lighting", RecommendationPriority.LOW),
            ("VIS-01", "Vistoria Técnica", "Realizar vistoria técnica detalhada para identificar causas raiz das anomalias.", "visual", RecommendationPriority.HIGH),
            ("VIS-02", "Documentação Fotográfica", "Documentar todas as anomalias visuais com registro fotográfico georreferenciado.", "visual", RecommendationPriority.MEDIUM),
            ("VIS-03", "Avaliação Estrutural", "Contratar engenheiro especialista para avaliação estrutural se houver trincas ou fissuras.", "visual", RecommendationPriority.HIGH),
            ("VIS-04", "Plano de Ação", "Elaborar plano de ação corretiva priorizando riscos imediatos à saúde e segurança.", "visual", RecommendationPriority.HIGH),
        ]
        for code, title, desc, category, priority in recs:
            db.execute(
                text("INSERT INTO recommendations (code, title, description, category, priority, is_active) VALUES (:code, :title, :desc, :cat, :pri, 1)"),
                {"code": code, "title": title, "desc": desc, "cat": category, "pri": priority.value},
            )
        db.commit()
        print(f"[seed] {len(recs)} recommendations inserted")
    except Exception as e:
        db.rollback()
        print(f"[seed] Skipped: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_migrations()
    _seed_recommendations()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Building Health Assessment — MSBD-360 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inspections.router, prefix=settings.api_v1_prefix)
app.include_router(rooms.router, prefix=settings.api_v1_prefix)
app.include_router(measurements.router, prefix=settings.api_v1_prefix)
app.include_router(photos.router, prefix=settings.api_v1_prefix)
app.include_router(reports.router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


@app.get("/health/db")
def health_db():
    """Test database connection and report which URL is being used."""
    from sqlalchemy import text

    info = {
        "database_url_configured": bool(settings.database_url),
        "resolved_url_start": settings.resolved_database_url[:50] + "...",
        "using_sqlite": "sqlite" in settings.resolved_database_url,
    }
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            info["connection"] = "ok"
            result = db.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            ).fetchall()
            info["tables"] = [r[0] for r in result]
    except Exception as e:
        info["connection"] = "error"
        info["error"] = str(e)
    return info
