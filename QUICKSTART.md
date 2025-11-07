# 🚀 EmoTrack Quick Start - Local Setup

Get EmoTrack running locally in 5 minutes with full camera access!

## Step-by-Step Instructions

### 1️⃣ Setup Environment (One Time Only)

```bash
# Navigate to the project directory
cd /Users/jjespinoza/Documents/PersonalGitHub/EmoTrack

# Run the automated setup
./setup_local.sh
```

This will create a virtual environment and install all dependencies automatically.

### 2️⃣ Configure AWS Credentials

Make sure you have AWS credentials configured. Choose one method:

**Option A: Quick Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your_access_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_key_here"
export AWS_DEFAULT_REGION="us-east-1"
```

**Option B: AWS CLI (Better)**
```bash
aws configure
# Then enter your credentials when prompted
```

### 3️⃣ Start EmoTrack

**EASIEST: Standalone Mode** (Single command)
```bash
source venv/bin/activate
./start_standalone.sh
```

Opens at: **http://localhost:8501**

---

**OR**

**Full Stack Mode** (More features, two terminals needed)

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

Opens at:
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## That's It! 🎉

1. Open http://localhost:8501 in your browser
2. Click "Webcam Feed" in the sidebar
3. Click "▶️ Start" button
4. Allow camera permissions if prompted
5. Watch real-time emotion detection!

## Common Issues

**Camera not working?**
- Make sure no other app is using your camera
- Grant camera permissions to Terminal (System Preferences → Security & Privacy → Camera)

**AWS errors?**
- Verify credentials: `aws configure list`
- Make sure Rekognition is enabled in your AWS region

**Port in use?**
```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

## Full Documentation

For detailed instructions, troubleshooting, and advanced features:
- **[Local Development Guide](README_LOCAL.md)** - Complete local setup guide
- **[Main README](README.md)** - Project overview and features

---

**Need help?** Open an issue: https://github.com/espin086/EmoTrack/issues

