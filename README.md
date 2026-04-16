# Stress Companion Backend

> A FastAPI-based backend service for the Stress Companion application, providing real-time AI capabilities, sensor integrations, database management, and more.

## 1. Project Overview and Backend Purpose
The Stress Companion Backend serves as the robust foundation for the Stress Companion application. It exposes a modern REST API and WebSocket endpoints built with FastAPI. It handles essential back-end operations such as:
- **AI Chat & Interviews**: Real-time integration with Google's Gemini API and a fallback local Hugging Face LLM.
- **Sensor Data Streaming**: Native processing of raw binary frames out of Optical and Thermal cameras to ascertain stress levels via WebSockets.
- **Session & User Profiling**: Secure registration, session state tracking, demographic storage, and profiling of user's mental traits mapping directly into a robust PostgreSQL database.

## 2. Complete Backend Tech Stack
The backend is primarily built with the following technologies and libraries:
- **Framework & Routing**: [FastAPI](https://fastapi.tiangolo.com/) (Web framework), `uvicorn` (ASGI Server).
- **Core Processing Language**: **Python 3.9+**
- **Database & ORM**: **PostgreSQL** (optimised for NeonDB), `psycopg2-binary`, managed natively by [SQLAlchemy](https://www.sqlalchemy.org/).
- **AI/Machine Learning Integration**:
  - LLMs: `google-genai` (Gemini API for primary chat features), Hugging Face `transformers` + `torch` (for Local fallback Model `Qwen/Qwen2.5-0.5B-Instruct`).
  - Frame Processing: `opencv-python`, alongside dedicated scikit-learn models.
- **Concurrency & Events**: `anyio` and native WebSockets (`websockets`) for ultra-low latency streams.
- **Validation**: Pydantic (`pydantic` & `pydantic-settings`).
- **Security & Authorization**: bcrypt implementation, `pyjwt`, and `python-jose` for secure JWT tokens.

## 3. Folder and Module Structure Overview
The highly modular architecture segregates standard concerns efficiently:
```
stress_companion_backend/
├── app/
│   ├── core/           # Security, environment configs (Pydantic settings), and global exception handlers
│   ├── db/             # SQLAlchemy engine creation, PostgreSQL bindings, and Session models
│   ├── db_models/      # SQLAlchemy ORM definitions natively mapping to PostgreSQL tables
│   ├── repositories/   # Storage layers handling raw abstracted Object Queries against tables
│   ├── routes/         # FastAPI Routers exposing HTTP (Auth/Session) and WebSocket APIs
│   ├── schemas/        # Dedicated Pydantic objects for parsing API Request/Response shapes
│   ├── scripts/        # Utility helpers such as `download_local_llm.py`
│   ├── services/       # Core Business Logic encapsulating API flow, DB parsing, and Model ingestion
│   ├── utils/          # Miscellaneous internal processing rules
│   ├── main.py         # Main entrypoint containing the Uvicorn FastAPI definition/middleware.
│   └── init_db.py      # Automated table-spinup schema executor.
├── storage/            # Disk storage locations for persistent offline records
├── uploads/            # Temporary directories isolating binary payloads and artifacts
├── .env.example        # Target schema describing needed ENV configurations
├── requirements.txt    # Frozen pip dependencies handling packages
└── migrate_schema.py   # Raw database mutation module (e.g. variable naming updates)
```

## 4. Environment Setup Instructions
To prepare your environment, clone the backend repository, navigate into the directory `stress_companion_backend`, ensure that Git is accessible, and verify `Python 3.9+` is accessible on your system path.
Ensure an internet connection is established and preserve ~1.5GB of free disk space required to house local machine-learning packages securely.

## 5. Virtual Environment Creation and Activation
Operating safely within a virtual environment prevents internal library conflicts:
**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 6. Dependency Installation
Load all project-required frameworks (FastAPI, Torch, Transformers, Uvicorn, PostgreSQL binaries) by firing PIP against the target definition block:
```bash
pip install -r requirements.txt
```

## 7. Required `.env` Configuration
Duplicate `.env.example` as a new raw text file named `.env`, and assign real values to its requirements:
- **`ENVIRONMENT`**: Determines mode. Usually `development` opens up Swagger endpoints (`/docs`). Set `production` otherwise.
- **`ALLOWED_ORIGINS`**: Essential for preventing CORS drops. Must strictly be a list (like `http://localhost:5173,https://yourdomain.com`). No trailing slashes.
- **`GEMINI_API_KEY`**: Native credential required to parse LLM interactions with `google-genai`.
- **`PROJECT_NAME`**: Exposed globally for title referencing and metadata checks.
- **`GEMINI_MODEL_NAME`**: Explicit targeted model config (Defaults gracefully to `gemini-2.5-flash`).
- **`DATABASE_URL`**: Hard PostgreSQL routing connection block beginning `postgresql://`. Works intimately with NeonDB.
- **`SECRET_KEY`**: Hashing string essential for User ID masking and encryption bindings. 

## 8. Initializing the Local LLM
The platform can operate completely natively via `Qwen/Qwen2.5-0.5B-Instruct` (~1GB in size).
To pre-download this asset to your offline cache seamlessly, execute:
```bash
python app/scripts/download_local_llm.py
```
This utility determines cache capacities dynamically through `huggingface_hub` limits, fetching configurations natively.

## 9. Backend Startup and Execution Steps
**1. Initializing Tables:**
For first-time environment loads, instantiate SQLAlchemy data points:
```bash
python -m app.init_db
```
**2. Service Application Server:**
Direct traffic toward Uvicorn definitions dynamically on Port `8000`:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API docs become visible implicitly around `http://localhost:8000/docs`.

## 10. API Architecture and Endpoint Overview
Traffic behaves dynamically based on payload types:
- **`POST /api/v1/auth/*`**: Dedicated JWT-based credential validations.
- **`GET / POST / PUT /api/v1/sessions/*`**: Isolates chronological history events, user sessions, and metadata objects inside standard REST forms.
- **`POST /api/v1/chat/gemini`** and **`/api/v1/chat/local`**: Specialized prompt handling targeting AI endpoints safely.
- **`WS /ws/optical`**: WebSockets specifically extracting visual components streaming 3 FPS binary objects.
- **`WS /ws/thermal`**: Analogous WebSocket encapsulating inferred temperature bounds inside RGB.

## 11. Request/Response Flow and Service Integration
A strict architectural flow prevents endpoint bloat leveraging standard OOP logic:
1. **Controllers (`app/routes/*`)**: APIs enforce authorization bindings, decode raw parameter strings gracefully into strict payload schema (`app.schemas`), and bounce off errors directly.
2. **Services (`app/services/*`)**: Where internal dependencies resolve. Route actions spawn custom entities (e.g. `local_llm_service`, `gemini_service`, or `FrameProcessingService`) routing interactions fluidly. 
3. **Repository Layer**: Core db calls decouple direct SQL actions away from Service models, providing purely object-driven CRUD.

## 12. Database/Storage Configuration
- **Relational Operations**: Everything writes tightly towards PostgreSQL mappings. Configuration binds instantly starting inside `app/db/session.py`.
- **File System Processing**: WebSocket binaries intercept streams to persist temporary raw `.jpg` imagery inside local `./uploads/` when active `session_id` query strings are established.

## 13. Model/Service Loading Pipeline
Machine Learning limits initiate intelligently to preserve thread states:
- `local_llm_service` initializes internal Hugging Face models asynchronously off system Memory utilizing core configurations safely isolated against application reloads.
- Visual processors instantiate dynamically: `FrameProcessingService` loads `optical_analyzer` or `thermal_analyzer` lazily dependent on routing inputs, allowing multi-frame buffers to cascade inference operations efficiently yielding Pydantic models downstream over Websockets.

## 14. Important Conventions, Assumptions, and Implementation Notes
- **WebSocket Pipelining Native**: Due to overhead restrictions, older traditional REST implementations managing binaries (`/sessions/frames`) were intentionally abstracted for native byte captures `await websocket.receive_bytes()`.
- **Global Error Middleware**: System errors propagate dynamically parsing down against specific internal definitions inside `app/core/handlers.py` (i.e. `GeminiServerError`), gracefully outputting formatted strings to Frontend targets.
- **Modular Data Validation**: Standardized strict parameter assertions route universally via `Pydantic` enforcing error prevention natively.

## 15. Troubleshooting and Common Setup Issues
- **Hugging Face Networking Conflicts**: Should the Python script `download_local_llm.py` flag internal connection breaks natively traversing out, configure global variables explicitly using VPN routing strategies.
- **Port 8000 Hangs**: Orphaned active processes limit reboots. Run system `taskkill` (windows), or explicit `kill -9 PID` routines to clear connections locking endpoints gracefully.
- **Schema Conflicts**: Executing `app.init_db.py` will not naturally patch preexisting migrations. Use the explicit backup `migrate_schema.py` natively if table collisions arise.
- **Silent CORS Dropping**: Always authenticate `.env` values accurately tracking strings lacking spacing commas and ensuring absolute root definitions `http://localhost:5173` lacking trailing paths.
