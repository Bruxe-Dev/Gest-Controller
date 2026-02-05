import cv2
import mediapipe as mediapipe
import numpy as np
from typing import Optional, Tuple ,List

class HandTracker:
    """This will help track hand landmarks nad provide gesture detection capabilities"""
    
    def __init__(self, max_hands=1,min_detection_confidence=0.75, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        self.hands =self.mp.hands.Hands(
            static_image_mode = False,
            max_num_hands = num_hands,
            min_detection_confidence = min_detection_confidence,
            min_tracking_confidence = min_tracking_confidence
        )

        self.results =None
        self.frame_shape =None
    
    