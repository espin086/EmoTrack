# ✅ EmoTrack Local Setup - Ready to Run!

Your EmoTrack application is now set up for local development with full camera access!

## 📦 What's Been Set Up

### New Files Created:

1. **requirements-local.txt** - Combined dependencies for local development
2. **setup_local.sh** - Automated setup script (executable)
3. **start_backend.sh** - Start backend API (executable)
4. **start_frontend.sh** - Start frontend UI (executable)
5. **start_standalone.sh** - Start standalone mode (executable)
6. **Makefile** - Convenient make commands
7. **QUICKSTART.md** - Quick start guide
8. **README_LOCAL.md** - Comprehensive local development guide

### Updated Files:

- **README.md** - Added quick start section linking to local development

## 🚀 How to Run (Quick Reference)

### First Time Setup:

```bash
cd /Users/jjespinoza/Documents/PersonalGitHub/EmoTrack

# 1. Run setup (one time only)
./setup_local.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Configure AWS (if not already done)
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### Running the Application:

**Option 1: Standalone (Recommended for Quick Start)**
```bash
source venv/bin/activate
./start_standalone.sh
```
→ Opens at http://localhost:8501

**Option 2: Full Stack (More Features)**

Terminal 1:
```bash
source venv/bin/activate
./start_backend.sh
```

Terminal 2:
```bash
source venv/bin/activate
./start_frontend.sh
```
→ Frontend: http://localhost:8501
→ API Docs: http://localhost:8000/docs

## 🎯 Using Make Commands

We've also added a Makefile for convenience:

```bash
make help              # Show all available commands
make setup             # Create virtual environment
make install           # Install dependencies
make start-standalone  # Start standalone mode
make start-backend     # Start backend
make start-frontend    # Start frontend
make stop              # Stop all services
make check-aws         # Verify AWS credentials
make camera-test       # Test camera access
make status            # Check service status
make clean             # Remove venv and cache files
```

## 📋 Project Structure

```
EmoTrack/
├── 🎭 EmoTrack.py              # Standalone app (simplest option)
│
├── backend/                    # FastAPI backend
│   ├── app.py                  # API endpoints
│   └── requirements.txt
│
├── frontend/                   # Streamlit frontend
│   ├── app.py                  # UI application
│   └── requirements.txt
│
├── logic/
│   └── facial_analysis.py     # Emotion detection logic
│
├── 📝 Documentation
│   ├── README.md              # Main project README
│   ├── README_LOCAL.md        # Local development guide (detailed)
│   ├── README_DOCKER.md       # Docker deployment guide
│   ├── QUICKSTART.md          # Quick start instructions
│   └── LOCAL_SETUP_COMPLETE.md # This file
│
├── 🔧 Setup Scripts
│   ├── setup_local.sh         # Initial setup
│   ├── start_standalone.sh    # Start standalone mode
│   ├── start_backend.sh       # Start backend
│   └── start_frontend.sh      # Start frontend
│
├── Makefile                    # Make commands
└── requirements-local.txt      # Local dependencies

```

## 🎥 Camera Access

### macOS Camera Permissions:
1. System Preferences → Security & Privacy → Privacy → Camera
2. Enable camera for your terminal (Terminal.app or iTerm2)
3. Restart terminal if needed

### Test Camera:
```bash
make camera-test
# Or manually:
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Camera OK!' if cap.read()[0] else '❌ Failed'); cap.release()"
```

## 🔐 AWS Configuration

EmoTrack requires AWS Rekognition. Configure credentials:

### Method 1: Environment Variables (Quick)
```bash
export AWS_ACCESS_KEY_ID="your_access_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_key_here"
export AWS_DEFAULT_REGION="us-east-1"
```

### Method 2: AWS CLI (Permanent)
```bash
aws configure
# Enter your credentials when prompted
```

### Verify:
```bash
make check-aws
```

## 🎨 Features Available

### Standalone Mode:
- ✅ Real-time webcam emotion tracking
- ✅ Daily emotion variation graphs
- ✅ SQLite database storage
- ✅ Simple one-process deployment

### Full Stack Mode (Additional Features):
- ✅ RESTful API backend (FastAPI)
- ✅ API documentation (Swagger UI)
- ✅ Emotion summary statistics
- ✅ Pie chart visualizations
- ✅ Data export (JSON/CSV)
- ✅ Advanced analytics
- ✅ Batch emotion processing

## 🐛 Troubleshooting

### Port Already in Use:
```bash
make stop
# Or manually:
lsof -ti:8501 | xargs kill -9  # Frontend
lsof -ti:8000 | xargs kill -9  # Backend
```

### Camera Not Working:
- Close other apps using camera (Zoom, Skype, etc.)
- Check camera permissions
- Try `make camera-test`

### AWS Errors:
- Verify credentials: `make check-aws`
- Ensure Rekognition is enabled in your AWS region
- Check IAM permissions include `rekognition:DetectFaces`

### Module Not Found:
```bash
source venv/bin/activate
make install
```

## 📊 Database Management

### Backup Database:
```bash
make db-backup
```

### Clear All Data (Warning!):
```bash
make db-clear
```

### Database Locations:
- Standalone: `emotions.db` (root directory)
- Full Stack: `data/emotions.db`

## 🔄 Development Workflow

```bash
# Start development
source venv/bin/activate

# Run in dev mode (auto-reload)
make dev

# Check status
make status

# Stop when done
make stop
```

## 📚 Next Steps

1. **Start the application** using one of the methods above
2. **Allow camera permissions** when prompted
3. **Click "Webcam Feed"** in the sidebar
4. **Press "▶️ Start"** to begin tracking
5. **View graphs** to see emotion trends over time

## 🆘 Getting Help

- **Quick Start**: See `QUICKSTART.md`
- **Detailed Guide**: See `README_LOCAL.md`
- **Main README**: See `README.md`
- **API Docs**: http://localhost:8000/docs (when backend running)
- **Issues**: https://github.com/espin086/EmoTrack/issues

## ⚡ Quick Commands Cheat Sheet

```bash
# Setup (one time)
./setup_local.sh && source venv/bin/activate

# Run standalone
./start_standalone.sh

# Run full stack
./start_backend.sh      # Terminal 1
./start_frontend.sh     # Terminal 2

# Using Make
make start-standalone   # Standalone mode
make start-backend      # Backend only
make start-frontend     # Frontend only
make stop               # Stop all
make status             # Check what's running
make check-aws          # Verify AWS config
make camera-test        # Test camera
```

---

## 🎉 You're All Set!

Everything is configured and ready to go. Just run:

```bash
source venv/bin/activate
./start_standalone.sh
```

Then open http://localhost:8501 and start tracking emotions! 🎭😊

---

**Questions?** Check the detailed guides or open an issue on GitHub.

**Enjoying EmoTrack?** Star the repo and share with others!

