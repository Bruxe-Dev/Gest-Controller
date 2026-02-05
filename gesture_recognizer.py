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