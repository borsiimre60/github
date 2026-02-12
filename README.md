# SzakiSzerviz PRO – CORE v1

FastAPI + PostgreSQL skeleton a SzakiSzerviz PRO CORE v1-hez.

## Tartalom

- FastAPI app: `app/`
- SQL schema: `db/schema.sql`
- Docker Compose PostgreSQL: `docker-compose.yml`
- Korábbi architektúra jegyzet: `docs/szakiszerviz-pro-core-architecture.md`

## 1) PostgreSQL indítás (persistent volume)

```bash
docker compose up -d
```

## 2) Függőségek telepítése

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Sémalétrehozás

```bash
psql postgresql://postgres:postgres@localhost:5432/szakiszerviz -f db/schema.sql
```

## 4) API indítás

```bash
uvicorn app.main:app --reload
```

## 5) Elérhető minimál endpointok

- `POST /jobs`
- `GET /jobs/{id}`
- `POST /jobs/{id}/assign`
- `POST /assignments/{id}/response`
- `GET /diagnostics/sendability?job_id=...`
- `GET /health`

## Megjegyzés

A projekt v1 skeleton: a business logika minimális, a cél a futtatható alap és a CORE táblák/endpointok előkészítése.
