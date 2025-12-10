"""EmoTrack Frontend"""

import streamlit as st
import cv2
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import logging
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API URL
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

# Constants
BATCH_SIZE = 60
FRAME_SAMPLE_RATE = 24  # Sample every 24th frame

# Initialize session state
if "emotions_batch" not in st.session_state:
    st.session_state.emotions_batch = []

st.set_page_config(page_title="EmoTrack", page_icon="😊", layout="wide")
st.title("EmoTrack - Real-Time Emotion Tracking Dashboard")

# Initialize session state
if "running" not in st.session_state:
    st.session_state.running = False
if "frame_count" not in st.session_state:
    st.session_state.frame_count = 0
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Check backend health
@st.cache_data(ttl=60)
def check_backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Backend health status in sidebar
with st.sidebar:
    st.markdown("## Backend Status")
    health = check_backend_health()
    if health["status"] == "healthy":
        st.success("✅ Backend Connected")
    else:
        st.error(f"❌ Backend Error: {health.get('error', 'Unknown')}")

# Helper function to save emotions batch
def save_emotions_batch(emotions_batch):
    """Save a batch of emotions to backend"""
    try:
        payload = {"emotions": emotions_batch}
        response = requests.post(f"{BACKEND_URL}/emotions/batch", json=payload)
        response.raise_for_status()
        logger.info(f"Saved {len(emotions_batch)} emotions")
        return True
    except Exception as e:
        logger.error(f"Error saving emotions: {e}")
        st.error(f"Failed to save emotions: {e}")
        return False

# Helper function to detect emotion
def detect_emotion_api(frame):
    """Call backend API to detect emotion"""
    try:
        # Convert frame to JPEG bytes
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            return None

        # Send to API
        files = {'file': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
        response = requests.post(f"{BACKEND_URL}/detect-emotion", files=files, timeout=5)
        response.raise_for_status()

        result = response.json()
        return result
    except Exception as e:
        logger.error(f"Error detecting emotion: {e}")
        return None

# Tab navigation
tab1, tab2 = st.tabs(["🏠 Overview", "⚙️ Settings"])

with tab1:
    st.write("## Dashboard Overview")

    # Auto-refresh every 60 seconds during tracking
    if st.session_state.running:
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh > 60:  # 60 seconds = 1 minute
            st.session_state.last_refresh = datetime.now()
            st.rerun()

    # Fetch summary statistics from backend
    try:
        response = requests.get(f"{BACKEND_URL}/emotions/summary")
        response.raise_for_status()
        summary = response.json()

        # Metrics cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Emotions Recorded", f"{summary['total_emotions_recorded']:,}")

        with col2:
            if summary['most_recent']['emotion']:
                st.metric("Most Recent Emotion", summary['most_recent']['emotion'])
            else:
                st.metric("Most Recent Emotion", "No data")

        with col3:
            # Get today's count
            try:
                today_response = requests.get(f"{BACKEND_URL}/emotions/daily-stats", params={"days": 1})
                today_response.raise_for_status()
                today_data = today_response.json()
                today_count = sum(item['count'] for item in today_data) if today_data else 0
                st.metric("Today's Records", f"{today_count:,}")
            except:
                st.metric("Today's Records", "0")

        # Today vs Week Comparison
        st.subheader("Today vs This Week")
        try:
            today_response = requests.get(f"{BACKEND_URL}/emotions/daily-stats", params={"days": 1})
            week_response = requests.get(f"{BACKEND_URL}/emotions/daily-stats", params={"days": 7})
            today_response.raise_for_status()
            week_response.raise_for_status()

            today_data = today_response.json()
            week_data = week_response.json()

            if today_data or week_data:
                # Get all unique emotions
                all_emotions = sorted(set(
                    [item['emotion'] for item in today_data] +
                    [item['emotion'] for item in week_data]
                ))

                # Calculate percentages (normalized to 100%)
                today_total = sum(item['count'] for item in today_data) if today_data else 0
                week_total = sum(item['count'] for item in week_data) if week_data else 0

                today_counts = {item['emotion']: (item['count'] / today_total * 100) if today_total > 0 else 0
                               for item in today_data}
                week_counts = {item['emotion']: (item['count'] / week_total * 100) if week_total > 0 else 0
                              for item in week_data}

                today_values = [today_counts.get(e, 0) for e in all_emotions]
                week_values = [week_counts.get(e, 0) for e in all_emotions]

                # Create modern comparison chart
                fig, ax = plt.subplots(figsize=(14, 6), facecolor='#0E1117')
                ax.set_facecolor('#0E1117')
                x = range(len(all_emotions))
                width = 0.38

                # Modern gradient colors
                today_color = '#00D9FF'  # Bright cyan
                week_color = '#7B61FF'   # Purple

                bars1 = ax.bar([i - width/2 for i in x], today_values, width,
                              label='Today', color=today_color, alpha=0.9,
                              edgecolor='none', linewidth=0)
                bars2 = ax.bar([i + width/2 for i in x], week_values, width,
                              label='Week Average', color=week_color, alpha=0.9,
                              edgecolor='none', linewidth=0)

                # Modern styling
                ax.set_xlabel('Emotion', fontsize=13, color='#FFFFFF', fontweight='500')
                ax.set_ylabel('Distribution (%)', fontsize=13, color='#FFFFFF', fontweight='500')
                ax.set_title('Today vs Weekly Baseline', fontsize=16, color='#FFFFFF',
                           fontweight='600', pad=20)
                ax.set_ylim(0, max(max(today_values) if today_values else 0,
                                 max(week_values) if week_values else 0) * 1.15)
                ax.set_xticks(x)
                ax.set_xticklabels(all_emotions, rotation=0, ha='center',
                                 fontsize=11, color='#FAFAFA')

                # Remove spines for cleaner look
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#333333')
                ax.spines['bottom'].set_color('#333333')

                # Subtle grid
                ax.grid(True, alpha=0.15, axis='y', color='#444444', linestyle='-', linewidth=0.5)
                ax.set_axisbelow(True)

                # Modern legend
                legend = ax.legend(loc='upper right', frameon=True, fancybox=True,
                                 shadow=False, fontsize=11, framealpha=0.9)
                legend.get_frame().set_facecolor('#1E1E1E')
                legend.get_frame().set_edgecolor('#333333')
                for text in legend.get_texts():
                    text.set_color('#FFFFFF')

                # Style tick labels
                ax.tick_params(axis='y', colors='#CCCCCC', labelsize=10)
                ax.tick_params(axis='x', colors='#FAFAFA', labelsize=11)

                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            else:
                st.info("No emotions recorded yet. Start tracking to see comparisons!")
        except Exception as e:
            st.info("No emotions recorded yet. Start tracking to see comparisons!")

        # Monthly Trend
        st.subheader("Monthly Emotion Trends")
        try:
            # Get data for last 12 months
            monthly_response = requests.get(f"{BACKEND_URL}/emotions/daily-stats", params={"days": 365})
            monthly_response.raise_for_status()
            monthly_data = monthly_response.json()

            if monthly_data:
                # Convert to DataFrame and group by month
                df = pd.DataFrame(monthly_data)
                df['date'] = pd.to_datetime(df['date'])
                df['month'] = df['date'].dt.to_period('M').astype(str)

                # Group by month and emotion
                monthly_grouped = df.groupby(['month', 'emotion'])['count'].sum().reset_index()

                # Pivot for stacking
                pivot_df = monthly_grouped.pivot(index='month', columns='emotion', values='count').fillna(0)

                if len(pivot_df) > 0:
                    # Create modern stacked area chart
                    fig, ax = plt.subplots(figsize=(14, 7), facecolor='#0E1117')
                    ax.set_facecolor('#0E1117')

                    # Normalize to percentages (each month = 100%)
                    pivot_df_pct = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100

                    # Modern vibrant color palette
                    emotion_colors_modern = {
                        'HAPPY': '#FFD93D',     # Bright yellow
                        'CALM': '#6BCB77',      # Fresh green
                        'SURPRISED': '#4D96FF', # Bright blue
                        'CONFUSED': '#9D84B7',  # Soft purple
                        'SAD': '#5F85DB',       # Deep blue
                        'FEAR': '#FF6B9D',      # Pink
                        'ANGRY': '#FF5757',     # Bright red
                        'DISGUST': '#A084DC'    # Lavender
                    }

                    # Create colors list for available emotions
                    colors = [emotion_colors_modern.get(emotion, '#808080') for emotion in pivot_df_pct.columns]

                    # Create smooth stacked area chart with percentages
                    ax.stackplot(range(len(pivot_df_pct)),
                                [pivot_df_pct[col].values for col in pivot_df_pct.columns],
                                labels=pivot_df_pct.columns,
                                colors=colors,
                                alpha=0.85,
                                edgecolor='none')

                    # Modern styling
                    ax.set_xlabel('Month', fontsize=13, color='#FFFFFF', fontweight='500')
                    ax.set_ylabel('Distribution (%)', fontsize=13, color='#FFFFFF', fontweight='500')
                    ax.set_title('Monthly Emotion Distribution', fontsize=16, color='#FFFFFF',
                               fontweight='600', pad=20)
                    ax.set_ylim(0, 100)
                    ax.set_xticks(range(len(pivot_df)))
                    ax.set_xticklabels(pivot_df.index, rotation=45, ha='right',
                                      fontsize=10, color='#FAFAFA')

                    # Remove top and right spines
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_color('#333333')
                    ax.spines['bottom'].set_color('#333333')

                    # Subtle grid
                    ax.grid(True, alpha=0.12, axis='y', color='#444444', linestyle='-', linewidth=0.5)
                    ax.set_axisbelow(True)

                    # Modern legend
                    legend = ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
                                      frameon=True, fancybox=True, shadow=False,
                                      fontsize=10, framealpha=0.9)
                    legend.get_frame().set_facecolor('#1E1E1E')
                    legend.get_frame().set_edgecolor('#333333')
                    for text in legend.get_texts():
                        text.set_color('#FFFFFF')

                    # Style tick labels
                    ax.tick_params(axis='y', colors='#CCCCCC', labelsize=10)
                    ax.tick_params(axis='x', colors='#FAFAFA', labelsize=10)

                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                else:
                    st.info("No historical data yet. Keep tracking to see monthly trends!")
            else:
                st.info("No historical data yet. Keep tracking to see monthly trends!")
        except Exception as e:
            st.info("No historical data yet. Keep tracking to see monthly trends!")

    except Exception as e:
        st.error(f"Failed to load dashboard: {e}")
        st.info("Make sure the backend is running and healthy.")

    # Live Tracking Section
    st.markdown("---")
    st.subheader("📹 Live Emotion Tracking")
    st.info("Start tracking to record your emotions in real-time. Charts will auto-update every 60 seconds.")

    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        if st.button("▶️ Start", disabled=st.session_state.running, use_container_width=True):
            st.session_state.running = True
            st.session_state.emotions_batch = []
            st.rerun()

    with col2:
        if st.button("⏹️ Stop", disabled=not st.session_state.running, use_container_width=True):
            st.session_state.running = False
            # Save any remaining emotions
            if st.session_state.emotions_batch:
                save_emotions_batch(st.session_state.emotions_batch)
                st.session_state.emotions_batch = []
            st.rerun()

    # Webcam Feed
    if st.session_state.running:
        frame_placeholder = st.empty()
        status_col1, status_col2 = st.columns(2)

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        current_emotion = None
        confidence = 0

        # Process frames in a loop
        for _ in range(1440):  # Process 1440 frames before allowing refresh (about 60 seconds at 24fps)
            if not st.session_state.running:
                break

            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to get frame from webcam")
                st.session_state.running = False
                break

            st.session_state.frame_count += 1

            # Sample frame for emotion detection
            if st.session_state.frame_count % FRAME_SAMPLE_RATE == 0:
                result = detect_emotion_api(frame)
                if result and result["emotion"] != "NO FACE":
                    current_emotion = result["emotion"]
                    confidence = result.get("confidence", 0)

                    # Add to batch
                    st.session_state.emotions_batch.append({
                        "timestamp": datetime.now().timestamp(),
                        "emotion": current_emotion
                    })

                    # Save batch if full
                    if len(st.session_state.emotions_batch) >= BATCH_SIZE:
                        save_emotions_batch(st.session_state.emotions_batch)
                        st.session_state.emotions_batch = []

            # Display emotion on frame
            if current_emotion:
                cv2.putText(frame, current_emotion, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Confidence bar
                if confidence > 0:
                    bar_width = int(200 * (confidence / 100))
                    cv2.rectangle(frame, (10, 50), (10 + bar_width, 70), (0, 255, 0), -1)
                    cv2.putText(frame, f"{confidence:.1f}%", (220, 65),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            # Display frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)

            # Status indicators
            with status_col1:
                st.metric("Current Emotion", current_emotion if current_emotion else "Detecting...")
            with status_col2:
                st.metric("Emotions in Buffer", len(st.session_state.emotions_batch))

        cap.release()

        # Continue capturing if still running
        if st.session_state.running:
            st.rerun()
    else:
        st.info("👆 Click Start to begin tracking your emotions")

with tab2:
    st.write("## Settings & Data Management")

    # Export Data
    st.subheader("📥 Export Data")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Export as JSON"):
            try:
                response = requests.get(f"{BACKEND_URL}/emotions/export", params={"format": "json"})
                response.raise_for_status()
                data = response.json()

                st.download_button(
                    label="Download JSON",
                    data=str(data['data']),
                    file_name=f"emotions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to export data: {e}")

    with col2:
        if st.button("📥 Export as CSV"):
            try:
                response = requests.get(f"{BACKEND_URL}/emotions/export", params={"format": "csv"})
                response.raise_for_status()
                data = response.json()

                st.download_button(
                    label="Download CSV",
                    data=data['data'],
                    file_name=f"emotions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to export data: {e}")

    # Clear data section
    st.markdown("---")
    st.subheader("⚠️ Danger Zone")
    with st.expander("Clear All Data"):
        st.warning("This will permanently delete all emotion data!")
        if st.checkbox("I confirm I want to delete all data"):
            if st.button("🗑️ Clear All Emotion Data", type="secondary"):
                try:
                    response = requests.delete(f"{BACKEND_URL}/emotions/clear", params={"confirm": True})
                    response.raise_for_status()
                    st.success("All emotion data has been cleared")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear data: {e}")

# Footer
st.markdown("---")
st.markdown("🎭 EmoTrack - Real-Time Emotion Tracking | Powered by AWS Rekognition")
