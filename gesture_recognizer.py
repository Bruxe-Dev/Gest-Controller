import numpy as np
from collections import deque
from typing import Tuple,Optional

class GestureRecognizer:

    def __init__(self,history_size =10):

        self.position_history = deque(maxlen=history_size)
        self.last_gesture = None
        self.gesture_cooldown = 0
        self.cooldown_frames = 15

    def update(self,position: Optional[Tuple[int,int]]):
        if position:
            self.position_history.append(position)

        if gesture_cooldown > 0:
            self.gesture_cooldown -= 1

    def detectSwipe(self, direction = 'any', threshold = 100)-> Optional[str]:
        if len(self.position_history) < 5:
            return None
        
        start = self.position_history[0]
        end = self.position_history[-1]

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        distance = np.sqrt(dx**2 + dy**2)

        if distance < threshold:
            return None

        if abs(dx) > abs(dy):
            detected_direction = 'right' if dx > 0 else 'left'
        else:
            detected_direction = 'down' if dy > 0 else 'up'

        if direction == 'any' or direction == detected_direction:
            if self.gesture_cooldown == 0:
                self.gesture_cooldown = self.cooldown_frames
                return detected_direction
        
        return None


    def detectPush(self, threshold = 150) -> bool:

        if len(self.position_history) < 5:
            return False
        
        start  = self.position_history[0]
        end = self.position_history[-1]

        dy = end[1] - start[1]

        if dy > threshold and self.gesture_cooldown ==0 :
            self.gesture_cooldown = self.cooldown_frames
            return True

        return False

    
    def detectPull(self ,threshold =150) -> bool:

        if len(self.position_history) < 5:
            return False
        
        start = self.position_history[0]
        end = self.position_history[-1]

        dx = end[1] - start[1]

        if dx < -threshold and self.gesture_cooldown == 0:
            self.gesture_cooldown = self.cooldown_frames
            return True

        return False


    def detect_cirlce(self, threshold = 200)-> Optional[str]:

        if len(self.position_history) < 8:
            return None

        total_distance = 0
        for i in range( 1, len(self.position_history)):
            p1 = self.position_history[i-1]
            p2 = self.position_history[i]
            total_distance = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        if total_distance < threshold:
            return None
        
                # Check if start and end are close (closed loop)
        start = self.position_history[0]
        end = self.position_history[-1]
        closure_distance = np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
        
        if closure_distance < 50:  # Points are close = closed loop
            # Determine direction using cross product
            cross_sum = 0
            for i in range(1, len(self.position_history)):
                p1 = self.position_history[i-1]
                p2 = self.position_history[i]
                cross_sum += (p2[0] - p1[0]) * (p2[1] + p1[1])
            
            if self.gesture_cooldown == 0:
                self.gesture_cooldown = self.cooldown_frames
                return 'clockwise' if cross_sum > 0 else 'counterclockwise'
        
        return None

    def reset(self):
        self.position_history.clear()
        self.gesture_cooldown = 0