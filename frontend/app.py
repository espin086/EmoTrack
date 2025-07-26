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
st.title("EmoTrack - Real-Time Emotion Tracking")

# Check backend health
@st.cache_data(ttl=60)
def check_backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Sidebar
with st.sidebar:
    st.markdown("## Navigation")
    menu = st.radio("Choose a Function", ["Webcam Feed", "Display Graph", "Emotion Summary", "Export Data"])
    
    # Backend health status
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

if menu == "Webcam Feed":
    st.write("## Webcam Feed")
    st.info("📹 Start the webcam to begin tracking your emotions in real-time")
    
    # Initialize session state
    if "running" not in st.session_state:
        st.session_state.running = False
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("▶️ Start", disabled=st.session_state.running):
            st.session_state.running = True
            st.session_state.emotions_batch = []
    
    with col2:
        if st.button("⏹️ Stop", disabled=not st.session_state.running):
            st.session_state.running = False
    
    # Webcam feed
    if st.session_state.running:
        frame_placeholder = st.empty()
        status_placeholder = st.empty()
        
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        frame_count = 0
        current_emotion = None
        confidence = 0
        
        while st.session_state.running:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to get frame from webcam")
                st.session_state.running = False
                break
            
            frame_count += 1
            
            # Sample frame for emotion detection
            if frame_count % FRAME_SAMPLE_RATE == 0:
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
                # Emotion text
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
            
            # Status
            status_placeholder.info(f"📊 Emotions in buffer: {len(st.session_state.emotions_batch)}")
        
        # Save remaining emotions
        if st.session_state.emotions_batch:
            save_emotions_batch(st.session_state.emotions_batch)
            st.session_state.emotions_batch = []
        
        cap.release()

elif menu == "Display Graph":
    st.write("## Emotion Variation Analysis")
    
    # Time range selector
    days = st.slider("Select number of days to analyze", 1, 30, 7)
    
    # Fetch data from backend
    try:
        response = requests.get(f"{BACKEND_URL}/emotions/daily-stats", params={"days": days})
        response.raise_for_status()
        data = response.json()
        
        if not data:
            st.warning("No emotion data available for the selected period")
        else:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Create stacked bar chart
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Define emotion colors
            emotion_colors = {
                "CALM": "#90EE90",
                "HAPPY": "#FFD700",
                "SURPRISED": "#87CEEB",
                "CONFUSED": "#DDA0DD",
                "SAD": "#4682B4",
                "ANGRY": "#DC143C",
                "FEAR": "#FF6347",
                "DISGUST": "#8B4513"
            }
            
            # Prepare data for stacking
            dates = df['date'].unique()
            bottom_values = {date: 0 for date in dates}
            
            # Create bars for each emotion
            for emotion in df['emotion'].unique():
                emotion_data = df[df['emotion'] == emotion]
                
                # Create mapping of date to percentage
                date_percentages = dict(zip(emotion_data['date'], emotion_data['percentage']))
                
                # Get values for all dates (0 if not present)
                values = [date_percentages.get(date, 0) for date in dates]
                bottoms = [bottom_values[date] for date in dates]
                
                # Create bars
                bars = ax.bar(dates, values, bottom=bottoms,
                             color=emotion_colors.get(emotion, '#808080'),
                             label=emotion)
                
                # Update bottom values
                for i, (date, value) in enumerate(zip(dates, values)):
                    bottom_values[date] += value
                
                # Add labels for significant percentages
                for bar, value in zip(bars, values):
                    if value > 5:  # Only show label if > 5%
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2, 
                               bar.get_y() + height/2,
                               f'{value:.0f}%',
                               ha='center', va='center',
                               color='white' if emotion in ['ANGRY', 'SAD', 'FEAR'] else 'black',
                               fontsize=9)
            
            # Customize chart
            ax.set_title(f'Emotion Distribution - Last {days} Days', fontsize=16)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Percentage', fontsize=12)
            ax.set_ylim(0, 100)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            
            # Grid
            ax.yaxis.grid(True, alpha=0.3)
            
            # Tight layout
            plt.tight_layout()
            
            # Display chart
            st.pyplot(fig)
            
            # Show raw data
            with st.expander("View Raw Data"):
                st.dataframe(df)
                
    except Exception as e:
        st.error(f"Failed to fetch emotion data: {e}")

elif menu == "Emotion Summary":
    st.write("## Emotion Summary Statistics")
    
    try:
        response = requests.get(f"{BACKEND_URL}/emotions/summary")
        response.raise_for_status()
        summary = response.json()
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Emotions Recorded", f"{summary['total_emotions_recorded']:,}")
        
        with col2:
            if summary['most_recent']['emotion']:
                st.metric("Most Recent Emotion", summary['most_recent']['emotion'])
            else:
                st.metric("Most Recent Emotion", "No data")
        
        with col3:
            if summary['date_range']['start'] and summary['date_range']['end']:
                st.metric("Date Range", f"{summary['date_range']['start']} to {summary['date_range']['end']}")
            else:
                st.metric("Date Range", "No data")
        
        # Emotion distribution
        st.subheader("Emotion Distribution")
        if summary['emotion_distribution']:
            # Create pie chart
            emotions = list(summary['emotion_distribution'].keys())
            percentages = [v['percentage'] for v in summary['emotion_distribution'].values()]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Define colors
            colors = ['#90EE90', '#FFD700', '#87CEEB', '#DDA0DD', 
                     '#4682B4', '#DC143C', '#FF6347', '#8B4513']
            
            wedges, texts, autotexts = ax.pie(percentages, labels=emotions, autopct='%1.1f%%',
                                               colors=colors[:len(emotions)], startangle=90)
            
            # Enhance text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
            
            ax.set_title('Overall Emotion Distribution', fontsize=16)
            plt.tight_layout()
            st.pyplot(fig)
            
            # Table view
            st.subheader("Detailed Statistics")
            dist_df = pd.DataFrame([
                {"Emotion": emotion, 
                 "Count": data['count'], 
                 "Percentage": f"{data['percentage']:.1f}%"}
                for emotion, data in summary['emotion_distribution'].items()
            ])
            st.dataframe(dist_df, use_container_width=True)
        else:
            st.info("No emotion data available")
            
    except Exception as e:
        st.error(f"Failed to fetch summary: {e}")

elif menu == "Export Data":
    st.write("## Export Emotion Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export as JSON"):
            try:
                response = requests.get(f"{BACKEND_URL}/emotions/export", params={"format": "json"})
                response.raise_for_status()
                data = response.json()
                
                # Create download button
                st.download_button(
                    label="Download JSON",
                    data=str(data['data']),
                    file_name=f"emotions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"Failed to export data: {e}")
    
    with col2:
        if st.button("📥 Export as CSV"):
            try:
                response = requests.get(f"{BACKEND_URL}/emotions/export", params={"format": "csv"})
                response.raise_for_status()
                data = response.json()
                
                # Create download button
                st.download_button(
                    label="Download CSV",
                    data=data['data'],
                    file_name=f"emotions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Failed to export data: {e}")
    
    # Clear data section
    st.subheader("⚠️ Danger Zone")
    with st.expander("Clear All Data"):
        st.warning("This will permanently delete all emotion data!")
        if st.button("🗑️ Clear All Emotion Data", type="secondary"):
            if st.checkbox("I confirm I want to delete all data"):
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