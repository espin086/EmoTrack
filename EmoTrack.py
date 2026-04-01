"""EmoTrack"""


import streamlit as st
import cv2
import sqlite3
from datetime import datetime
import pytz

import pandas as pd
import plotly.graph_objects as go

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

# Hide Streamlit chrome for desktop-like experience
st.markdown("""<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>""", unsafe_allow_html=True)

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

        # Create modern comparison chart with Plotly
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Today', x=all_emotions, y=today_values,
            marker_color='#00D9FF', opacity=0.9,
        ))
        fig.add_trace(go.Bar(
            name='Week Average', x=all_emotions, y=week_values,
            marker_color='#7B61FF', opacity=0.9,
        ))
        fig.update_layout(
            title='Today vs Weekly Baseline',
            xaxis_title='Emotion',
            yaxis_title='Distribution (%)',
            barmode='group',
            template='plotly_dark',
            height=450,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        st.plotly_chart(fig, use_container_width=True)
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
            'DISGUSTED': '#A084DC'  # Lavender
        }

        # Create stacked area chart with Plotly
        fig = go.Figure()
        for emotion in pivot_df_pct.columns:
            fig.add_trace(go.Scatter(
                x=pivot_df_pct.index,
                y=pivot_df_pct[emotion],
                name=emotion,
                stackgroup='one',
                line=dict(width=0.5),
                fillcolor=emotion_colors_modern.get(emotion, '#808080'),
                marker_color=emotion_colors_modern.get(emotion, '#808080'),
            ))
        fig.update_layout(
            title='Monthly Emotion Distribution',
            xaxis_title='Month',
            yaxis_title='Distribution (%)',
            yaxis=dict(range=[0, 100]),
            template='plotly_dark',
            height=500,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        st.plotly_chart(fig, use_container_width=True)
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
st.markdown("EmoTrack - Real-Time Emotion Tracking | Powered by On-Device AI")
