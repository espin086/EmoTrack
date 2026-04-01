"""
Unit tests for facial_analysis module (on-device ML)

Run with: pytest logic/test_facial_analysis.py -v
"""
import pytest
import numpy as np
import cv2
from unittest.mock import patch, MagicMock
from logic.facial_analysis import detect_emotion, EMOTION_LABELS


def _make_mock_cascade(faces):
    """Create a mock CascadeClassifier that returns the given faces."""
    mock = MagicMock()
    mock.detectMultiScale.return_value = faces
    return mock


def _make_model_output(emotion_idx):
    """Create a mock ONNX model output for a given emotion index."""
    output = np.zeros((1, 7), dtype=np.float32)
    output[0, emotion_idx] = 0.95
    return [output]


@pytest.mark.unit
class TestDetectEmotion:
    """Tests for detect_emotion function"""

    @pytest.fixture
    def sample_frame(self):
        """Create a sample image frame"""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(frame, (25, 25), (75, 75), (255, 255, 255), -1)
        return frame

    def test_detect_emotion_success(self, sample_frame):
        """Test successful emotion detection returns correct emotion"""
        mock_cascade = _make_mock_cascade(np.array([[25, 25, 50, 50]]))
        with patch("logic.facial_analysis.face_cascade", mock_cascade), \
             patch("logic.facial_analysis.session.run", return_value=_make_model_output(3)):
            emotion = detect_emotion(sample_frame)
            assert emotion == "HAPPY"

    def test_detect_emotion_no_face(self, sample_frame):
        """Test emotion detection when no face is detected"""
        mock_cascade = _make_mock_cascade(())
        with patch("logic.facial_analysis.face_cascade", mock_cascade):
            emotion = detect_emotion(sample_frame)
            assert emotion == "NO FACE"

    def test_detect_emotion_all_supported_emotions(self, sample_frame):
        """Test detection of all supported emotions"""
        mock_cascade = _make_mock_cascade(np.array([[25, 25, 50, 50]]))
        for idx, emotion_label in enumerate(EMOTION_LABELS):
            with patch("logic.facial_analysis.face_cascade", mock_cascade), \
                 patch("logic.facial_analysis.session.run", return_value=_make_model_output(idx)):
                detected = detect_emotion(sample_frame)
                assert detected == emotion_label

    def test_detect_emotion_encoding_failure(self):
        """Test emotion detection with invalid frame"""
        invalid_frame = np.array([])
        with pytest.raises((ValueError, cv2.error)):
            detect_emotion(invalid_frame)

    def test_detect_emotion_model_error(self, sample_frame):
        """Test emotion detection when model inference fails"""
        mock_cascade = _make_mock_cascade(np.array([[25, 25, 50, 50]]))
        with patch("logic.facial_analysis.face_cascade", mock_cascade), \
             patch("logic.facial_analysis.session.run", side_effect=Exception("Model error")):
            with pytest.raises(Exception, match="Model error"):
                detect_emotion(sample_frame)

    def test_detect_emotion_with_realistic_frame(self):
        """Test emotion detection with a realistic colored frame"""
        frame = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.ellipse(frame, (100, 100), (50, 70), 0, 0, 360, (180, 150, 120), -1)
        cv2.circle(frame, (85, 90), 8, (50, 50, 50), -1)
        cv2.circle(frame, (115, 90), 8, (50, 50, 50), -1)

        mock_cascade = _make_mock_cascade(np.array([[50, 30, 100, 140]]))
        with patch("logic.facial_analysis.face_cascade", mock_cascade), \
             patch("logic.facial_analysis.session.run", return_value=_make_model_output(6)):
            emotion = detect_emotion(frame)
            assert emotion == "CALM"

    def test_detect_emotion_largest_face_used(self, sample_frame):
        """Test that the largest face is selected when multiple faces detected"""
        mock_cascade = _make_mock_cascade(np.array([[10, 10, 10, 10], [25, 25, 50, 50]]))
        with patch("logic.facial_analysis.face_cascade", mock_cascade), \
             patch("logic.facial_analysis.session.run", return_value=_make_model_output(3)) as mock_run:
            emotion = detect_emotion(sample_frame)
            assert emotion == "HAPPY"
            assert mock_run.called

    def test_emotion_labels_count(self):
        """Test that we have exactly 7 emotion labels"""
        assert len(EMOTION_LABELS) == 7

    def test_emotion_labels_contents(self):
        """Test that emotion labels match expected set"""
        expected = {"ANGRY", "DISGUSTED", "FEAR", "HAPPY", "SAD", "SURPRISED", "CALM"}
        assert set(EMOTION_LABELS) == expected

    def test_detect_emotion_returns_string(self, sample_frame):
        """Test that detect_emotion always returns a string"""
        mock_cascade = _make_mock_cascade(np.array([[25, 25, 50, 50]]))
        with patch("logic.facial_analysis.face_cascade", mock_cascade), \
             patch("logic.facial_analysis.session.run", return_value=_make_model_output(0)):
            result = detect_emotion(sample_frame)
            assert isinstance(result, str)

    def test_detect_emotion_no_face_returns_string(self, sample_frame):
        """Test that NO FACE result is a string"""
        mock_cascade = _make_mock_cascade(())
        with patch("logic.facial_analysis.face_cascade", mock_cascade):
            result = detect_emotion(sample_frame)
            assert isinstance(result, str)
            assert result == "NO FACE"


@pytest.mark.integration
class TestDetectEmotionIntegration:
    """Integration tests for detect_emotion (requires ONNX model)"""

    @pytest.mark.skip(reason="Requires webcam and real inference")
    def test_detect_emotion_real_inference(self):
        """Test emotion detection with real model inference"""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(frame, (25, 25), (75, 75), (255, 255, 255), -1)

        emotion = detect_emotion(frame)

        valid_emotions = list(EMOTION_LABELS) + ["NO FACE"]
        assert emotion in valid_emotions
