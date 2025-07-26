"""EmoTrack Backend API"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
import cv2
import numpy as np
import boto3
from typing import List, Dict, Optional
import json
import base64
import logging
from contextlib import contextmanager
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="EmoTrack API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AWS Rekognition client
client = boto3.client("rekognition")

# Database configuration
DB_PATH = os.environ.get("DB_PATH", "/app/data/emotions.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Pydantic models
class EmotionRecord(BaseModel):
    timestamp: float
    emotion: str

class EmotionBatch(BaseModel):
    emotions: List[EmotionRecord]

class DateRange(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class EmotionStats(BaseModel):
    date: str
    emotion: str
    count: int
    percentage: float

# Database context manager
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize database
def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS emotions 
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                emotion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
        )
        conn.commit()
    logger.info("Database initialized")

# Initialize database on startup
init_db()

@app.get("/")
def read_root():
    return {"message": "EmoTrack API is running"}

@app.post("/detect-emotion")
async def detect_emotion(file: UploadFile = File(...)):
    """Detect emotion from uploaded image"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Call AWS Rekognition
        response = client.detect_faces(
            Image={"Bytes": contents}, 
            Attributes=["EMOTIONS"]
        )
        
        if not response["FaceDetails"]:
            return {"emotion": "NO FACE", "confidence": 0}
        
        emotions = response["FaceDetails"][0]["Emotions"]
        top_emotion = emotions[0]
        
        return {
            "emotion": top_emotion["Type"],
            "confidence": top_emotion["Confidence"],
            "all_emotions": emotions
        }
    except Exception as e:
        logger.error(f"Error detecting emotion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emotions/batch")
async def save_emotions_batch(batch: EmotionBatch):
    """Save a batch of emotions to database"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            data = [(e.timestamp, e.emotion) for e in batch.emotions]
            cursor.executemany(
                "INSERT INTO emotions (timestamp, emotion) VALUES (?, ?)", 
                data
            )
            conn.commit()
            return {"message": f"Saved {len(batch.emotions)} emotions"}
    except Exception as e:
        logger.error(f"Error saving emotions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emotions/daily-stats", response_model=List[EmotionStats])
async def get_daily_emotion_stats(days: int = 7):
    """Get emotion statistics for the last N days"""
    try:
        with get_db() as conn:
            query = """
            WITH date_emotions AS (
                SELECT
                    DATE(DATETIME(timestamp, 'unixepoch')) as date,
                    emotion,
                    COUNT(*) as emotion_count
                FROM emotions
                WHERE timestamp >= ?
                GROUP BY date, emotion
            ),
            date_totals AS (
                SELECT date, SUM(emotion_count) as total_count
                FROM date_emotions
                GROUP BY date
            )
            SELECT 
                de.date,
                de.emotion,
                de.emotion_count as count,
                ROUND(CAST(de.emotion_count AS FLOAT) / dt.total_count * 100, 2) as percentage
            FROM date_emotions de
            JOIN date_totals dt ON de.date = dt.date
            ORDER BY de.date DESC, de.emotion_count DESC
            """
            
            start_timestamp = (datetime.now() - timedelta(days=days)).timestamp()
            cursor = conn.execute(query, (start_timestamp,))
            
            results = []
            for row in cursor:
                results.append(EmotionStats(
                    date=row["date"],
                    emotion=row["emotion"],
                    count=row["count"],
                    percentage=row["percentage"]
                ))
            
            return results
    except Exception as e:
        logger.error(f"Error getting daily stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emotions/summary")
async def get_emotion_summary():
    """Get overall emotion summary statistics"""
    try:
        with get_db() as conn:
            # Total emotions recorded
            total_query = "SELECT COUNT(*) as total FROM emotions"
            total_count = conn.execute(total_query).fetchone()["total"]
            
            # Emotion distribution
            distribution_query = """
            SELECT emotion, COUNT(*) as count,
                   ROUND(CAST(COUNT(*) AS FLOAT) / ? * 100, 2) as percentage
            FROM emotions
            GROUP BY emotion
            ORDER BY count DESC
            """
            cursor = conn.execute(distribution_query, (total_count,))
            distribution = {row["emotion"]: {"count": row["count"], "percentage": row["percentage"]} 
                          for row in cursor}
            
            # Most recent emotion
            recent_query = """
            SELECT emotion, timestamp 
            FROM emotions 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
            recent = conn.execute(recent_query).fetchone()
            
            # Date range
            range_query = """
            SELECT 
                DATE(DATETIME(MIN(timestamp), 'unixepoch')) as start_date,
                DATE(DATETIME(MAX(timestamp), 'unixepoch')) as end_date
            FROM emotions
            """
            date_range = conn.execute(range_query).fetchone()
            
            return {
                "total_emotions_recorded": total_count,
                "emotion_distribution": distribution,
                "most_recent": {
                    "emotion": recent["emotion"] if recent else None,
                    "timestamp": recent["timestamp"] if recent else None
                },
                "date_range": {
                    "start": date_range["start_date"] if date_range else None,
                    "end": date_range["end_date"] if date_range else None
                }
            }
    except Exception as e:
        logger.error(f"Error getting emotion summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emotions/export")
async def export_emotions(format: str = "json"):
    """Export all emotion data in JSON or CSV format"""
    try:
        with get_db() as conn:
            query = """
            SELECT timestamp, emotion, created_at
            FROM emotions
            ORDER BY timestamp DESC
            """
            cursor = conn.execute(query)
            
            data = []
            for row in cursor:
                data.append({
                    "timestamp": row["timestamp"],
                    "emotion": row["emotion"],
                    "created_at": row["created_at"]
                })
            
            if format == "csv":
                import csv
                import io
                output = io.StringIO()
                if data:
                    writer = csv.DictWriter(output, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                return {"format": "csv", "data": output.getvalue()}
            else:
                return {"format": "json", "data": data}
    except Exception as e:
        logger.error(f"Error exporting emotions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/emotions/clear")
async def clear_emotions(confirm: bool = False):
    """Clear all emotion data (requires confirmation)"""
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM emotions")
            conn.commit()
            return {"message": "All emotion data cleared"}
    except Exception as e:
        logger.error(f"Error clearing emotions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        with get_db() as conn:
            conn.execute("SELECT 1")
        
        # Check AWS connection (optional, might want to cache this)
        # client.describe_regions()
        
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)