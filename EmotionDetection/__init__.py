"""Public interface for the EmotionDetection package."""

from .emotion_detection import EmotionServiceError, emotion_detector

__all__ = ["EmotionServiceError", "emotion_detector"]
