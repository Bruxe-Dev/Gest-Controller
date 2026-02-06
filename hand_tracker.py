import cv2
import numpy as np
from typing import Optional, Tuple, List
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker:
    
    def __init__(self, max_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5):

        # Create hand landmarker options
        base_options = python.BaseOptions(model_asset_path=self._download_model())
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Initialize the hand landmarker
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        
        self.results = None
        self.frame_shape = None
        self.timestamp_ms = 0
        
    def _download_model(self):
        """Download the hand landmark model if needed"""
        import urllib.request
        import os
        
        model_path = "hand_landmarker.task"
        
        if not os.path.exists(model_path):
            print("Downloading hand landmark model (one-time setup)...") 
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            try:
                urllib.request.urlretrieve(url, model_path)
                print("✓ Model downloaded successfully!")
            except Exception as e:
                print(f"Error downloading model: {e}")
                print("Please download manually from:")
                print(url)
                raise
        
        return model_path
    
    def find_hands(self, frame, draw=True):

        self.frame_shape = frame.shape
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Process the frame
        self.timestamp_ms += 33  # Approximate 30 fps
        self.results = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)
        
        # Draw hand landmarks if requested
        if draw and self.results.hand_landmarks:
            for hand_landmarks in self.results.hand_landmarks:
                self._draw_landmarks(frame, hand_landmarks)
        
        return frame
    
    def _draw_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks on frame"""
        h, w, _ = frame.shape
        
        # Convert normalized landmarks to pixel coordinates
        landmark_list = []
        for landmark in hand_landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            landmark_list.append((x, y))
        
        # Draw connections
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index finger
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle finger
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring finger
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky
            (0, 17), (17, 18), (18, 19), (19, 20),
            # Palm
            (5, 9), (9, 13), (13, 17)
        ]
        
        for start, end in connections:
            cv2.line(frame, landmark_list[start], landmark_list[end], (0, 255, 0), 2)
        
        # Draw landmarks
        for x, y in landmark_list:
            cv2.circle(frame, (x, y), 5, (255, 0, 255), -1)
    
    def get_finger_tip_position(self, hand_index=0) -> Optional[Tuple[int, int]]:
        """
        Get the position of the index finger tip
        
        Args:
            hand_index: Which hand to get (0 for first detected hand)
            
        Returns:
            (x, y) position in pixels, or None if no hand detected
        """
        if not self.results or not self.results.hand_landmarks:
            return None
        
        if hand_index >= len(self.results.hand_landmarks):
            return None
        
        # Index finger tip is landmark 8
        hand_landmarks = self.results.hand_landmarks[hand_index]
        tip = hand_landmarks[8]
        
        # Convert normalized coordinates to pixel coordinates
        h, w, _ = self.frame_shape
        x = int(tip.x * w)
        y = int(tip.y * h)
        
        return (x, y)
    
    def get_all_landmarks(self, hand_index=0) -> Optional[List[Tuple[int, int]]]:
        """
        Get all 21 hand landmarks
        
        Returns:
            List of (x, y) positions for all landmarks, or None
        """
        if not self.results or not self.results.hand_landmarks:
            return None
        
        if hand_index >= len(self.results.hand_landmarks):
            return None
        
        hand_landmarks = self.results.hand_landmarks[hand_index]
        h, w, _ = self.frame_shape
        
        landmarks = []
        for landmark in hand_landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            landmarks.append((x, y))
        
        return landmarks
    
    def is_pinching(self, hand_index=0, threshold=40) -> bool:
        """
        Detect if thumb and index finger are pinched together
        
        Args:
            hand_index: Which hand to check
            threshold: Maximum distance in pixels to consider as pinch
            
        Returns:
            True if pinching, False otherwise
        """
        landmarks = self.get_all_landmarks(hand_index)
        if not landmarks:
            return False
        
        # Thumb tip is landmark 4, index finger tip is landmark 8
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Calculate Euclidean distance
        distance = np.sqrt((thumb_tip[0] - index_tip[0])**2 + 
                          (thumb_tip[1] - index_tip[1])**2)
        
        return distance < threshold
    
    def count_fingers_up(self, hand_index=0) -> int:
        """
        Count how many fingers are extended
        
        Returns:
            Number of fingers up (0-5)
        """
        landmarks = self.get_all_landmarks(hand_index)
        if not landmarks:
            return 0
        
        fingers_up = 0
        
        # Determine handedness (left or right hand)
        # For simplicity, we'll use a basic check
        # If wrist is left of middle finger base, it's likely right hand
        wrist_x = landmarks[0][0]
        middle_base_x = landmarks[9][0]
        is_right_hand = wrist_x < middle_base_x
        
        # Thumb - special case (horizontal check)
        if is_right_hand:
            if landmarks[4][0] > landmarks[3][0]:  # Thumb tip right of thumb joint
                fingers_up += 1
        else:
            if landmarks[4][0] < landmarks[3][0]:  # Thumb tip left of thumb joint
                fingers_up += 1
        
        # Other fingers - check if tip is above the middle joint
        finger_tips = [8, 12, 16, 20]  # Index, middle, ring, pinky tips
        finger_joints = [6, 10, 14, 18]  # Corresponding joints
        
        for tip, joint in zip(finger_tips, finger_joints):
            if landmarks[tip][1] < landmarks[joint][1]:  # Tip is above joint
                fingers_up += 1
        
        return fingers_up
    
    def release(self):
        """Release resources"""
        self.landmarker.close()