# Stress Companion Backend

> A FastAPI-based backend service for the Stress Companion application, providing real-time AI capabilities, sensor integrations, database management, and more.

## 1. Overview and Purpose

The Stress Companion Backend serves as the robust foundation for the Stress Companion application. It exposes a modern REST API built with FastAPI and is responsible for managing:

- **AI Chat & Interviews**: Integration with Google's Gemini API and a local LLM fallback/question generation service.
- **Sensor Data Processing**: Handling incoming data from optical and thermal sensors (`/api/v1/optical`, `/api/v1/thermal`).
- **User & Session Management**: Secure authentication, user profiling, and tracking of user sessions (`/api/v1/auth`, `/api/v1/sessions`).
- **Database Mapping**: Direct PostgreSQL interactions using SQLAlchemy, structured to handle dynamic user metadata.

## 2. Environment Setup & Prerequisites

Before starting, ensure you have the following installed on your machine:
- **Python 3.9+** (preferably 3.10+ as type hints and modern features are utilized)
- **Git**
- A stable internet connection (for local LLM download and package installation)
- A **Google Gemini API Key** and a **PostgreSQL Database** (e.g., NeonDB) for complete functionality.

## 3. Virtual Environment Creation

We strongly recommend creating a virtual environment to avoid conflicts with system-wide python packages. 

**For Windows:**
```bash
python -m venv venv
# Activate the virtual environment
venv\Scripts\activate
```

**For macOS/Linux:**
```bash
python3 -m venv venv
# Activate the virtual environment
source venv/bin/activate
```

## 4. Dependency Installation

With the virtual environment active, install all required dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```
*Note: This will install FastAPI, SQLAlchemy, Uvicorn, Transformers, PyTorch, Hugging Face Hub, OpenCV, and other essential libraries required for machine learning and web serving.*

## 5. Configuration (.env file)

The project relies on environment variables for configuration. You need to create a `.env` file in the root directory based on the provided `.env.example`.

Create a new file named `.env` and copy the contents of `.env.example` into it. Update the variables accordingly:

### Environment Variables Explanation:

- **`ENVIRONMENT`**: Set to `development` for local testing, or `production` when deployed. Controls things like Swagger UI availability.
- **`ALLOWED_ORIGINS`**: A comma-separated list of URLs allowed to communicate with this backend (CORS). E.g., `http://localhost:5173`. Avoid trailing slashes.
- **`GEMINI_API_KEY`**: Your Google Gemini API Key required for the AI chat companion. (Obtain from Google AI Studio).
- **`PROJECT_NAME`**: Custom string to name the instance in Swagger and Health checks.
- **`GEMINI_MODEL_NAME`**: (Optional) Specific Gemini model to use, defaults generally to `gemini-2.5-flash`.
- **`DATABASE_URL`**: Your PostgreSQL connection string. Typically starts with `postgresql://`. The app was built aiming at NeonDB compatibility.
- **`SECRET_KEY`**: A very secret security key string used for hashing/salting user passwords and session tokens.
- **`DEPRESSION_MODEL_PATH` / `ANXIETY_MODEL_PATH`**: (Optional) Paths to your saved scikit-learn/XGBoost models.
- **`SAMPLE_RATE` / `ANXIETY_N_MFCC`**: (Optional) Audio configurations for Emotion Recognition (SER).
- **`TOTAL_QUESTIONS`**: (Optional) Determines interview length setting.
- **`SER_LOAD_TIMEOUT`**: (Optional) Timeout threshold limit for loading ML Models.

## 6. Downloading Local LLM

The application uses an offline, local LLM (`Qwen/Qwen2.5-0.5B-Instruct` - roughly 1GB in size) for fallback or offline question generation. 

Before running the server smoothly, you should pre-download the model into your HuggingFace cache:

```bash
python app/scripts/download_local_llm.py
```
This script checks if the model is locally cached. If not, it uses `huggingface_hub` or `transformers` to securely pull it and run a quick generation verification test.

## 7. Database Initialization

Once your `DATABASE_URL` is configured in the `.env` file, initialize your database schema by running:

```bash
python -m app.init_db
```
This applies SQLAlchemy defined models across your database. 
*Note: If you are upgrading from an older schema and need to rename the 'curious' column to 'openness', you can run: `python migrate_schema.py`.*

## 8. Execution Steps

With the dependencies installed, database prepared, local LLM cached, and environment variables set, you can launch the backend using Uvicorn.

From the root of the project:

```bash
uvicorn app.main:app --reload
```
Alternatively, as a python module:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- The backend API will be accessible at: `http://localhost:8000`
- API documentation (Swagger UI) is available at: `http://localhost:8000/docs` (NOTE: Auto-disabled in `production` environment).
- Health check available at `http://localhost:8000/health`.

## 9. Troubleshooting & Common Issues

- **Port 8000 already in use:** If the server fails to start, specify a different port: `uvicorn app.main:app --reload --port 8080`
- **Database Connection Failure:** Ensure that your Neon DB or local PostgreSQL URL is properly formatted. Verify that the IP address running your backend is allowed via your Database provider's Firewall setting.
- **CORS Issues on Frontend:** Double-check your `ALLOWED_ORIGINS` in `.env`. Ensure there are absolutely NO spaces near the commas and no trailing slashes at the ends of URLs.
- **PyTorch/Transformers Download Issues:** If the `download_local_llm.py` script fails, check your internet connectivity or whether VPN access restrictions apply to `huggingface.co`. Ensure you have adequate disk space (~1.5GB) available.
