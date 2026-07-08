# CBAM XLSX Validator

Base architecture for a technical backend challenge focused on Excel ingestion and validation.  
This iteration delivers only a clean, extensible foundation (no business logic yet).

## Tech Stack

### Backend
- Python 3.12+
- FastAPI + Uvicorn
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Pydantic v2
- OpenPyXL
- Pandas
- Pytest

### Frontend
- React
- Vite
- TypeScript
- Axios
- React Router

## Project Structure

```text
.
├── backend
│   ├── alembic
│   │   ├── versions
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── app
│   │   ├── api
│   │   │   └── v1/endpoints
│   │   ├── core
│   │   ├── database
│   │   ├── models
│   │   ├── repositories
│   │   ├── schemas
│   │   ├── services
│   │   ├── validators
│   │   └── tests
│   │       └── data
│   ├── alembic.ini
│   ├── pytest.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend
│   ├── src
│   │   ├── components
│   │   ├── hooks
│   │   ├── pages
│   │   ├── router
│   │   ├── services
│   │   └── types
│   └── package.json
├── docs
├── scripts
├── .env.example
└── .gitignore
```

## Environment Setup

### 1) Create virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 2) Install backend dependencies

```bash
pip install -r backend/requirements-dev.txt
```

### 3) Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Run Backend

```bash
./scripts/run_backend.sh
```

Or directly:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run Frontend

```bash
./scripts/run_frontend.sh
```

## Run Migrations

```bash
cd backend
alembic upgrade head
```

## Run Tests

```bash
./scripts/run_tests.sh
```

## Available API Endpoints (Current Iteration)

- `GET /health` → returns application health status
- `POST /upload` → `501 Not Implemented`
- `GET /records` → `501 Not Implemented`

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

- `DATABASE_URL`
- `APP_NAME`
- `DEBUG`
- `HOST`
- `PORT`

## Notes

This iteration intentionally excludes:
- Excel parsing
- Validation rules execution
- Record persistence logic
- Functional frontend integration

The project is ready for incremental feature implementation in the next iteration.
