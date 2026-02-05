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

    def finger_print_position(self,hand_index =0)->Optional[Tuple[int,int]]:

        if not self.results or not self.results.multi_hand_landmarks:
            return None
        if hand_index >= len(self.results.multi_hand_landmarks):
            return None
        
        hand_landmarks = self.results.multi_hand_landmarks[hand_index]
        tip = hand_landmarks.landmarks[8]

        h, w, _ = self.frame_shape
        x = int(tip.x * w)
        y = int(tip.y * h)

        return (x,y)

    def get_all_landmarks(self,hand_index =0)->Optional[Tuple[int, int]]:

        if not self.results or not self.results.multi_hand_landmarks:
            return None
        if hand_index >= len(self.results.multi_hand_landmarks):
            return None

        hand_landmarks =self.results.multi_hand_landmarks[hand_index]
        h,w,_ = self.frame_shape
        x = int(tip.x * w)
        y = int(tip.y * h)

        landmarks =[]

        for landmark in hand_landmarks.landmark:
            x= int(landmark.x * w)
            y= int(landmark.y * h)
            landmarks.append((x,y))
        
        return landmarks

    def is_pinching(self,hand_index = 0, threshold = 40)->bool:

        landmarks = self.get_all_landmarks(hand_index)
        if not landmarks:
            return False
        
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]

        #Calculate the distance

        distance = np.sqrt((thumb_tip[0] - index_tip[0]) **2 +
                            (thumb_tip[1] - index_tip[1]) **2)

        return distance < threshold

    def count_fingers_up(self,hand_index = 0,)-> int:
        landmarks = slef.get_all_landmarks(hand_index)

        if not landmarks:
            return 0
        
        fingers_up = 0

        #Checks whether the thumb is in a horizontal position

        if landmarks[4][0] < landmarks[3][0]:
            fingers_up += 1

        finger_tip = [8, 12, 16 ,20]
        finger_joints = [6, 10, 14, 16]

        for tip, joint in zip(finger_tips, finger_joints):
            if landmarks[tip][1] < landmarks[joint][1]:  # Tip is above joint
                fingers_up += 1

        return fingers_up
    
    def release(self):
        self.hands.close()