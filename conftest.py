"""
Shared pytest fixtures for EmoTrack tests
"""
import os
import sqlite3
import tempfile
from typing import Generator
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_db_path() -> Generator[str, None, None]:
    """Create a temporary database file for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture(scope="function")
def test_db(test_db_path: str) -> Generator[sqlite3.Connection, None, None]:
    """Create a test database connection with schema"""
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row

    # Create schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            emotion TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    yield conn

    # Cleanup - clear all data after each test
    conn.execute("DELETE FROM emotions")
    conn.commit()
    conn.close()


@pytest.fixture(scope="function")
def populated_test_db(test_db: sqlite3.Connection) -> sqlite3.Connection:
    """Test database with sample emotion data"""
    import time

    # Insert sample data spanning multiple days
    base_time = time.time() - (7 * 24 * 60 * 60)  # 7 days ago

    emotions_data = [
        (base_time, "HAPPY"),
        (base_time + 3600, "SAD"),
        (base_time + 7200, "HAPPY"),
        (base_time + 86400, "ANGRY"),  # Next day
        (base_time + 86400 + 3600, "HAPPY"),
        (base_time + 172800, "SURPRISED"),  # 2 days later
        (base_time + 172800 + 3600, "CALM"),
        (base_time + 259200, "FEAR"),  # 3 days later
        (base_time + 259200 + 3600, "CONFUSED"),
        (base_time + 345600, "DISGUSTED"),  # 4 days later
    ]

    test_db.executemany(
        "INSERT INTO emotions (timestamp, emotion) VALUES (?, ?)",
        emotions_data
    )
    test_db.commit()

    return test_db


@pytest.fixture(scope="function")
def api_client(test_db_path: str, monkeypatch) -> TestClient:
    """FastAPI test client with test database"""
    # Set test database path BEFORE importing
    monkeypatch.setenv("DB_PATH", test_db_path)

    # Clear any previously imported modules to force reimport with new env
    import sys
    if 'backend.app' in sys.modules:
        del sys.modules['backend.app']

    # Import app after setting environment variable
    from backend.app import app

    return TestClient(app)


@pytest.fixture
def sample_frame():
    """Generate a sample image frame for testing"""
    import numpy as np
    import cv2

    # Create a simple 100x100 black image
    frame = np.zeros((100, 100, 3), dtype=np.uint8)

    # Add a white rectangle to make it more realistic
    cv2.rectangle(frame, (25, 25), (75, 75), (255, 255, 255), -1)

    return frame


@pytest.fixture
def sample_jpeg_bytes():
    """Generate sample JPEG bytes for testing"""
    import numpy as np
    import cv2

    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(frame, (25, 25), (75, 75), (255, 255, 255), -1)

    _, buffer = cv2.imencode(".jpg", frame)
    return buffer.tobytes()


@pytest.fixture
def mock_rekognition_response():
    """Mock AWS Rekognition response for emotion detection"""
    return {
        "FaceDetails": [
            {
                "Emotions": [
                    {"Type": "HAPPY", "Confidence": 98.5},
                    {"Type": "SAD", "Confidence": 1.2},
                    {"Type": "CALM", "Confidence": 0.3}
                ]
            }
        ]
    }


@pytest.fixture
def mock_rekognition_no_face():
    """Mock AWS Rekognition response with no face detected"""
    return {
        "FaceDetails": []
    }
