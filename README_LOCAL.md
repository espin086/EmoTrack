# EmoTrack Local Development Guide

This guide will help you run EmoTrack locally on your machine with full camera access, without using Docker.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.8+** installed on your system
- **Webcam** connected and accessible
- **AWS Account** with Rekognition service enabled
- **AWS Credentials** configured (see below)

## AWS Setup

EmoTrack uses AWS Rekognition for emotion detection. You need to configure your AWS credentials:

### Option 1: Using AWS CLI (Recommended)

1. Install AWS CLI:
   ```bash
   # macOS
   brew install awscli
   
   # Or using pip
   pip install awscli
   ```

2. Configure credentials:
   ```bash
   aws configure
   ```
   
   You'll be prompted to enter:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Output format (e.g., `json`)

### Option 2: Using Environment Variables

Set these environment variables in your terminal:

```bash
export AWS_ACCESS_KEY_ID="your_access_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_key_here"
export AWS_DEFAULT_REGION="us-east-1"
```

To make these permanent, add them to your `~/.zshrc` or `~/.bashrc`:

```bash
echo 'export AWS_ACCESS_KEY_ID="your_access_key_here"' >> ~/.zshrc
echo 'export AWS_SECRET_ACCESS_KEY="your_secret_key_here"' >> ~/.zshrc
echo 'export AWS_DEFAULT_REGION="us-east-1"' >> ~/.zshrc
source ~/.zshrc
```

## Installation

### 1. Clone and Navigate to Repository

```bash
git clone https://github.com/espin086/EmoTrack
cd EmoTrack
```

### 2. Run Setup Script

The automated setup script will create a virtual environment and install all dependencies:

```bash
./setup_local.sh
```

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

## Running EmoTrack

You have **two options** for running EmoTrack locally:

### Option 1: Standalone Mode (Recommended for Quick Start)

The simplest way to run EmoTrack with a single command:

```bash
./start_standalone.sh
```

This will:
- Start a single Streamlit application
- Use SQLite database locally
- Open in your browser at `http://localhost:8501`
- Give you full camera access

**Features:**
- ✅ Real-time webcam emotion tracking
- ✅ Daily emotion graphs
- ✅ SQLite database (stored in `emotions.db`)

### Option 2: Full Stack Mode (Backend + Frontend)

For the complete microservices architecture with separate backend and frontend:

**Terminal 1 - Start Backend:**
```bash
./start_backend.sh
```

This starts the FastAPI backend on `http://localhost:8000`

**Terminal 2 - Start Frontend:**
```bash
./start_frontend.sh
```

This starts the Streamlit frontend on `http://localhost:8501`

**Features:**
- ✅ RESTful API backend (FastAPI)
- ✅ Enhanced frontend with more features
- ✅ Emotion summary statistics
- ✅ Data export (JSON/CSV)
- ✅ Advanced analytics
- ✅ API documentation at `http://localhost:8000/docs`

## Using EmoTrack

### 1. Webcam Feed

1. Navigate to `http://localhost:8501` in your browser
2. Select "Webcam Feed" from the sidebar
3. Click "▶️ Start" to begin emotion tracking
4. Your camera will activate and emotions will be detected in real-time
5. Click "⏹️ Stop" when finished

### 2. View Emotion Analytics

- **Display Graph**: View emotion distribution over time with stacked bar charts
- **Emotion Summary**: See overall statistics and pie charts (Full Stack mode only)
- **Export Data**: Download your emotion data as JSON or CSV (Full Stack mode only)

## Camera Permissions

### macOS
You may need to grant camera permissions to your terminal:

1. Go to **System Preferences** → **Security & Privacy** → **Privacy** → **Camera**
2. Enable camera access for your terminal application (Terminal.app or iTerm2)

### Linux
Make sure your user has access to video devices:

```bash
sudo usermod -a -G video $USER
# Log out and back in for changes to take effect
```

## Troubleshooting

### Camera Not Working

**Problem:** "Failed to get frame from webcam"

**Solutions:**
1. Check if camera is being used by another application
2. Verify camera permissions (see above)
3. Try a different camera index in the code (change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`)

### AWS Rekognition Errors

**Problem:** Boto3 credential errors

**Solutions:**
1. Verify AWS credentials are set: `aws configure list`
2. Check IAM permissions include `rekognition:DetectFaces`
3. Verify AWS region is correct

### Port Already in Use

**Problem:** "Address already in use" error

**Solutions:**
```bash
# Find process using port 8501 (Streamlit)
lsof -ti:8501 | xargs kill -9

# Find process using port 8000 (FastAPI)
lsof -ti:8000 | xargs kill -9
```

### Module Not Found Errors

**Problem:** `ModuleNotFoundError` when running

**Solutions:**
1. Make sure virtual environment is activated:
   ```bash
   source venv/bin/activate
   ```
2. Reinstall dependencies:
   ```bash
   pip install -r requirements-local.txt
   ```

## Project Structure

```
EmoTrack/
├── EmoTrack.py              # Standalone Streamlit app
├── backend/
│   ├── app.py               # FastAPI backend
│   └── requirements.txt     # Backend dependencies
├── frontend/
│   ├── app.py               # Streamlit frontend
│   └── requirements.txt     # Frontend dependencies
├── logic/
│   └── facial_analysis.py   # Emotion detection logic
├── data/                    # Database storage (created on first run)
├── requirements-local.txt   # Combined local dependencies
├── setup_local.sh          # Setup script
├── start_standalone.sh     # Start standalone mode
├── start_backend.sh        # Start backend service
└── start_frontend.sh       # Start frontend service
```

## Database

EmoTrack stores emotion data in SQLite:

- **Standalone mode**: `emotions.db` in root directory
- **Full stack mode**: `data/emotions.db`

### Database Schema

```sql
CREATE TABLE emotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL,
    emotion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Documentation

When running in Full Stack mode, the backend provides a RESTful API:

**Swagger UI:** `http://localhost:8000/docs`

### Key Endpoints:

- `POST /detect-emotion` - Detect emotion from image
- `POST /emotions/batch` - Save batch of emotions
- `GET /emotions/daily-stats` - Get daily statistics
- `GET /emotions/summary` - Get overall summary
- `GET /emotions/export` - Export data (JSON/CSV)
- `DELETE /emotions/clear` - Clear all data

## Performance Tips

1. **Reduce CPU usage**: Adjust `FRAME_SAMPLE_RATE` in code (higher = less frequent sampling)
2. **Improve accuracy**: Better lighting and camera positioning
3. **Batch size**: Adjust `BATCH_SIZE` for database write frequency

## Development

### Adding New Emotions

AWS Rekognition detects these emotions:
- HAPPY
- SAD
- ANGRY
- CONFUSED
- DISGUSTED
- SURPRISED
- CALM
- FEAR

To customize emotion handling, edit `logic/facial_analysis.py`

### Modifying the UI

- Standalone: Edit `EmoTrack.py`
- Full Stack: Edit `frontend/app.py`

### Backend Changes

Edit `backend/app.py` to add new API endpoints or modify emotion processing.

## Deactivating Virtual Environment

When you're done:

```bash
deactivate
```

## Additional Resources

- [AWS Rekognition Documentation](https://docs.aws.amazon.com/rekognition/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenCV Documentation](https://docs.opencv.org/)

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs in the terminal
3. Open an issue on GitHub: https://github.com/espin086/EmoTrack/issues

## License

MIT License - See LICENSE file for details.

---

**Happy Emotion Tracking! 🎭😊**

