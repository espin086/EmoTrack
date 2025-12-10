# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

EmoTrack is a dual-mode emotion detection system that uses AWS Rekognition to analyze facial expressions from webcam feeds. It can run as either a monolithic standalone Streamlit app or as a microservices architecture with separated FastAPI backend and Streamlit frontend.

## Development Commands

### Setup
```bash
# One-time setup
./setup_local.sh
source venv/bin/activate

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-local.txt
```

### Running the Application

**Standalone Mode (Recommended for Development):**
```bash
make start-standalone
# OR: streamlit run EmoTrack.py
```
- All-in-one application on port 8501
- Database: `./emotions.db`
- Direct camera access (no Docker limitations)
- Auto-reloads on file changes (click "Always rerun" in Streamlit)

**Full Stack Mode (For API Development):**
```bash
# Development mode with auto-reload (parallel)
make dev

# Or separately in two terminals:
make start-backend   # Port 8000, auto-reloads with --reload flag
make start-frontend  # Port 8501, auto-reloads on file save
```
- Backend: FastAPI on port 8000 with `/docs` for API testing
- Frontend: Streamlit on port 8501
- Database: `./data/emotions.db`
- Backend URL: `http://localhost:8000`

**Docker Mode:**
```bash
docker-compose up --build
# Note: Webcam access only works on Linux
```

### Testing
```bash
# Backend API tests
cd backend && pytest test_api.py -v

# Or with make
make test
```

### Utilities
```bash
make status          # Check which services are running
make stop            # Kill all EmoTrack processes on ports 8000/8501
make check-aws       # Verify AWS credentials are configured
make camera-test     # Test webcam access
make db-backup       # Backup emotions database
make db-clear        # Delete all emotion data (with confirmation)
```

## Architecture & Key Concepts

### Dual-Mode Design

The codebase supports three deployment modes from a single repository:

1. **Standalone (`EmoTrack.py`)**: Monolithic Streamlit app with all logic embedded
2. **Full Stack (`backend/app.py` + `frontend/app.py`)**: Microservices communicating via REST API
3. **Docker**: Containerized version of Full Stack mode

### Core Data Flow

```
Webcam → Frame Sampling (1 in 24) → JPEG Encoding →
AWS Rekognition → Emotion Detection → Batch Buffer (60 emotions) →
SQLite Database → Analytics/Visualization
```

**Key Performance Patterns:**
- **Frame sampling**: Only processes every 24th frame to reduce AWS API calls (cost optimization)
- **Batch processing**: Collects 60 emotions in memory before database write (60x fewer I/O operations)
- **Session state**: Uses `st.session_state` to maintain buffer and running status across Streamlit reruns

### Facial Detection Logic

The emotion detection is isolated in `logic/facial_analysis.py` with a single function:
```python
detect_emotion(frame) -> str
```
- Encodes frame as JPEG bytes
- Calls AWS Rekognition's `detect_faces()` with EMOTIONS attribute
- Returns highest-confidence emotion or "NO FACE"
- Used by both standalone and backend modes

### Database Schema

```sql
CREATE TABLE emotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL,                -- Unix timestamp (float)
    emotion TEXT,                  -- One of 8 emotions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Supported Emotions**: HAPPY, SAD, ANGRY, SURPRISED, CONFUSED, DISGUSTED, CALM, FEAR

**Database Locations:**
- Standalone: `./emotions.db`
- Full Stack: `./data/emotions.db`
- Docker: `/app/data/emotions.db` (volume mounted)

### API Endpoints (Full Stack Mode)

When modifying the backend API (`backend/app.py`), key endpoints are:

- `POST /detect-emotion` - Upload frame, returns emotion
- `POST /emotions/batch` - Save multiple emotion records
- `GET /emotions/daily-stats?days=N` - Daily emotion distribution
- `GET /emotions/summary` - Overall statistics and percentages
- `GET /emotions/export?format=json|csv` - Export all data
- `DELETE /emotions/clear?confirm=true` - Delete all records
- `GET /health` - Health check (database + service status)

Interactive docs at `http://localhost:8000/docs`

### Frontend-Backend Communication

The Full Stack frontend (`frontend/app.py`) communicates with backend via:
- Environment variable `BACKEND_URL` (defaults to `http://backend:8000` for Docker)
- Health check with 60-second cache: `@st.cache_data(ttl=60)`
- File uploads for emotion detection: multipart form-data with JPEG bytes
- Error handling with `requests.raise_for_status()`

## Important Patterns

### Session State Management
```python
# Required pattern for maintaining state across Streamlit reruns
if "emotions_batch" not in st.session_state:
    st.session_state.emotions_batch = []
```

### Database Context Manager
```python
# Backend pattern for database access
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables dict-like access
    try:
        yield conn
    finally:
        conn.close()
```

### Error Handling
- AWS calls are wrapped in try/except with logging
- Backend raises `HTTPException` with appropriate status codes
- Frontend displays errors with `st.error()` and continues gracefully
- "NO FACE" is returned instead of exceptions when no face detected

### Configuration
- AWS credentials: Environment variables or `~/.aws/credentials` (AWS SDK standard)
- No `.env` file in repo; use `.env.example` as template
- Constants defined at module level: `FRAME_SAMPLE_RATE`, `BATCH_SIZE`, `DB_PATH`

## Testing Guidelines

When adding tests to `backend/test_api.py`:
- Use `TestClient` from FastAPI for endpoint testing
- Mock AWS Rekognition calls to avoid real API charges
- Test both success and error cases
- Verify response status codes and JSON structure
- Clean up test data after tests complete

## Known Limitations

1. **SQLite in Full Stack**: Single-process only; doesn't scale for concurrent users. For production, migrate to PostgreSQL/MySQL.

2. **No API Authentication**: Backend has CORS open to all origins. Add JWT or API keys for production.

3. **Frame Sampling Trade-off**: Processing 1 in 24 frames means emotions between samples are missed. Adjust `FRAME_SAMPLE_RATE` for different accuracy/cost balance.

4. **Batch Buffer**: 60-emotion buffer held in memory could lose data on crash. Consider more frequent syncs for critical applications.

5. **Docker Webcam**: Camera access only works on Linux containers. macOS/Windows users should use local setup.

## File Structure Guide

**Core Application Files:**
- `EmoTrack.py` - Standalone monolithic app (212 lines)
- `backend/app.py` - FastAPI backend (304 lines)
- `frontend/app.py` - Streamlit frontend for Full Stack mode (389 lines)
- `logic/facial_analysis.py` - AWS Rekognition integration (29 lines)

**Configuration:**
- `requirements-local.txt` - Combined dependencies for local development
- `backend/requirements.txt` - Backend-only dependencies
- `frontend/requirements.txt` - Frontend-only dependencies
- `docker-compose.yml` - Container orchestration with health checks

**Scripts:**
- `setup_local.sh` - Automated local environment setup
- `start_standalone.sh` - Launch standalone mode
- `start_backend.sh` - Launch FastAPI backend
- `start_frontend.sh` - Launch Streamlit frontend
- `Makefile` - Convenience commands for all operations

**Utilities:**
- `migrate_data.py` - Database schema migration tool
- `backend/test_api.py` - API integration tests

## AWS Rekognition Integration

The application requires AWS credentials with `rekognition:DetectFaces` permission:
```bash
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"
```

Or configure via AWS CLI: `aws configure`

Each API call to Rekognition incurs cost (~$0.001 per image). Frame sampling reduces this by 24x.

## Adding New Features

**New Emotion Types:**
1. AWS Rekognition supports the 8 emotions listed above (API limitation)
2. To add custom emotions, you'd need to train a custom ML model

**New Analytics:**
1. Add SQL query in `backend/app.py`
2. Create new endpoint or expand existing `/emotions/summary`
3. Add visualization in `frontend/app.py` or `EmoTrack.py`
4. Use pandas for data manipulation, matplotlib for charts

**New API Endpoints:**
1. Define Pydantic models for request/response validation
2. Add endpoint function with appropriate HTTP method decorator
3. Use `get_db()` context manager for database operations
4. Update `backend/test_api.py` with new test cases
5. Frontend can call via `requests.get/post(f"{BACKEND_URL}/endpoint")`

## Troubleshooting

**Camera Issues:**
- Verify permissions: System Preferences → Security & Privacy → Camera
- Test camera: `make camera-test`
- Try different camera index: Change `cv2.VideoCapture(0)` to `VideoCapture(1)`

**AWS Issues:**
- Verify credentials: `make check-aws` or `aws configure list`
- Test connection: `aws rekognition describe-projects --region us-east-1`

**Port Conflicts:**
- Stop services: `make stop`
- Or manually: `lsof -ti:8501 | xargs kill -9`

**Module Not Found:**
- Activate venv: `source venv/bin/activate`
- Reinstall: `make install`
