# Mac App Store Distribution Plan for EmoTrack

## Context

EmoTrack is a web-based Python/Streamlit emotion detection app using AWS Rekognition. This plan covers converting it to a native Mac App Store application using on-device Core ML (replacing AWS), improving the UI, and establishing a local testing workflow.

---

## Phase 1: Replace AWS Rekognition with Apple Core ML

### Why
- Eliminates network dependency and AWS costs ($0 vs ~$0.001/image)
- No facial data leaves the device — dramatically simplifies App Store privacy review
- 20-100ms latency vs ~2 seconds with AWS
- Works offline
- Removes need for `com.apple.security.network.client` entitlement (unless needed for other features)

### How

**Step 1: Obtain a pre-trained emotion detection model**

Use an open-source FER2013-trained PyTorch model:

| Project | Accuracy | Notes |
|---------|----------|-------|
| [WuJie1010/Facial-Expression-Recognition.Pytorch](https://github.com/WuJie1010/Facial-Expression-Recognition.Pytorch) | 73% FER2013 / 95% CK+ | Mature, well-documented |
| [LetheSec/Fer2013-Facial-Emotion-Recognition-Pytorch](https://github.com/LetheSec/Fer2013-Facial-Emotion-Recognition-Pytorch) | 73.7% | Ready to convert |

Classifies 7 emotions: Angry, Disgusted, Fearful, Happy, Sad, Surprised, Neutral (comparable to Rekognition's 8).

**Step 2: Convert to Core ML format**

```python
import torch
import coremltools as ct

model = torch.load('fer2013_model.pth')
model.eval()

example_input = torch.randn(1, 1, 48, 48)
traced_model = torch.jit.trace(model, example_input)

mlmodel = ct.convert(
    traced_model,
    convert_to='mlprogram',
    inputs=[ct.ImageType(name="image", shape=(1, 1, 48, 48))],
    compute_units=ct.ComputeUnit.CPU_AND_NE  # Use Neural Engine on Apple Silicon
)
mlmodel.save('models/emotion_detector.mlmodel')
```

**Step 3: Replace `logic/facial_analysis.py`**

```python
# logic/facial_analysis.py — Core ML version (drop-in replacement)
import coremltools as ct
import cv2
import numpy as np

model = ct.models.MLModel('models/emotion_detector.mlmodel')

def detect_emotion(frame) -> str:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    normalized = resized.astype('float32') / 255.0
    input_data = np.expand_dims(normalized, axis=(0, 1))

    try:
        result = model.predict({'image': input_data})
        return result.get('classLabel', 'NO FACE')
    except Exception:
        return 'NO FACE'
```

No changes needed to batch buffering, database logic, or API endpoints — this is a drop-in replacement.

### Dependencies to Add
```
coremltools>=7.0
```

### Dependencies to Remove
```
boto3  (no longer needed)
```

---

## Phase 2: UI Improvements

### 2.1 Hide Streamlit Chrome (Desktop-Like Feel)

Add to both `EmoTrack.py` and `frontend/app.py`:

```python
def hide_streamlit_ui():
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { margin-top: -4rem; }
    </style>
    """, unsafe_allow_html=True)
```

### 2.2 Custom Theme

Create `.streamlit/config.toml`:

```toml
[theme]
base = "light"
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

Add dark mode support:
```toml
[theme.dark]
primaryColor = "#FF6B6B"
backgroundColor = "#1E1E1E"
secondaryBackgroundColor = "#262730"
textColor = "#FFFFFF"
```

### 2.3 Replace Matplotlib with Plotly

Swap static charts for interactive ones:

```python
import plotly.express as px

fig = px.bar(emotion_counts, x='emotion', y='count',
             color='emotion', template="plotly_white")
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)
```

### 2.4 Upgrade Video Display with streamlit-webrtc

Replace frame-by-frame `st.image()` (~14fps) with WebRTC streaming:

```python
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

def process_frame(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    emotion = detect_emotion(img)
    cv2.putText(img, f"Emotion: {emotion}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_streamer(
    key="emotion-detection",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=process_frame,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True
)
```

### 2.5 Enhanced Dashboard Components

Add `streamlit-extras` for polished metric cards:

```bash
pip install streamlit-extras plotly streamlit-webrtc
```

```python
from streamlit_extras.metric_cards import style_metric_cards

col1, col2, col3 = st.columns(3)
with col1: st.metric("Total Emotions", 450)
with col2: st.metric("Today's Peak", "Happy")
with col3: st.metric("Avg Session", "12 min")

style_metric_cards()
```

### 2.6 Responsive Layout

```python
st.markdown("""
<style>
@media (max-width: 768px) {
    [data-testid="column"] {
        display: block;
        width: 100% !important;
        margin-bottom: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)
```

---

## Phase 3: Local Testing

### 3.1 Core ML Model Testing

```python
# tests/test_coreml_model.py
import pytest
import numpy as np

def test_model_loads():
    import coremltools as ct
    model = ct.models.MLModel('models/emotion_detector.mlmodel')
    assert model is not None

def test_model_predicts_emotion():
    import coremltools as ct
    model = ct.models.MLModel('models/emotion_detector.mlmodel')
    test_input = np.random.rand(1, 1, 48, 48).astype('float32')
    result = model.predict({'image': test_input})
    assert 'classLabel' in result
    assert result['classLabel'] in [
        'ANGRY', 'DISGUSTED', 'FEARFUL', 'HAPPY', 'SAD', 'SURPRISED', 'NEUTRAL'
    ]

def test_detect_emotion_no_face():
    from logic.facial_analysis import detect_emotion
    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = detect_emotion(blank_frame)
    assert result == 'NO FACE'
```

### 3.2 UI Testing

```bash
# Manual testing checklist
make start-standalone     # Launch app
# Verify:
# - Hamburger menu hidden
# - Footer hidden
# - Dark/light mode works
# - Charts are interactive (Plotly)
# - Video feed renders smoothly
# - Emotion overlay displays correctly
```

### 3.3 Desktop Wrapper Testing (Tauri)

```bash
# Install Tauri CLI
cargo install tauri-cli

# Dev mode (hot-reload)
cargo tauri dev

# Build .app bundle
cargo tauri build

# Test sandbox manually
codesign --verify --deep --strict EmoTrack.app
```

### 3.4 Sandbox Testing

```bash
# Test with sandbox enabled before submission
sandbox-exec -f /usr/share/sandbox/profiles/no-network.sb ./EmoTrack.app/Contents/MacOS/EmoTrack

# Verify database writes to correct sandbox location
ls ~/Library/Containers/com.emotrack.app/Data/Library/Application\ Support/EmoTrack/
```

### 3.5 Makefile Additions

```makefile
test-coreml:       ## Test Core ML model inference
	pytest tests/test_coreml_model.py -v

test-ui:           ## Launch app for manual UI testing
	streamlit run EmoTrack.py

build-macos:       ## Build macOS .app bundle via Tauri
	cargo tauri build

sign-macos:        ## Code sign the .app bundle
	codesign --deep --force --sign "Developer ID Application: YOUR_NAME" \
		target/release/bundle/macos/EmoTrack.app
```

---

## Phase 4: Tauri Desktop Wrapper

### Architecture

```
Tauri Shell (native macOS WebKit window)
  └── Embedded Streamlit server (Python process)
       └── Core ML inference (on-device)
            └── SQLite database (sandboxed)
```

### Setup

```bash
# Prerequisites
brew install rust
cargo install tauri-cli

# Initialize Tauri project
cargo tauri init
```

### Key Configuration (`tauri.conf.json`)

```json
{
  "build": {
    "devUrl": "http://localhost:8501",
    "beforeDevCommand": "streamlit run EmoTrack.py --server.headless true",
    "beforeBuildCommand": "streamlit run EmoTrack.py --server.headless true"
  },
  "app": {
    "title": "EmoTrack",
    "identifier": "com.emotrack.app",
    "windows": [{
      "title": "EmoTrack - Emotion Detection",
      "width": 1200,
      "height": 800,
      "resizable": true,
      "fullscreen": false
    }],
    "security": {
      "csp": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'"
    }
  },
  "bundle": {
    "active": true,
    "targets": ["dmg", "app"],
    "icon": ["icons/icon.icns"],
    "macOS": {
      "entitlements": "Entitlements.plist",
      "signingIdentity": "Developer ID Application: YOUR_NAME"
    }
  }
}
```

### Entitlements (`Entitlements.plist`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <true/>
    <key>com.apple.security.device.camera</key>
    <true/>
</dict>
</plist>
```

Note: `com.apple.security.network.client` is no longer needed since Core ML runs on-device.

### Lifecycle Management

Tauri must:
1. Start the bundled Python + Streamlit server on app launch
2. Wait for Streamlit to be ready (poll `localhost:8501`)
3. Load the WebView pointing to `localhost:8501`
4. Kill the Python process on app quit

---

## Phase 5: App Store Submission

### Prerequisites
- Apple Developer Program enrollment ($99/year)
- Apple Distribution certificate
- Provisioning profile for Mac App Store

### Submission Steps
1. Code sign `.app` bundle with distribution certificate
2. Package as `.pkg` using `productbuild`
3. Upload via Transporter or `xcrun altool`
4. Fill App Store Connect metadata:
   - App name, description, category (Medical or Lifestyle)
   - Screenshots (at least 1280x800)
   - Privacy policy URL
   - Privacy nutrition labels (camera usage disclosed)
   - Age rating
5. Submit for review (1-3 days typical)

### Privacy Policy Requirements
Must explain:
- Camera is used for real-time facial emotion detection
- All processing happens on-device (no data sent to cloud)
- Emotion data stored locally in SQLite (never uploaded)
- User can delete all data at any time

### App Store Review Risks

| Risk | Mitigation |
|------|------------|
| Camera usage questioned | Clear `NSCameraUsageDescription`: "EmoTrack uses your camera to detect facial emotions in real-time. All processing happens on your device." |
| Embedded web server flagged | Document it; VS Code, Slack use same pattern |
| Sandbox violations | Test with `sandbox-exec` before submission |

---

## Files That Need Changes

| File | Change |
|------|--------|
| `logic/facial_analysis.py` | Replace AWS Rekognition with Core ML |
| `EmoTrack.py` | Hide Streamlit chrome, upgrade charts, use WebRTC |
| `frontend/app.py` | Same UI improvements |
| `requirements-local.txt` | Remove boto3, add coremltools/plotly/streamlit-webrtc |
| `.streamlit/config.toml` | **New** — custom theme + dark mode |
| `models/emotion_detector.mlmodel` | **New** — converted Core ML model |
| `tauri.conf.json` | **New** — Tauri desktop wrapper config |
| `Entitlements.plist` | **New** — macOS sandbox + camera entitlements |
| `tests/test_coreml_model.py` | **New** — Core ML model tests |
| `Makefile` | Add test-coreml, build-macos, sign-macos targets |

---

## New Dependencies

### Add
```
coremltools>=7.0        # Core ML model conversion & inference
plotly>=5.18             # Interactive charts
streamlit-webrtc>=0.47   # Real-time video streaming
streamlit-extras>=0.4    # Enhanced UI components
av>=12.0                 # Video frame processing (WebRTC dependency)
```

### Remove
```
boto3                    # No longer needed (was for AWS Rekognition)
```

---

## Estimated Timeline

| Phase | Duration |
|-------|----------|
| Phase 1: Core ML migration | 1-2 weeks |
| Phase 2: UI improvements | 1 week |
| Phase 3: Local testing | 1 week |
| Phase 4: Tauri wrapper + packaging | 2-3 weeks |
| Phase 5: App Store submission + review | 1-2 weeks |
| **Total** | **6-9 weeks** |

---

## Quick Reference: Key Commands

```bash
# Development
make start-standalone          # Run Streamlit app locally
make test-coreml               # Test Core ML model
cargo tauri dev                # Run in Tauri wrapper (hot-reload)

# Building
cargo tauri build              # Build .app bundle
make sign-macos                # Code sign

# Testing
pytest tests/ -v               # All tests
sandbox-exec -f ... ./app      # Sandbox testing
codesign --verify ./app        # Verify signing
```
