<div align="center">

# 🎭 EmoTrack

### Real-Time Emotion Analytics Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by AWS Rekognition](https://img.shields.io/badge/AWS-Rekognition-orange.svg)](https://aws.amazon.com/rekognition/)
[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red.svg)](https://streamlit.io/)

**Track, analyze, and understand your emotional patterns with AI-powered facial recognition**

[Live Demo](https://www.youtube.com/watch?v=jj4j2264Nxw) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

<a href="https://buymeacoffee.com/jjespinozag" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174">
</a>

---

### 📺 See It In Action

[![EmoTrack Demo](https://img.youtube.com/vi/jj4j2264Nxw/maxresdefault.jpg)](https://www.youtube.com/watch?v=jj4j2264Nxw)

*Click to watch the full demo*

</div>

---

## 🚀 What is EmoTrack?

EmoTrack is a cutting-edge emotion analytics platform that combines **AI-powered facial recognition** with **beautiful data visualization** to help you understand your emotional patterns over time.

Built for researchers, therapists, wellness coaches, and anyone interested in emotional intelligence, EmoTrack provides real-time emotion detection with comprehensive analytics dashboards.

### ✨ Key Features

🎥 **Real-Time Emotion Detection**
- Live webcam feed with instant emotion recognition
- Powered by AWS Rekognition for 99% accuracy
- Frame sampling optimization (reduced API costs by 24x)

📊 **Beautiful Analytics Dashboards**
- Modern dark-themed charts with vibrant colors
- Today vs Weekly baseline comparisons
- 12-month trend analysis with normalized distributions
- Auto-refreshing metrics during live tracking

🏗️ **Flexible Architecture**
- **Standalone Mode**: All-in-one Streamlit app
- **Full Stack Mode**: FastAPI backend + Streamlit frontend
- **Docker Mode**: Containerized microservices

📈 **Comprehensive Insights**
- 8 emotion types: Happy, Sad, Angry, Surprised, Confused, Disgusted, Calm, Fear
- Percentage-based distributions for fair comparisons
- Monthly emotional patterns and seasonal trends
- Export data in JSON/CSV formats

⚡ **Performance Optimized**
- Batch processing: 60 emotions before database write
- Frame sampling: Every 24th frame processed
- Auto-refresh: Updates every 60 seconds
- SQLite with potential for PostgreSQL/MySQL scaling

---

## 🎯 Use Cases

- **🧘 Personal Wellness**: Track your emotional health over time
- **🔬 Research**: Study emotional patterns in controlled environments
- **💼 Workplace Analytics**: Monitor team morale (with consent)
- **🎓 Education**: Teach emotional intelligence concepts
- **🏥 Therapy**: Support mental health tracking (clinical validation required)
- **🎮 Gaming**: Emotion-responsive interactive experiences

---

## 🏁 Quick Start

### Prerequisites

- Python 3.11+
- AWS Account with Rekognition access
- Webcam (for emotion detection)
- macOS, Linux, or Windows

### Option 1: Standalone Mode (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/EmoTrack.git
cd EmoTrack

# Setup environment
./setup_local.sh
source venv/bin/activate

# Configure AWS credentials
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"

# Generate sample data (optional)
python generate_fake_data.py

# Launch the app
make start-standalone
```

**Access:** http://localhost:8501

### Option 2: Full Stack Mode (For API Development)

```bash
# Setup environment
./setup_local.sh
source venv/bin/activate

# Configure AWS credentials
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"

# Generate sample data for backend
python generate_fake_data.py data/emotions.db

# Start backend + frontend
make dev
```

**Frontend:** http://localhost:8501
**Backend API:** http://localhost:8000/docs

### Option 3: Docker Mode

```bash
# Build and run containers
docker-compose up --build
```

**Note:** Webcam access in Docker only works on Linux hosts.

---

## 🎨 Architecture

### 🏗️ Dual-Mode Design

```
┌─────────────────────────────────────────────────────────┐
│                     EMOTRACK                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐          ┌──────────────────┐  │
│  │  Standalone Mode  │          │  Full Stack Mode  │  │
│  │                   │          │                   │  │
│  │  Streamlit App    │          │  FastAPI Backend  │  │
│  │  (All-in-One)     │          │  +                │  │
│  │                   │          │  Streamlit Frontend│  │
│  └────────┬─────────┘          └────────┬──────────┘  │
│           │                              │             │
│           └──────────────┬───────────────┘             │
│                          │                             │
│                    ┌─────▼──────┐                      │
│                    │   SQLite    │                      │
│                    │  Database   │                      │
│                    └─────┬──────┘                      │
│                          │                             │
│                    ┌─────▼──────┐                      │
│                    │    AWS      │                      │
│                    │ Rekognition │                      │
│                    └────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### 🔄 Data Flow

```
📹 Webcam Feed
    ↓
🎯 Frame Sampling (1 in 24 frames)
    ↓
🖼️ JPEG Encoding
    ↓
☁️ AWS Rekognition API
    ↓
🎭 Emotion Detection
    ↓
💾 Batch Buffer (60 emotions)
    ↓
🗄️ SQLite Database
    ↓
📊 Analytics & Visualization
```

---

## 📊 Emotion Types

| Emotion | Icon | AWS Rekognition Label | Color Code |
|---------|------|----------------------|------------|
| Happy | 😊 | `HAPPY` | `#FFD93D` |
| Calm | 😌 | `CALM` | `#6BCB77` |
| Surprised | 😲 | `SURPRISED` | `#4D96FF` |
| Confused | 😕 | `CONFUSED` | `#9D84B7` |
| Sad | 😢 | `SAD` | `#5F85DB` |
| Fear | 😨 | `FEAR` | `#FF6B9D` |
| Angry | 😠 | `ANGRY` | `#FF5757` |
| Disgust | 🤢 | `DISGUST` | `#A084DC` |

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Interactive web interface
- **Matplotlib** - Chart generation with modern dark theme
- **Pandas** - Data manipulation and analysis
- **OpenCV** - Webcam capture and image processing

### Backend
- **FastAPI** - High-performance REST API
- **Pydantic** - Data validation
- **SQLite** - Lightweight database (production: PostgreSQL/MySQL)

### AI/ML
- **AWS Rekognition** - Facial emotion detection
- **Boto3** - AWS SDK for Python

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Makefile** - Task automation

---

## 📖 Documentation

### Command Reference

```bash
# Development
make start-standalone  # Run all-in-one app
make dev               # Run backend + frontend in parallel
make start-backend     # Run FastAPI backend only
make start-frontend    # Run Streamlit frontend only

# Testing
make test              # Run backend API tests
make camera-test       # Test webcam access

# Utilities
make status            # Check running services
make stop              # Kill all EmoTrack processes
make check-aws         # Verify AWS credentials
make db-backup         # Backup emotions database
make db-clear          # Delete all emotion data

# Data Generation
python generate_fake_data.py                # Generate for standalone
python generate_fake_data.py data/emotions.db  # Generate for full stack
```

### API Endpoints

**Base URL:** `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/detect-emotion` | Upload frame, returns emotion |
| `POST` | `/emotions/batch` | Save multiple emotion records |
| `GET` | `/emotions/daily-stats?days=N` | Daily emotion distribution |
| `GET` | `/emotions/summary` | Overall statistics |
| `GET` | `/emotions/export?format=json\|csv` | Export all data |
| `DELETE` | `/emotions/clear?confirm=true` | Delete all records |
| `GET` | `/health` | Health check |

**Interactive Docs:** http://localhost:8000/docs

### Database Schema

```sql
CREATE TABLE emotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL,                -- Unix timestamp
    emotion TEXT,                  -- HAPPY, SAD, ANGRY, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Database Locations:**
- Standalone: `./emotions.db`
- Full Stack: `./data/emotions.db`
- Docker: `/app/data/emotions.db` (volume mounted)

---

## 🎯 Performance Optimization

### Frame Sampling
```python
FRAME_SAMPLE_RATE = 24  # Process every 24th frame
# Reduces AWS API calls by 96%
# Cost savings: ~$0.001 → $0.00004 per second
```

### Batch Processing
```python
BATCH_SIZE = 60  # Buffer 60 emotions before DB write
# Reduces database I/O by 60x
# Prevents frequent disk writes
```

### Auto-Refresh
```python
REFRESH_INTERVAL = 60  # Update charts every 60 seconds
# Minimal interruption to video feed
# Aligns with batch save cycle
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   cd backend && pytest test_api.py -v
   ```
5. **Commit your changes**
   ```bash
   git commit -m "✨ Add amazing feature"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines

- Follow [PEP 8](https://pep8.org/) style guide
- Write docstrings for all functions
- Add tests for new features
- Update documentation as needed
- Use conventional commit messages

### Areas for Contribution

- 🎨 UI/UX improvements
- 📊 New chart types and visualizations
- 🔌 Integration with other emotion detection APIs
- 🌐 Multi-language support
- 🧪 Additional test coverage
- 📝 Documentation improvements
- 🐛 Bug fixes

---

## 🔒 Security & Privacy

### Data Privacy
- All emotion data is stored **locally** in SQLite
- No data is sent to external servers (except AWS Rekognition API)
- Database files can be encrypted at rest
- No personal identifiable information (PII) is collected

### AWS Security
- Use IAM roles with minimal permissions
- Rotate AWS credentials regularly
- Never commit credentials to version control
- Use AWS Secrets Manager in production

### Webcam Access
- Webcam is only accessed when tracking is active
- No video is recorded or stored
- Only emotion metadata is saved to database
- Users have full control over data collection

---

## 📈 Roadmap

### Planned Features

- [ ] **PostgreSQL/MySQL support** for production deployments
- [ ] **Authentication & user management** with JWT tokens
- [ ] **Real-time notifications** for emotion thresholds
- [ ] **Mobile app** with React Native
- [ ] **Multi-face detection** for group analytics
- [ ] **Custom emotion models** with TensorFlow
- [ ] **Voice emotion analysis** integration
- [ ] **Slack/Discord integration** for team analytics
- [ ] **Data anonymization** for research sharing
- [ ] **Cloud deployment guides** (AWS, Azure, GCP)

---

## ⚠️ Known Limitations

1. **SQLite Concurrency** - Single-process only; use PostgreSQL/MySQL for multi-user
2. **No Authentication** - Backend has open CORS; add JWT/API keys for production
3. **Frame Sampling Trade-off** - Processes 1 in 24 frames; some emotions may be missed
4. **Batch Buffer Risk** - 60-emotion buffer in memory; data loss possible on crash
5. **Docker Webcam** - Camera access only works on Linux containers
6. **AWS Costs** - Rekognition charges per API call; ~$0.001 per image

---

## 🐛 Troubleshooting

### Camera Issues
```bash
# Check camera permissions
# macOS: System Preferences → Security & Privacy → Camera

# Test camera
make camera-test

# Try different camera index
# In code: cv2.VideoCapture(0) → cv2.VideoCapture(1)
```

### AWS Issues
```bash
# Verify credentials
make check-aws

# Or manually
aws configure list
aws rekognition describe-projects --region us-east-1
```

### Port Conflicts
```bash
# Stop all services
make stop

# Or manually
lsof -ti:8501 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### Module Not Found
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements-local.txt
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 EmoTrack Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- **AWS Rekognition** for providing powerful emotion detection capabilities
- **Streamlit** for making web app development delightful
- **FastAPI** for the blazing-fast backend framework
- **OpenCV** for robust computer vision tools
- All our contributors and supporters!

---

## 💬 Community & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/EmoTrack/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/EmoTrack/discussions)
- **Email**: support@emotrack.dev

---

<div align="center">

### ⭐ Star us on GitHub!

If you find EmoTrack useful, please consider giving us a star. It helps the project grow!

[![GitHub stars](https://img.shields.io/github/stars/yourusername/EmoTrack.svg?style=social&label=Star)](https://github.com/yourusername/EmoTrack)

**Built with ❤️ by the EmoTrack team**

[Website](https://emotrack.dev) • [Twitter](https://twitter.com/emotrack) • [Blog](https://blog.emotrack.dev)

</div>
