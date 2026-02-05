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
    
    def find_hands(self,frame,draw =True):
        #Convert to RGB for Mediapipe

        rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        self.frame_shape = frame.shape

        #Result processing
        self.results =self.hands.process(rgb_frame)

            # Draw hand landmarks if requested
        if draw and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        
        return frame