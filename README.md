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

### Probar endpoints desde Swagger

Desde http://127.0.0.1:8000/docs se pueden ejecutar los endpoints directamente:

- **POST /upload** — hacer clic en "Try it out", seleccionar un archivo .xlsx
  en el campo `file`, ejecutar y ver la respuesta JSON con el reporte de
  validacion.
- **GET /records** — ejecutar con parametros `page` y `page_size` para listar
  las filas validas persistidas.
- **GET /health** — verificar que el servidor esta operativo.

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

## Pruebas manuales (solo backend)

Instructivo paso a paso para probar la API manualmente con curl.

### Requisitos previos

- Servidor detenido (puerto 8000 libre)
- Entorno virtual activo

### 1. Preparar base de datos limpia

```bash
cd backend
rm -f cbam.db
alembic upgrade head
```

Salida esperada: `Running upgrade  -> <hash>, initial schema`

### 2. Iniciar el servidor

```bash
cd backend
uvicorn app.main:app --reload
```

Salida esperada: `Uvicorn running on http://127.0.0.1:8000`

Mantener esta terminal abierta. Abrir una terminal nueva para los comandos
siguientes (todo desde la carpeta `backend/`).

### 3. Health check

```bash
curl http://127.0.0.1:8000/health
```

Esperado: HTTP 200 — `{"status":"ok"}`

### 4. Subir archivo valido

```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@tests/data/valid_sample.xlsx"
```

Esperado: HTTP 200 — `total_rows: 3, valid_rows: 3, invalid_rows: 0`

### 5. Subir archivo invalido

```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@tests/data/invalid_sample.xlsx"
```

Esperado: HTTP 200 — `total_rows: 3, valid_rows: 0, invalid_rows: 3`
con 3 errores (filas 2, 3 y 4).

### 6. Listar registros persistidos

```bash
curl "http://127.0.0.1:8000/records?page=1&page_size=10"
```

Esperado: HTTP 200 — `page: 1, total: 3`, con los 3 registros validos.

### 7. Paginacion con parametros invalidos

```bash
curl "http://127.0.0.1:8000/records?page=0"
```

Esperado: HTTP 422 con detalle `page must be >= 1`.

```bash
curl "http://127.0.0.1:8000/records?page=1&page_size=0"
```

Esperado: HTTP 422 con detalle `page_size must be >= 1`.

### 8. Rechazo por extension incorrecta

```bash
echo "no es xlsx" > /tmp/archivo.txt
curl -X POST http://127.0.0.1:8000/upload -F "file=@/tmp/archivo.txt"
```

Esperado: HTTP 400 — `Only .xlsx files are accepted`

### 9. Rechazo por archivo mayor a 10 MB

```bash
python -c "open('/tmp/grande.bin','wb').write(b'x' * (11 * 1024 * 1024))"
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@/tmp/grande.bin;filename=grande.xlsx"
```

Esperado: HTTP 400 — `File too large. Maximum size is 10 MB, got 11.00 MB`

### 10. Rechazo por archivo sin filas de datos

```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@tests/data/cbam_template.xlsx"
```

Esperado: HTTP 400 — `The uploaded file contains no data rows`

### Resumen de codigos HTTP esperados

| Caso | Codigo | Mensaje clave |
|---|---|---|
| Health | 200 | `{"status":"ok"}` |
| Upload valido | 200 | `valid_rows: 3` |
| Upload invalido | 200 | `invalid_rows: 3`, 3 errores |
| Pagina invalida | 422 | validacion Pydantic |
| Extension incorrecta | 400 | `Only .xlsx files are accepted` |
| Archivo > 10 MB | 400 | `File too large...` |
| Archivo sin filas | 400 | `no data rows` |

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
