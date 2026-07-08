# CBAM XLSX Validator

API en Python (FastAPI) para la validacion de archivos Excel en el formato
del template CBAM (Carbon Border Adjustment Mechanism). Ingiere el archivo,
aplica las reglas definidas en la hoja Rules y persiste las filas validas en
una base de datos relacional.

---

## Requisitos

- Python 3.12 o superior
- pip

---

## Instalacion y arranque (5 minutos)

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd cbam-xlsx-validator

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv

# En Windows (Git Bash):
source .venv/Scripts/activate
# En Linux/macOS:
# source .venv/bin/activate

pip install -r backend/requirements.txt -r backend/requirements-dev.txt

# 3. Configurar variables de entorno
cp .env.example backend/.env
# El archivo copiado ya funciona con SQLite local.
# No requiere edicion para desarrollo local.

# 4. Crear el esquema de la base de datos
cd backend
alembic upgrade head
cd ..

# 5. Iniciar el servidor
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abrir http://127.0.0.1:8000/docs en el navegador para acceder a la
documentacion interactiva (Swagger UI) de la API.

---

## Endpoints

| Metodo | Ruta              | Descripcion                                      | Codigos de respuesta |
|--------|-------------------|--------------------------------------------------|----------------------|
| GET    | `/health`         | Verifica que el servidor esta operativo          | 200                  |
| POST   | `/upload`         | Sube un archivo .xlsx (multipart, campo `file`)  | 200, 400             |
| GET    | `/records`        | Lista las filas validas persistidas, paginadas   | 200, 422             |

### Parametros de `/records`

| Parametro  | Tipo | Default | Validacion     |
|------------|------|---------|----------------|
| `page`     | int  | 1       | mayor o igual a 1  |
| `page_size`| int  | 20      | entre 1 y 100  |

---

## Probar la API con curl

```bash
# Verificar salud del servidor
curl http://127.0.0.1:8000/health

# Subir un archivo de prueba (incluido en el repositorio)
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@backend/tests/data/cbam_template.xlsx" | python -m json.tool

# Listar filas validas persistidas
curl "http://127.0.0.1:8000/records?page=1&page_size=10" | python -m json.tool

# Probar validacion de paginacion (debe devolver 422)
curl "http://127.0.0.1:8000/records?page=0"
```

### Respuesta esperada de `/upload`

```json
{
  "filename": "cbam_template.xlsx",
  "total_rows": 5,
  "valid_rows": 1,
  "invalid_rows": 4,
  "errors": [
    {
      "row": 2,
      "field": "EORI Number",
      "value": "",
      "message": "is required"
    }
  ]
}
```

---

## Ejecutar los tests

```bash
cd backend
pytest -v
```

84 tests que cubren:

- Lectura del archivo Excel (hojas Template y Rules)
- Parseo de reglas desde la hoja Rules
- Validacion estructural (consistencia de columnas)
- 30 tests unitarios de validadores (required, max_length, regex, date,
  positive_number, allowed_values)
- Validacion por fila con 13 escenarios
- 9 tests funcionales del endpoint POST /upload
- 6 tests funcionales del endpoint GET /records
- Persistencia de modelos SQLAlchemy y migracion Alembic
- Integracion E2E contra el template real

---

## Base de datos

- **Por defecto**: SQLite (archivo `backend/cbam.db`). No requiere instalacion
  ni configuracion adicional.
- **Produccion**: cambiar `DATABASE_URL` en `backend/.env` a una base de datos
  PostgreSQL y ejecutar `alembic upgrade head` para crear el esquema.
- Las migraciones se encuentran en `backend/alembic/versions/`. Siempre se
  parte de una base de datos limpia.

### Esquema

- `import_jobs`: registro de cada archivo subido (filename, uploaded_at,
  total_rows, valid_rows, invalid_rows).
- `records`: filas validas extraidas del archivo (import_job_id FK, row_number,
  payload en JSON, created_at).

---

## Estructura del proyecto

```
cbam-xlsx-validator/
  backend/
    app/
      api/v1/endpoints/  # GET /health, POST /upload, GET /records
      services/           # ExcelReader, RulesReader, WorkbookValidator,
                          # ValidationService, ImportService
      validators/         # required, max_length, regex, date,
                          # positive_number, allowed_values
      repositories/       # ImportJobRepository, RecordRepository
      models/             # SQLAlchemy: ImportJob, Record
      schemas/            # Pydantic: UploadReport, RecordOut, PaginatedRecords
      database/           # engine, session, Base declarativa
      core/               # Settings, AppException, logging
    alembic/versions/     # Migraciones de base de datos
    tests/                # 84 tests con pytest
  frontend/               # Capa opcional (React + Vite + TypeScript)
  scripts/                # Scripts de arranque
  .env.example            # Template de variables de entorno (copiar a backend/.env)
```

---

## Capa frontend opcional

Hay una SPA en React (carpeta `frontend/`) que consume los mismos endpoints
del backend. Es opcional: el backend funciona de forma independiente.

```bash
cd frontend
cp .env.example .env          # crear frontend/.env con VITE_API_URL
pnpm install
pnpm run dev                  # http://localhost:5173
```

Funcionalidades: pagina de Upload (seleccion de archivo, envio, resumen con
estadisticas, tabla de errores por fila) y pagina de Records (tabla paginada
con preview de columnas, modal con JSON completo de cada registro, indicador
de salud del backend).

---

## Notas tecnicas

- Los valores del Excel se leen con `dtype=str` y `keep_default_na=False` para
  evitar que pandas convierta valores como `05.05.2026` a numeros.
- La hoja Rules se acepta con nombre `Rules` o `Sheet1` (compatibilidad con
  versiones del template).
- Los archivos sin filas de datos (solo encabezados) son rechazados con
  codigo 400 y un mensaje explicativo.
- Los campos opcionales vacios no generan errores de validacion.
