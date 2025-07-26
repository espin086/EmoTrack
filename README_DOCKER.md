# EmoTrack - Dockerized Version

This is the refactored version of EmoTrack with separate backend (FastAPI) and frontend (Streamlit) services running in Docker containers.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Streamlit UI   │────▶│  FastAPI Backend│────▶│ AWS Rekognition │
│   (Frontend)    │     │     (API)       │     │                 │
│                 │     │                 │     └─────────────────┘
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │  SQLite DB      │
                        │  (Volume)       │
                        │                 │
                        └─────────────────┘
```

## Features

### Frontend (Streamlit)
- Real-time webcam emotion tracking
- Emotion variation graphs
- Summary statistics
- Data export (JSON/CSV)
- Clean, modern UI

### Backend (FastAPI)
- `/detect-emotion` - Detect emotion from uploaded image
- `/emotions/batch` - Save batch of emotions
- `/emotions/daily-stats` - Get daily emotion statistics
- `/emotions/summary` - Get overall emotion summary
- `/emotions/export` - Export emotion data
- `/emotions/clear` - Clear all emotion data
- `/health` - Health check endpoint

## Prerequisites

- Docker and Docker Compose installed
- AWS account with Rekognition service enabled
- Webcam connected to your system

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/EmoTrack
   cd EmoTrack
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

### Running locally without Docker

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### Project Structure

```
EmoTrack/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── requirements.txt    # Backend dependencies
│   └── Dockerfile         # Backend container
├── frontend/
│   ├── app.py             # Streamlit application
│   ├── requirements.txt   # Frontend dependencies
│   └── Dockerfile        # Frontend container
├── data/                  # SQLite database volume
├── docker-compose.yml     # Container orchestration
├── .env.example          # Environment variables template
└── README_DOCKER.md      # This file
```

## Configuration

### Environment Variables

- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_DEFAULT_REGION` - AWS region (default: us-east-1)

### Webcam Access

For Linux systems, the docker-compose file includes device mapping for `/dev/video0`. 

For other systems, you may need to adjust the device mapping or use alternative methods for webcam access in containers.

## Troubleshooting

### Webcam not working in container
- Ensure your webcam is connected and accessible
- Check device permissions
- For Linux: `sudo chmod 666 /dev/video0`

### Backend connection issues
- Check if backend is healthy: `curl http://localhost:8000/health`
- View logs: `docker-compose logs backend`

### AWS Rekognition errors
- Verify AWS credentials in `.env` file
- Check AWS region settings
- Ensure Rekognition service is enabled in your AWS account

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

## License

MIT License