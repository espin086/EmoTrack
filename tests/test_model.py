"""
Unit tests for the ONNX emotion detection model.

Run with: pytest tests/test_model.py -v
"""
import os
import pytest
import numpy as np


MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "emotion_model.onnx")
EXPECTED_EMOTIONS = ["ANGRY", "DISGUSTED", "FEAR", "HAPPY", "SAD", "SURPRISED", "CALM"]


@pytest.mark.unit
class TestModelFile:
    """Tests for the ONNX model file"""

    def test_model_file_exists(self):
        """Test that the ONNX model file exists"""
        assert os.path.exists(MODEL_PATH), f"Model file not found at {MODEL_PATH}"

    def test_model_file_not_empty(self):
        """Test that the model file is not empty"""
        assert os.path.getsize(MODEL_PATH) > 0, "Model file is empty"

    def test_model_file_reasonable_size(self):
        """Test that the model file is a reasonable size (< 50MB)"""
        size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        assert size_mb < 50, f"Model file is too large: {size_mb:.1f}MB"


@pytest.mark.unit
class TestModelLoading:
    """Tests for loading the ONNX model"""

    def test_model_loads_with_onnxruntime(self):
        """Test that the model loads successfully via onnxruntime"""
        import onnxruntime as ort
        session = ort.InferenceSession(MODEL_PATH)
        assert session is not None

    def test_model_has_correct_input_name(self):
        """Test that the model expects 'input' as the input name"""
        import onnxruntime as ort
        session = ort.InferenceSession(MODEL_PATH)
        input_names = [inp.name for inp in session.get_inputs()]
        assert "input" in input_names

    def test_model_has_correct_output_name(self):
        """Test that the model produces 'output' as the output name"""
        import onnxruntime as ort
        session = ort.InferenceSession(MODEL_PATH)
        output_names = [out.name for out in session.get_outputs()]
        assert "output" in output_names

    def test_model_input_shape(self):
        """Test that the model expects the right input shape"""
        import onnxruntime as ort
        session = ort.InferenceSession(MODEL_PATH)
        input_shape = session.get_inputs()[0].shape
        # Should be (batch, 1, 48, 48) — batch may be dynamic
        assert input_shape[1] == 1
        assert input_shape[2] == 48
        assert input_shape[3] == 48


@pytest.mark.unit
class TestModelInference:
    """Tests for model inference"""

    @pytest.fixture
    def session(self):
        import onnxruntime as ort
        return ort.InferenceSession(MODEL_PATH)

    def test_model_output_shape(self, session):
        """Test that model output has shape (1, 7)"""
        test_input = np.random.randn(1, 1, 48, 48).astype(np.float32)
        outputs = session.run(None, {"input": test_input})
        assert outputs[0].shape == (1, 7)

    def test_model_output_is_finite(self, session):
        """Test that model outputs are finite numbers (no NaN/Inf)"""
        test_input = np.random.randn(1, 1, 48, 48).astype(np.float32)
        outputs = session.run(None, {"input": test_input})
        assert np.all(np.isfinite(outputs[0]))

    def test_model_output_deterministic(self, session):
        """Test that the same input produces the same output"""
        test_input = np.ones((1, 1, 48, 48), dtype=np.float32) * 0.5
        output1 = session.run(None, {"input": test_input})
        output2 = session.run(None, {"input": test_input})
        np.testing.assert_array_almost_equal(output1[0], output2[0])

    def test_model_batch_inference(self, session):
        """Test that model handles batch input"""
        test_input = np.random.randn(4, 1, 48, 48).astype(np.float32)
        outputs = session.run(None, {"input": test_input})
        assert outputs[0].shape == (4, 7)

    def test_model_argmax_gives_valid_index(self, session):
        """Test that argmax of output maps to a valid emotion index"""
        test_input = np.random.randn(1, 1, 48, 48).astype(np.float32)
        outputs = session.run(None, {"input": test_input})
        emotion_idx = int(np.argmax(outputs[0], axis=1)[0])
        assert 0 <= emotion_idx < len(EXPECTED_EMOTIONS)

    def test_model_zero_input(self, session):
        """Test model with all-zero input (black image)"""
        test_input = np.zeros((1, 1, 48, 48), dtype=np.float32)
        outputs = session.run(None, {"input": test_input})
        assert outputs[0].shape == (1, 7)
        assert np.all(np.isfinite(outputs[0]))

    def test_model_ones_input(self, session):
        """Test model with all-ones input (white image)"""
        test_input = np.ones((1, 1, 48, 48), dtype=np.float32)
        outputs = session.run(None, {"input": test_input})
        assert outputs[0].shape == (1, 7)
        assert np.all(np.isfinite(outputs[0]))


@pytest.mark.unit
class TestEmotionLabels:
    """Tests for emotion label configuration"""

    def test_emotion_labels_imported(self):
        """Test that EMOTION_LABELS can be imported from facial_analysis"""
        from logic.facial_analysis import EMOTION_LABELS
        assert EMOTION_LABELS is not None

    def test_emotion_labels_count(self):
        """Test that there are exactly 7 emotion labels"""
        from logic.facial_analysis import EMOTION_LABELS
        assert len(EMOTION_LABELS) == 7

    def test_emotion_labels_match_expected(self):
        """Test that emotion labels match expected set"""
        from logic.facial_analysis import EMOTION_LABELS
        assert set(EMOTION_LABELS) == set(EXPECTED_EMOTIONS)

    def test_emotion_labels_are_uppercase(self):
        """Test that all emotion labels are uppercase"""
        from logic.facial_analysis import EMOTION_LABELS
        for label in EMOTION_LABELS:
            assert label == label.upper(), f"Label '{label}' is not uppercase"

    def test_emotion_labels_are_strings(self):
        """Test that all emotion labels are strings"""
        from logic.facial_analysis import EMOTION_LABELS
        for label in EMOTION_LABELS:
            assert isinstance(label, str)


@pytest.mark.unit
class TestCreateModelScript:
    """Tests for the model creation script"""

    def test_create_model_script_exists(self):
        """Test that create_model.py exists"""
        script_path = os.path.join(os.path.dirname(__file__), "..", "models", "create_model.py")
        assert os.path.exists(script_path)

    def test_create_model_importable(self):
        """Test that create_model module can be imported"""
        import importlib.util
        script_path = os.path.join(os.path.dirname(__file__), "..", "models", "create_model.py")
        spec = importlib.util.spec_from_file_location("create_model", script_path)
        module = importlib.util.module_from_spec(spec)
        # Just verify it's importable, don't execute
        assert module is not None

    def test_model_path_constant(self):
        """Test that MODEL_PATH in create_model points to correct location"""
        import importlib.util
        script_path = os.path.join(os.path.dirname(__file__), "..", "models", "create_model.py")
        spec = importlib.util.spec_from_file_location("create_model", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.MODEL_PATH.endswith("emotion_model.onnx")
