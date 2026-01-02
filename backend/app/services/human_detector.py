"""
Human Detection Service

Filters video frames to keep only those containing human presence.
Uses MediaPipe for face, hand, and pose detection.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import mediapipe as mp

from app.models.health_observation import (
    BodyRegion,
    ExtractedFrame,
    HumanDetectionResult,
)

logger = logging.getLogger(__name__)


class HumanDetector:
    """Detects human presence in video frames using MediaPipe."""

    def __init__(self):
        # Initialize MediaPipe solutions
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose

        # Detection instances (lazy initialization)
        self._face_detector: Optional[mp.solutions.face_detection.FaceDetection] = None
        self._hand_detector: Optional[mp.solutions.hands.Hands] = None
        self._pose_detector: Optional[mp.solutions.pose.Pose] = None

    @property
    def face_detector(self):
        if self._face_detector is None:
            self._face_detector = self.mp_face_detection.FaceDetection(
                model_selection=1,  # Full range model (better for various distances)
                min_detection_confidence=0.5
            )
        return self._face_detector

    @property
    def hand_detector(self):
        if self._hand_detector is None:
            self._hand_detector = self.mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.5
            )
        return self._hand_detector

    @property
    def pose_detector(self):
        if self._pose_detector is None:
            self._pose_detector = self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=1,
                min_detection_confidence=0.5
            )
        return self._pose_detector

    def detect_humans(self, frame_path: Path) -> HumanDetectionResult:
        """
        Detect if frame contains humans and which body regions are visible.

        Args:
            frame_path: Path to the image file

        Returns:
            HumanDetectionResult with detection details
        """
        # Load image
        image = cv2.imread(str(frame_path))
        if image is None:
            logger.warning(f"Could not load image: {frame_path}")
            return HumanDetectionResult(has_human=False)

        # Convert to RGB (MediaPipe uses RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_detected, face_confidence = self._detect_faces(rgb_image)

        # Detect hands
        hands_detected, hand_confidence = self._detect_hands(rgb_image)

        # Detect body/pose
        body_detected, pose_confidence = self._detect_pose(rgb_image)

        # Determine which body regions are visible
        body_regions = []
        if face_detected:
            body_regions.extend([BodyRegion.FACE, BodyRegion.EYES, BodyRegion.SKIN])
        if hands_detected:
            body_regions.append(BodyRegion.HANDS)
        if body_detected:
            body_regions.append(BodyRegion.POSTURE)
            if BodyRegion.SKIN not in body_regions:
                body_regions.append(BodyRegion.SKIN)
            # Neck is often visible with body detection
            body_regions.append(BodyRegion.NECK)

        # Remove duplicates while preserving order
        body_regions = list(dict.fromkeys(body_regions))

        has_human = face_detected or hands_detected or body_detected

        # Calculate overall confidence
        confidences = []
        if face_detected:
            confidences.append(face_confidence)
        if hands_detected:
            confidences.append(hand_confidence)
        if body_detected:
            confidences.append(pose_confidence)

        overall_confidence = max(confidences) if confidences else 0.0

        return HumanDetectionResult(
            has_human=has_human,
            face_detected=face_detected,
            hands_detected=hands_detected,
            body_detected=body_detected,
            body_regions=body_regions,
            detection_confidence=overall_confidence
        )

    def _detect_faces(self, rgb_image) -> Tuple[bool, float]:
        """Detect faces in the image."""
        try:
            results = self.face_detector.process(rgb_image)
            if results.detections:
                # Get highest confidence detection
                max_confidence = max(d.score[0] for d in results.detections)
                return True, max_confidence
        except Exception as e:
            logger.warning(f"Face detection error: {e}")
        return False, 0.0

    def _detect_hands(self, rgb_image) -> Tuple[bool, float]:
        """Detect hands in the image."""
        try:
            results = self.hand_detector.process(rgb_image)
            if results.multi_hand_landmarks:
                # MediaPipe hands doesn't provide confidence scores directly
                # but presence of landmarks indicates detection
                return True, 0.7  # Default confidence
        except Exception as e:
            logger.warning(f"Hand detection error: {e}")
        return False, 0.0

    def _detect_pose(self, rgb_image) -> Tuple[bool, float]:
        """Detect body pose in the image."""
        try:
            results = self.pose_detector.process(rgb_image)
            if results.pose_landmarks:
                # Count visible landmarks with good confidence
                visible_count = sum(
                    1 for lm in results.pose_landmarks.landmark
                    if lm.visibility > 0.5
                )
                # If we have at least some visible body landmarks
                if visible_count > 5:
                    avg_visibility = sum(
                        lm.visibility for lm in results.pose_landmarks.landmark
                    ) / len(results.pose_landmarks.landmark)
                    return True, avg_visibility
        except Exception as e:
            logger.warning(f"Pose detection error: {e}")
        return False, 0.0

    def filter_frames(
        self,
        frames: List[ExtractedFrame],
        require_face: bool = False
    ) -> List[Tuple[ExtractedFrame, HumanDetectionResult]]:
        """
        Filter frames to keep only those with human presence.

        Args:
            frames: List of extracted frames to filter
            require_face: If True, only keep frames with faces detected

        Returns:
            List of (frame, detection_result) tuples for frames with humans
        """
        filtered = []

        for frame in frames:
            detection = self.detect_humans(Path(frame.frame_path))

            if require_face:
                if detection.face_detected:
                    filtered.append((frame, detection))
            else:
                if detection.has_human:
                    filtered.append((frame, detection))

        logger.info(
            f"Filtered {len(frames)} frames to {len(filtered)} with human presence"
        )
        return filtered

    def close(self):
        """Release MediaPipe resources."""
        if self._face_detector:
            self._face_detector.close()
        if self._hand_detector:
            self._hand_detector.close()
        if self._pose_detector:
            self._pose_detector.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
