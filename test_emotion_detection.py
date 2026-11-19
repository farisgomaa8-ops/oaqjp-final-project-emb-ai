"""Required live tests: run these where the Skills Network Watson API is reachable.

These tests use the real service; they are not part of the offline test suite.
An unavailable service is reported as a test error rather than a successful test.
"""

import unittest

from EmotionDetection import emotion_detector


class TestEmotionDetection(unittest.TestCase):
    """Check the five statements and dominant emotions listed in the lab."""

    def test_joy(self):
        """The lab's positive statement should have joy as its dominant emotion."""
        result = emotion_detector("I am glad this happened")
        self.assertEqual(result["dominant_emotion"], "joy")

    def test_anger(self):
        """The lab's angry statement should have anger as its dominant emotion."""
        result = emotion_detector("I am really mad about this")
        self.assertEqual(result["dominant_emotion"], "anger")

    def test_disgust(self):
        """The lab's disgust statement should have disgust as its dominant emotion."""
        result = emotion_detector("I feel disgusted just hearing about this")
        self.assertEqual(result["dominant_emotion"], "disgust")

    def test_sadness(self):
        """The lab's sad statement should have sadness as its dominant emotion."""
        result = emotion_detector("I am so sad about this")
        self.assertEqual(result["dominant_emotion"], "sadness")

    def test_fear(self):
        """The lab's fearful statement should have fear as its dominant emotion."""
        result = emotion_detector("I am really afraid that this will happen")
        self.assertEqual(result["dominant_emotion"], "fear")


if __name__ == "__main__":
    unittest.main()
