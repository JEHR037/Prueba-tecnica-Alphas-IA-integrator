# Prueba técnica – ALPHAS IA Integrator (RAG RRHH)

### Descripción
Sistema RAG (Retrieval-Augmented Generation) para consultas sobre políticas de RRHH con:
- Búsqueda semántica sobre documentos y FAQs precargados
- Contexto por departamento y categorías
- Endpoints REST con FastAPI, documentación Swagger y health checks
- Modo “integrado” con carga automática de datos y modo “estándar” con servicio RAG modular

---

## 1) Análisis heurístico del software

- **Arquitectura**: Clean/Hexagonal orientada a casos de uso y puertos/adaptadores.
  - `application/` contiene DTOs y casos de uso.
  - `domain/` define entidades y excepciones del dominio RAG.
  - `infrastructure/` aporta adaptadores (repositorios SQLite, embeddings), configuración, servicios de datos precargados y capa web (FastAPI).
- **Modos de ejecución**:
  - **API actualizada (recomendada)**: `src/infrastructure/web/api/endpoints.py` expone `/ask`, `/documents/*`, `/system/*`, `/departments`, y usa `IntegratedRAGService` para datos precargados.
  - **API mejorada “enhanced”**: `src/infrastructure/web/api/rag_enhanced_endpoints.py` enruta bajo prefijo `/enhanced/*`, con endpoints para inicialización y métricas de datos precargados.
  - **API consolidada**: `src/infrastructure/web/server.py` combina un RAG “ALPHAS” y uno estándar en un único servicio (modo demo/compatibilidad).
- **Carga de datos**: `DataLoaderService` carga políticas y FAQs de `infrastructure/data/preloaded_hr_policies.py` en el backend RAG (SQLite + embeddings). También valida y expone estadísticas de carga.
- **Embeddings y búsqueda**: `RAGFactory`, `sentence-transformers`, `sqlite-vss` y adaptadores implementan indexación/búsqueda vectorial y recuperación de fragmentos; `IntegratedRAGService` compone la respuesta con contexto.
- **DTOs y validación**: `application/dto/api_dto.py` centraliza requests/responses con Pydantic.
- **Observabilidad**: logs estándar; existe un logger ALPHAS opcional en `infrastructure/logger/*` usado por el servidor consolidado.

---

## 2) Requisitos

Python 3.10+ (recomendado 3.11) y pip/venv.

Dependencias principales (ver `requirements.txt`):
- FastAPI, Uvicorn
- Pydantic 2.x
- sentence-transformers, sqlite-vss
- SQLAlchemy, ChromaDB, LangChain (soporte)

Instalación:
```bash
python -m venv venv
venv\Scripts\python -m pip install -U pip
venv\Scripts\pip install -r requirements.txt
```

Variables opcionales (archivo `.env`):
- `OPENAI_API_KEY` (si se habilita generación con OpenAI en componentes compatibles)
- `RAG_API_HOST`, `RAG_API_PORT`, `RAG_API_RELOAD`, `RAG_API_WORKERS` (solo servidor consolidado)

---

## 3) Ejecución

### Opción A – API RAG actualizada (puerto 8000)

Inicia los endpoints modernos con datos precargados y contexto por departamento:
```bash
python run_updated_api.py
```
- Docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

### Opción B – API “Enhanced” con prefijo /enhanced (puerto 8002)

Incluye endpoints de inicialización y estadísticas de datos precargados:
```bash
python run_enhanced_rag_api.py
```
- Docs: `http://127.0.0.1:8002/enhanced/docs`
- Health: `http://127.0.0.1:8002/enhanced/health`

### Opción C – Servidor consolidado (demo)

Combina sistemas ALPHAS y estándar en una única API:
```bash
python run_api.py
```
- Docs: `http://127.0.0.1:8000/docs`

---

## 4) Endpoints principales

### API actualizada (`:8000`)
- **POST `/ask`**: pregunta principal con datos precargados y contexto.
- **GET `/ask`**: variante rápida por querystring.
- **GET `/system/integrated/status`**: estado del sistema integrado (carga, docs, métricas).
- **GET `/system/info`**: resumen de sistema (categorías, departamentos, total docs).
- **GET `/system/stats`**: métricas de uso y configuración.
- **POST `/documents`**: alta de documento.
- **GET `/documents/search`**: búsqueda de documentos.
- **DELETE `/documents/{id}`**: eliminación de documento.
- **GET `/departments`** y **GET `/departments/{department}/categories`**.
- **GET `/health`** y **GET `/`** información básica.

### API enhanced (`:8002/enhanced`)
- **POST `/system/initialize`**: inicialización/recarga de datos en background.
- **GET `/system/status`**: estado de datos precargados.
- **GET `/data/info`**: inventario de políticas y FAQs.
- **POST `/ask`** y **GET `/ask/quick`**: preguntas con opciones extra (FAQs, preferencia recientes, etc.).
- **GET `/categories`**, **GET `/departments/{department}/policies`**.
- **GET `/search/faq`**, **GET `/health`**, **GET `/`**.

---

## 5) Ejemplos rápidos

PowerShell (Windows):
```powershell
# Pregunta principal (API 8000)
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/ask" -ContentType 'application/json' -Body (@{
  question = '¿Cuál es la política de trabajo remoto?'
  department = 'rrhh'
  use_ai = $true
  top_k = 5
} | ConvertTo-Json)

# Búsqueda de documentos
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/documents/search?query=vacaciones&top_k=5"
```

curl:
```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Cuáles son los beneficios de salud?","department":"rrhh","use_ai":true,"top_k":5}'
```

Enhanced (inicialización y pregunta rápida):
```bash
curl -X POST http://127.0.0.1:8002/enhanced/system/initialize \
  -H "Content-Type: application/json" -d '{"force_reload":false,"auto_validate":true}'
curl "http://127.0.0.1:8002/enhanced/ask/quick?question=politica%20de%20vacaciones"
```

---

## 6) Pruebas

Ejecutar pruebas manuales contra la API en `:8000`:
```bash
python test_rag_simple.py
python test_integrated_rag.py
```

Los scripts validan health, estado integrado y preguntas de ejemplo, mostrando confianza y fuentes.

---

## 7) Configuración RAG y datos

- Config por defecto en `src/infrastructure/config/rag_config.py`:
  - `database_path = "hr_policies.db"`
  - `embedding_model = "all-MiniLM-L6-v2"`
  - `chunk_size = 500`, `chunk_overlap = 50`, `default_top_k = 5`
- Datos precargados en `src/infrastructure/data/preloaded_hr_policies.py`.
- Cargador y validación de datos: `src/infrastructure/services/data_loader_service.py`.
- Servicio integrado: `src/infrastructure/services/integrated_rag_service.py`.

---

## 8) Notas y recomendaciones

- Ejecutar en entorno virtual limpio y versiones fijas de `requirements.txt`.
- Para producción, restringir CORS y ocultar `/docs` si aplica.
- Persistencia: asegúrate de permisos de escritura para la base SQLite.
- Si habilitas OpenAI, configura `OPENAI_API_KEY` y revisa límites de uso.

---

## 9) Estructura del proyecto (resumen)

```
src/
  application/           # DTOs y casos de uso
  domain/                # Entidades y excepciones de dominio
  infrastructure/
    adapters/            # Integraciones RAG/DB/Embeddings
    config/              # Configuración RAG
    data/                # Datos precargados RRHH
    services/            # Data loader, servicio integrado
    web/api/             # FastAPI endpoints (actualizado y enhanced)
    web/server.py        # Servidor consolidado (demo)
```

---

## 10) Licencia

Ver `LICENSE`.
