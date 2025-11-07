# EmoTrack: Real-Time Emotion Tracking Application

<a href="https://buymeacoffee.com/jjespinozag" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174">
</a>

EmoTrack is a real-time emotion tracking application that utilizes facial recognition to capture emotions from a webcam feed. Built with Python, Streamlit, FastAPI, and AWS Rekognition, it provides both standalone and microservices architectures for flexible deployment.

## 🎯 Features

### Real-Time Emotion Detection
![Happy Emotion Detection](./images/ui_happy.png)
![Angry Emotion Detection](./images/ui_angry.png)

### Daily Emotion Analytics
![ui_new_metrics](./images/ui_metrics.png)

### Key Capabilities
- ✅ **Real-time webcam emotion tracking** with AWS Rekognition
- ✅ **Daily emotion variation graphs** with trend analysis
- ✅ **Multiple deployment options** (Standalone, Full Stack, Docker)
- ✅ **RESTful API** with FastAPI backend
- ✅ **Data export** (JSON/CSV formats)
- ✅ **Emotion statistics** with pie charts and visualizations
- ✅ **SQLite database** for persistent storage
- ✅ **Modern UI** built with Streamlit

### Supported Emotions
- HAPPY 😊
- SAD 😢
- ANGRY 😠
- SURPRISED 😲
- CONFUSED 😕
- DISGUSTED 🤢
- CALM 😌
- FEAR 😨

---

## 🏗️ Architecture

### Standalone Mode
```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  Streamlit App  │────▶│ AWS Rekognition │
│  (All-in-One)   │     │                 │
│                 │     └─────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SQLite DB     │
└─────────────────┘
```

### Full Stack / Docker Mode
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
                        │   SQLite DB     │
                        │   (Volume)      │
                        └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (for local setup) OR Docker & Docker Compose
- AWS account with Rekognition service enabled
- Webcam

### Option 1: Local Setup (Recommended for Camera Access)

**Step 1: Clone and Setup**
```bash
git clone https://github.com/espin086/EmoTrack
cd EmoTrack
./setup_local.sh
```

**Step 2: Configure AWS**
```bash
# Option A: Environment variables
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"

# Option B: AWS CLI
aws configure
```

**Step 3: Run Application**
```bash
source venv/bin/activate
./start_standalone.sh
```

Open **http://localhost:8501** and start tracking! 🎉

### Option 2: Docker Setup

```bash
git clone https://github.com/espin086/EmoTrack
cd EmoTrack

# Configure AWS credentials in .env
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker-compose up --build
```

Access:
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

---

## 📦 Installation

### Local Development Setup

#### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements-local.txt
```

#### 3. Configure AWS Credentials

**Method 1: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your_access_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_key_here"
export AWS_DEFAULT_REGION="us-east-1"

# Make permanent (macOS/Linux)
echo 'export AWS_ACCESS_KEY_ID="your_access_key"' >> ~/.zshrc
echo 'export AWS_SECRET_ACCESS_KEY="your_secret_key"' >> ~/.zshrc
echo 'export AWS_DEFAULT_REGION="us-east-1"' >> ~/.zshrc
source ~/.zshrc
```

**Method 2: AWS CLI (Recommended)**
```bash
# Install AWS CLI
brew install awscli  # macOS
# or
pip install awscli

# Configure
aws configure
```

Enter when prompted:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., `us-east-1`)
- Default output format (e.g., `json`)

### Docker Setup

#### 1. Install Docker
- **macOS/Windows**: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)

#### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

#### 3. Run with Docker Compose
```bash
docker-compose up --build
```

---

## 🎮 Usage

### Running Locally

#### Standalone Mode (Simplest)
Perfect for personal use, single process:

```bash
source venv/bin/activate
./start_standalone.sh
# OR
streamlit run EmoTrack.py
```

**Features:**
- Real-time webcam tracking
- Daily emotion graphs
- SQLite storage
- Opens at http://localhost:8501

#### Full Stack Mode (Advanced)
Separate backend and frontend for development:

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
./start_backend.sh
# OR
cd backend && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
source venv/bin/activate
./start_frontend.sh
# OR
cd frontend && BACKEND_URL=http://localhost:8000 streamlit run app.py
```

**Features:**
- All standalone features +
- RESTful API
- API documentation
- Emotion summaries
- Data export (JSON/CSV)
- Advanced analytics

### Running with Docker

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using the Application

1. **Open** http://localhost:8501 in your browser
2. **Navigate** to "Webcam Feed" in the sidebar
3. **Click** "▶️ Start" button
4. **Allow** camera permissions when prompted
5. **Watch** real-time emotion detection
6. **Click** "⏹️ Stop" when finished
7. **View** "Display Graph" for emotion trends

---

## ⚙️ Make Commands

We provide convenient Make commands for common tasks:

```bash
make help              # Show all available commands
make setup             # Create virtual environment
make install           # Install dependencies
make start-standalone  # Start standalone mode
make start-backend     # Start backend only
make start-frontend    # Start frontend only
make stop              # Stop all services
make dev               # Start both backend and frontend with auto-reload

# Utilities
make check-aws         # Verify AWS credentials
make camera-test       # Test camera access
make status            # Check if services are running
make clean             # Remove venv and cache files

# Database
make db-backup         # Backup emotions database
make db-clear          # Clear all emotion data (with confirmation)

# Development
make test              # Run tests
make lint              # Run linters
make format            # Format code with black
```

---

## 🎥 Camera Access

### macOS
Grant camera permissions to your terminal:
1. **System Preferences** → **Security & Privacy** → **Privacy** → **Camera**
2. Enable for Terminal.app or iTerm2
3. Restart terminal if needed

### Linux
Grant user access to video devices:
```bash
sudo usermod -a -G video $USER
# Log out and back in
```

### Test Camera
```bash
make camera-test
# OR
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Camera OK!' if cap.read()[0] else '❌ Failed'); cap.release()"
```

---

## 📡 API Documentation

When running in Full Stack or Docker mode, the backend provides a RESTful API.

### Endpoints

#### Emotion Detection
```bash
POST /detect-emotion
```
Upload an image and detect emotion.

#### Batch Save
```bash
POST /emotions/batch
```
Save multiple emotion records at once.

#### Daily Statistics
```bash
GET /emotions/daily-stats?days=7
```
Get emotion statistics for the last N days.

#### Summary
```bash
GET /emotions/summary
```
Get overall emotion distribution and statistics.

#### Export Data
```bash
GET /emotions/export?format=json
GET /emotions/export?format=csv
```
Export all emotion data.

#### Clear Data
```bash
DELETE /emotions/clear?confirm=true
```
Delete all emotion records (requires confirmation).

#### Health Check
```bash
GET /health
```
Check API and database health.

### Interactive Documentation

Access interactive API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example Usage

```bash
# Check API health
curl http://localhost:8000/health

# Get daily stats
curl http://localhost:8000/emotions/daily-stats?days=7

# Export data as JSON
curl http://localhost:8000/emotions/export?format=json > emotions.json
```

---

## 🐛 Troubleshooting

### Camera Issues

**Problem:** "Failed to get frame from webcam"

**Solutions:**
1. Check if another app is using the camera
2. Grant camera permissions (see Camera Access section)
3. Try different camera index:
   ```python
   # In code, change from:
   cv2.VideoCapture(0)
   # To:
   cv2.VideoCapture(1)  # or 2, 3, etc.
   ```
4. On macOS, restart terminal after granting permissions

### AWS Rekognition Errors

**Problem:** Boto3 credential errors or "Unable to locate credentials"

**Solutions:**
1. Verify credentials are set:
   ```bash
   aws configure list
   # OR
   make check-aws
   ```
2. Check IAM permissions include `rekognition:DetectFaces`
3. Verify AWS region is correct
4. Test AWS connection:
   ```bash
   aws rekognition describe-projects --region us-east-1
   ```

### Port Already in Use

**Problem:** "Address already in use" on port 8501 or 8000

**Solutions:**
```bash
# Stop all EmoTrack services
make stop

# OR manually kill processes
lsof -ti:8501 | xargs kill -9  # Frontend
lsof -ti:8000 | xargs kill -9  # Backend

# On Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

### Module Not Found

**Problem:** `ModuleNotFoundError` when running

**Solutions:**
1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Reinstall dependencies:
   ```bash
   make install
   # OR
   pip install -r requirements-local.txt
   ```

### Docker Issues

**Problem:** Webcam not accessible in Docker

**Solution:**
Docker has limitations with webcam access. Use local setup instead:
```bash
./setup_local.sh
source venv/bin/activate
./start_standalone.sh
```

**Problem:** Backend connection issues

**Solutions:**
```bash
# Check backend health
curl http://localhost:8000/health

# View backend logs
docker-compose logs backend

# Restart services
docker-compose restart
```

### Database Issues

**Problem:** Database locked or corrupted

**Solutions:**
```bash
# Backup current database
make db-backup

# Clear and restart
make db-clear

# Restart application
make stop
make start-standalone
```

---

## 📁 Project Structure

```
EmoTrack/
├── EmoTrack.py                 # Standalone Streamlit application
│
├── backend/                    # FastAPI backend service
│   ├── app.py                 # API endpoints and logic
│   ├── requirements.txt       # Backend dependencies
│   ├── test_api.py           # API tests
│   └── Dockerfile            # Backend container
│
├── frontend/                   # Streamlit frontend service
│   ├── app.py                 # UI application
│   ├── requirements.txt       # Frontend dependencies
│   └── Dockerfile            # Frontend container
│
├── logic/
│   └── facial_analysis.py     # Emotion detection logic
│
├── images/                     # UI screenshots
│   ├── ui_happy.png
│   ├── ui_angry.png
│   └── ...
│
├── data/                       # Database storage (Full Stack mode)
│   └── emotions.db
│
├── Setup Scripts
│   ├── setup_local.sh         # Automated local setup
│   ├── start_standalone.sh    # Start standalone mode
│   ├── start_backend.sh       # Start backend service
│   └── start_frontend.sh      # Start frontend service
│
├── Configuration
│   ├── requirements.txt       # Original combined requirements
│   ├── requirements-local.txt # Local development requirements
│   ├── docker-compose.yml     # Docker orchestration
│   ├── Makefile              # Make commands
│   └── .env.example          # Environment variables template
│
├── Documentation
│   ├── README.md             # This file
│   └── migrate_data.py       # Database migration script
│
└── Database Files
    └── emotions.db           # SQLite database (Standalone mode)
```

---

## 💾 Database

### Schema

```sql
CREATE TABLE emotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL,
    emotion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Locations
- **Standalone mode**: `emotions.db` (root directory)
- **Full Stack mode**: `data/emotions.db`
- **Docker mode**: `data/emotions.db` (mounted volume)

### Management

**Backup Database:**
```bash
make db-backup
# Creates: backups/emotions_YYYYMMDD_HHMMSS.db
```

**Clear Database:**
```bash
make db-clear
# Requires confirmation
```

**Manual Backup:**
```bash
cp emotions.db backups/emotions_$(date +%Y%m%d_%H%M%S).db
```

**View Data:**
```bash
sqlite3 emotions.db "SELECT * FROM emotions ORDER BY timestamp DESC LIMIT 10;"
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# AWS Configuration (Required)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Backend Configuration (Full Stack mode)
BACKEND_URL=http://localhost:8000
DB_PATH=./data/emotions.db

# Optional
LOG_LEVEL=INFO
```

### Application Settings

**Adjust frame sampling rate** (in `EmoTrack.py` or `frontend/app.py`):
```python
FRAME_SAMPLE_RATE = 24  # Sample every 24th frame (higher = less CPU)
BATCH_SIZE = 60         # Number of emotions to batch before saving
```

**Change camera index** (if you have multiple cameras):
```python
cv2.VideoCapture(0)  # Change 0 to 1, 2, etc.
```

---

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
pytest test_api.py -v

# Using make
make test
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking (if using mypy)
mypy backend/app.py
```

### Adding New Features

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `make test`
5. **Commit**: `git commit -m 'Add amazing feature'`
6. **Push**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Guidelines
1. Follow PEP 8 style guide
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Keep commits atomic and well-described

---

## 📄 License

MIT License

Copyright (c) 2024 EmoTrack

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 📞 Support

- **Issues**: https://github.com/espin086/EmoTrack/issues
- **Discussions**: https://github.com/espin086/EmoTrack/discussions
- **Email**: For private inquiries

---

## 🙏 Acknowledgments

- **AWS Rekognition** for emotion detection capabilities
- **Streamlit** for the amazing UI framework
- **FastAPI** for the high-performance API framework
- **OpenCV** for video processing
- All contributors and users of EmoTrack

---

## ⚡ Quick Reference

### Commands Cheat Sheet

```bash
# Setup (one time)
./setup_local.sh && source venv/bin/activate

# Run standalone
./start_standalone.sh                    # http://localhost:8501

# Run full stack
./start_backend.sh                       # Terminal 1
./start_frontend.sh                      # Terminal 2

# Using Make
make start-standalone                    # Standalone mode
make dev                                 # Full stack with auto-reload
make stop                                # Stop all services
make status                              # Check service status
make check-aws                           # Verify AWS config
make camera-test                         # Test camera

# Docker
docker-compose up --build                # Build and run
docker-compose down                      # Stop and remove containers
docker-compose logs -f                   # Follow logs
```

---

**Happy Emotion Tracking! 🎭😊**

Made with ❤️ by the EmoTrack team
