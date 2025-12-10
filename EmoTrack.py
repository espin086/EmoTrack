"""EmoTrack"""


import streamlit as st
import cv2
import sqlite3
from datetime import datetime
import pytz

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from logic.facial_analysis import detect_emotion


BATCH_SIZE = 60


# Function to save a list of emotions to SQLite
def save_emotions_batch(emotions_batch):
    """Save a list of emotions to SQLite"""
    with sqlite3.connect("emotions.db") as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO emotions (timestamp, emotion) VALUES (?, ?)", emotions_batch
        )
        conn.commit()


# Create SQLite database if it doesn't exist
with sqlite3.connect("emotions.db") as conn:
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS emotions 
                  (timestamp INTEGER, emotion TEXT)"""
    )

st.title("EmoTrack - Real-Time Emotion Tracking Dashboard")

# Initialize session state
if "running" not in st.session_state:
    st.session_state.running = False
if "emotions_batch" not in st.session_state:
    st.session_state.emotions_batch = []
if "frame_count" not in st.session_state:
    st.session_state.frame_count = 0
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

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

    # Fetch summary statistics
    with sqlite3.connect("emotions.db") as conn:
        # Total emotions
        total_query = "SELECT COUNT(*) as total FROM emotions"
        total_result = pd.read_sql_query(total_query, conn)
        total_emotions = total_result['total'].iloc[0] if len(total_result) > 0 else 0

        # Most common emotion today
        today_query = """
        SELECT emotion, COUNT(*) as count
        FROM emotions
        WHERE DATE(DATETIME(timestamp, 'unixepoch')) = DATE('now')
        GROUP BY emotion
        ORDER BY count DESC
        LIMIT 1
        """
        today_result = pd.read_sql_query(today_query, conn)
        most_common_today = today_result['emotion'].iloc[0] if len(today_result) > 0 else "No data"

        # Today's emotion timeline
        timeline_query = """
        SELECT
            DATETIME(timestamp, 'unixepoch') as time,
            emotion
        FROM emotions
        WHERE DATE(DATETIME(timestamp, 'unixepoch')) = DATE('now')
        ORDER BY timestamp
        """
        timeline_df = pd.read_sql_query(timeline_query, conn)

    # Metrics cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Emotions Recorded", f"{total_emotions:,}")

    with col2:
        st.metric("Most Common Today", most_common_today)

    with col3:
        if len(timeline_df) > 0:
            st.metric("Today's Records", len(timeline_df))
        else:
            st.metric("Today's Records", "0")

    # Today vs Week Comparison
    st.subheader("Today vs This Week")
    with sqlite3.connect("emotions.db") as conn:
        # Today's emotions
        today_comparison_query = """
        SELECT emotion, COUNT(*) as count
        FROM emotions
        WHERE DATE(DATETIME(timestamp, 'unixepoch')) = DATE('now')
        GROUP BY emotion
        """
        today_comp_df = pd.read_sql_query(today_comparison_query, conn)

        # Last 7 days average
        week_query = """
        SELECT emotion, COUNT(*) as count
        FROM emotions
        WHERE DATE(DATETIME(timestamp, 'unixepoch')) >= DATE('now', '-7 days')
        GROUP BY emotion
        """
        week_df = pd.read_sql_query(week_query, conn)

    if len(today_comp_df) > 0 or len(week_df) > 0:
        # Get all unique emotions
        all_emotions = sorted(set(list(today_comp_df['emotion'].unique() if len(today_comp_df) > 0 else []) +
                                    list(week_df['emotion'].unique() if len(week_df) > 0 else [])))

        # Calculate percentages (normalized to 100%)
        today_total = today_comp_df['count'].sum() if len(today_comp_df) > 0 else 0
        week_total = week_df['count'].sum() if len(week_df) > 0 else 0

        today_counts = {row['emotion']: (row['count'] / today_total * 100) if today_total > 0 else 0
                       for _, row in today_comp_df.iterrows()}
        week_counts = {row['emotion']: (row['count'] / week_total * 100) if week_total > 0 else 0
                      for _, row in week_df.iterrows()}

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

    # Monthly Trend
    st.subheader("Monthly Emotion Trends")
    with sqlite3.connect("emotions.db") as conn:
        monthly_query = """
        SELECT
            strftime('%Y-%m', DATETIME(timestamp, 'unixepoch')) as month,
            emotion,
            COUNT(*) as count
        FROM emotions
        WHERE DATE(DATETIME(timestamp, 'unixepoch')) >= DATE('now', '-12 months')
        GROUP BY month, emotion
        ORDER BY month
        """
        monthly_df = pd.read_sql_query(monthly_query, conn)

    if len(monthly_df) > 0:
        # Create modern stacked area chart
        fig, ax = plt.subplots(figsize=(14, 7), facecolor='#0E1117')
        ax.set_facecolor('#0E1117')

        # Pivot data for stacking
        pivot_df = monthly_df.pivot(index='month', columns='emotion', values='count').fillna(0)

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

        # Process frames in a loop
        for _ in range(1440):  # Process 1440 frames before allowing refresh (about 60 seconds at 24 fps)
            if not st.session_state.running:
                break

            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to get frame from webcam.")
                st.session_state.running = False
                break

            st.session_state.frame_count += 1

            # Detect emotion every 24 frames
            if st.session_state.frame_count % 24 == 0:
                current_emotion = detect_emotion(frame)
                if current_emotion != "NO FACE":
                    st.session_state.emotions_batch.append(
                        (datetime.now().timestamp(), current_emotion)
                    )

                    # Save batch if full
                    if len(st.session_state.emotions_batch) >= BATCH_SIZE:
                        save_emotions_batch(st.session_state.emotions_batch)
                        st.session_state.emotions_batch = []

            # Display emotion on frame
            if current_emotion:
                cv2.putText(
                    frame, current_emotion, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2
                )

            # Display frame
            frame_placeholder.image(frame, channels="BGR", use_column_width=True)

            # Status indicators
            with status_col1:
                st.metric("Current Emotion", current_emotion if current_emotion else "Detecting...")
            with status_col2:
                st.metric("Emotions in Buffer", len(st.session_state.emotions_batch))

        cap.release()

        # Trigger page refresh to update charts
        if st.session_state.running:
            st.rerun()
    else:
        st.info("👆 Click Start to begin tracking your emotions")

with tab2:
    st.write("## Settings & Data Management")

    # Export Data
    st.subheader("📥 Export Data")

    with sqlite3.connect("emotions.db") as conn:
        total_query = "SELECT COUNT(*) as total FROM emotions"
        total_result = pd.read_sql_query(total_query, conn)
        total_emotions = total_result['total'].iloc[0] if len(total_result) > 0 else 0

    col1, col2 = st.columns(2)

    with col1:
        if total_emotions > 0:
            with sqlite3.connect("emotions.db") as conn:
                export_df = pd.read_sql_query("SELECT * FROM emotions", conn)
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="📥 Export as CSV",
                    data=csv,
                    file_name=f"emotrack_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.button("📥 Export as CSV", use_container_width=True, disabled=True)

    with col2:
        if total_emotions > 0:
            with sqlite3.connect("emotions.db") as conn:
                export_df = pd.read_sql_query("SELECT * FROM emotions", conn)
                json_data = export_df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 Export as JSON",
                    data=json_data,
                    file_name=f"emotrack_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.button("📥 Export as JSON", use_container_width=True, disabled=True)

    # Clear Data
    st.markdown("---")
    st.subheader("⚠️ Danger Zone")
    with st.expander("Clear All Data"):
        st.warning("This will permanently delete all emotion records!")
        if st.checkbox("I confirm I want to delete all data"):
            if st.button("🗑️ Clear All Emotion Data", type="secondary"):
                with sqlite3.connect("emotions.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM emotions")
                    conn.commit()
                st.success("All emotion data has been cleared!")
                st.rerun()

# Footer
st.markdown("---")
st.markdown("🎭 EmoTrack - Real-Time Emotion Tracking | Powered by AWS Rekognition")
