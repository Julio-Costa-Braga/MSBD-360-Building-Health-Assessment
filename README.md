# MSBD-360 — Building Health Assessment

Sistema de diagnóstico ambiental de edifícios com cálculo do **ISA (Índice de Saúde Ambiental)**.

## Stack

| Camada    | Tecnologia                                         |
|-----------|----------------------------------------------------|
| Backend   | Python 3.12 + FastAPI + SQLAlchemy + Pydantic      |
| Frontend  | React 18 + TypeScript + Vite + Tailwind + Recharts |
| Banco     | SQLite (dev) / PostgreSQL (prod — Supabase)        |
| Migrations| Alembic                                            |
| Deploy    | Docker Compose                                     |

## Estrutura

```
msbd-360/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Config (DATABASE_URL, etc)
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   ├── models/              # ORM models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   └── services/
│   │       ├── isa_calculator.py      # ISA scoring engine
│   │       ├── recommendation_engine.py
│   │       └── report_generator.py    # PDF export
│   ├── alembic/                 # DB migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.ts        # Axios client
│   │   ├── components/          # ISAGauge, RoomCard, Layout
│   │   ├── pages/               # Dashboard, NewInspection, InspectionDetail
│   │   └── types/index.ts       # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
└── docker-compose.yml
```

## ISA — Índice de Saúde Ambiental

Score 0–100 baseado em 6 pilares com pesos:

| Pilar                      | Peso | Faixa Ideal (referência)          |
|----------------------------|------|-----------------------------------|
| Condições Térmicas         | 1.0  | 20–24 °C (ASHRAE 55)              |
| Humidade e Condensação     | 1.2  | 40–60% UR + risco de condensação  |
| Ventilação (CO₂)           | 1.1  | < 800 ppm (ASHRAE 62.1)           |
| Estado dos Materiais       | 1.0  | < 12% umidade                      |
| Iluminação                 | 0.8  | 300–750 lux (NBR 5413)            |
| Evidências Visuais         | 0.9  | Sem anomalias registradas         |

Cores: **Verde** (80–100) · **Amarelo** (60–79) · **Laranja** (40–59) · **Vermelho** (< 40)

## Rodar Local

### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API em `http://localhost:8000` — Swagger em `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend em `http://localhost:3000`

### Docker

```bash
docker compose up --build
```

## Supabase (produção)

1. Crie um projeto no [Supabase](https://supabase.com)
2. Vá em **Project Settings > Database > Connection string**
3. Copie a URI `postgresql://...`
4. Crie `.env` no backend:

```env
DATABASE_URL=postgresql://user:password@host:6543/postgres
```

5. Rode as migrations:

```bash
cd backend
alembic upgrade head
```

## API Endpoints

| Método | Endpoint                           | Descrição                |
|--------|------------------------------------|--------------------------|
| GET    | `/api/v1/inspections`              | Listar inspeções         |
| POST   | `/api/v1/inspections`              | Criar inspeção           |
| GET    | `/api/v1/inspections/:id`          | Detalhes da inspeção     |
| PATCH  | `/api/v1/inspections/:id`          | Atualizar inspeção       |
| DELETE | `/api/v1/inspections/:id`          | Excluir inspeção         |
| GET    | `/api/v1/inspections/:id/rooms`    | Listar cômodos           |
| POST   | `/api/v1/inspections/:id/rooms`    | Adicionar cômodo         |
| POST   | `/api/v1/rooms/:id/measurements`   | Adicionar medição        |
| GET    | `/api/v1/inspections/:id/reports/isa` | Calcular ISA          |
| GET    | `/api/v1/inspections/:id/reports/pdf`  | Exportar PDF           |

## Sugestões de Hospedagem

- **Frontend**: Vercel (deploy automático via git)
- **Backend**: Railway ou Render (suportam FastAPI nativamente)
- **Banco**: Supabase (PostgreSQL gerenciado, free tier)
