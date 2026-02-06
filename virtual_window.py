import cv2
import numpy as np
from typing import List, Tuple, Optional

class VirtualWindow:
    """Represents a draggable window in the virtual desktop"""
    
    def __init__(self, x, y, width, height, title, color):
 
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.color = color
        self.is_active = False
        self.is_minimized = False
        self.original_pos = (x, y)
        
    def contains_point(self, px, py) -> bool:
        """Check if point is inside window"""
        if self.is_minimized:
            return False
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)
    
    def in_title_bar(self, px, py) -> bool:
        """Check if point is in title bar"""
        if self.is_minimized:
            return False
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + 30)
    
    def move(self, dx, dy):
        """Move window by delta"""
        self.x += dx
        self.y += dy
        
    def set_position(self, x, y):
        """Set window position"""
        self.x = x
        self.y = y
    
    def toggle_minimize(self):
        """Minimize or restore window"""
        self.is_minimized = not self.is_minimized


class VirtualDesktop:
    """Simulated desktop environment with windows and taskbar"""
    
    def __init__(self, width=1280, height=720):

        self.width = width
        self.height = height
        self.windows: List[VirtualWindow] = []
        self.active_window: Optional[VirtualWindow] = None
        self.dragging = False
        self.drag_offset = (0, 0)
        
        # Create some demo windows
        self._create_demo_windows()
        
        # Status message
        self.status_message = "Welcome! Use hand gestures to control windows"
        self.message_timer = 0
        
    def _create_demo_windows(self):
        """Create initial demo windows"""
        self.windows = [
            VirtualWindow(100, 100, 300, 200, "Notes", (230, 216, 173)),
            VirtualWindow(450, 150, 350, 250, "Browser", (173, 216, 230)),
            VirtualWindow(250, 350, 280, 180, "Music", (216, 191, 216)),
        ]
    
    def render(self) -> np.ndarray:

        # Create desktop background
        desktop = np.ones((self.height, self.width, 3), dtype=np.uint8) * 60
        
        # Draw a gradient background
        for i in range(self.height):
            intensity = int(60 + (i / self.height) * 40)
            desktop[i, :] = (intensity, intensity, intensity)
        
        # Draw all non-minimized windows (back to front)
        for window in self.windows:
            if not window.is_minimized:
                self._draw_window(desktop, window)
        
        # Draw taskbar
        self._draw_taskbar(desktop)
        
        # Draw status message
        if self.message_timer > 0:
            self._draw_status(desktop)
            self.message_timer -= 1
        
        return desktop
    
    def _draw_window(self, canvas, window):
        """Draw a single window"""
        x, y, w, h = window.x, window.y, window.width, window.height
        
        # Ensure window stays in bounds
        x = max(0, min(x, self.width - w))
        y = max(0, min(y, self.height - 60 - h))  # Account for taskbar
        
        # Draw shadow
        shadow_offset = 5
        cv2.rectangle(canvas, 
                     (x + shadow_offset, y + shadow_offset),
                     (x + w + shadow_offset, y + h + shadow_offset),
                     (30, 30, 30), -1)
        
        # Draw window body
        cv2.rectangle(canvas, (x, y), (x + w, y + h), window.color, -1)
        
        # Draw title bar
        title_color = tuple(int(c * 0.7) for c in window.color)
        cv2.rectangle(canvas, (x, y), (x + w, y + 30), title_color, -1)
        
        # Draw title text
        cv2.putText(canvas, window.title, (x + 10, y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw close button
        cv2.rectangle(canvas, (x + w - 25, y + 5), (x + w - 5, y + 25),
                     (0, 0, 200), -1)
        cv2.putText(canvas, "X", (x + w - 20, y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Draw minimize button
        cv2.rectangle(canvas, (x + w - 50, y + 5), (x + w - 30, y + 25),
                     (200, 200, 0), -1)
        cv2.putText(canvas, "_", (x + w - 45, y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Active window indicator
        if window.is_active:
            cv2.rectangle(canvas, (x-2, y-2), (x + w+2, y + h+2),
                         (0, 255, 0), 3)
    
    def _draw_taskbar(self, canvas):
        """Draw the taskbar at the bottom"""
        taskbar_height = 50
        taskbar_y = self.height - taskbar_height
        
        # Taskbar background
        cv2.rectangle(canvas, (0, taskbar_y), (self.width, self.height),
                     (40, 40, 40), -1)
        
        # Draw window buttons in taskbar
        button_x = 10
        for window in self.windows:
            button_width = 100
            button_color = window.color if not window.is_minimized else (80, 80, 80)
            
            cv2.rectangle(canvas, (button_x, taskbar_y + 10),
                         (button_x + button_width, taskbar_y + 40),
                         button_color, -1)
            
            # Truncate long titles
            title = window.title[:8] + "..." if len(window.title) > 8 else window.title
            cv2.putText(canvas, title, (button_x + 5, taskbar_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            button_x += button_width + 10
    
    def _draw_status(self, canvas):
        """Draw status message"""
        msg_height = 40
        msg_y = self.height - 60 - msg_height
        
        # Semi-transparent background
        overlay = canvas.copy()
        cv2.rectangle(overlay, (10, msg_y), (self.width - 10, msg_y + msg_height),
                     (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, canvas, 0.3, 0, canvas)
        
        # Message text
        cv2.putText(canvas, self.status_message, (20, msg_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    def handle_cursor(self, x, y, is_pinching):

        clicked_window = None
        for window in reversed(self.windows):  # Check from front to back
            if window.contains_point(x, y):
                clicked_window = window
                break
        
        if is_pinching:
            if not self.dragging and clicked_window:
                # Start dragging
                if clicked_window.in_title_bar(x, y):
                    self.dragging = True
                    self.active_window = clicked_window
                    self.drag_offset = (x - clicked_window.x, y - clicked_window.y)
                    self._bring_to_front(clicked_window)
                    clicked_window.is_active = True
        else:
            # Release drag
            self.dragging = False
        
        # Update dragging
        if self.dragging and self.active_window:
            new_x = x - self.drag_offset[0]
            new_y = y - self.drag_offset[1]
            self.active_window.set_position(new_x, new_y)
    
    def _bring_to_front(self, window):
        """Bring window to front"""
        if window in self.windows:
            self.windows.remove(window)
            self.windows.append(window)
            
            # Deactivate other windows
            for w in self.windows:
                if w != window:
                    w.is_active = False
    
    def handle_swipe(self, direction):
        """Handle swipe gestures"""
        if not self.active_window:
            # Activate first window if none active
            if self.windows:
                self.active_window = self.windows[-1]
                self.active_window.is_active = True
            return
        
        move_amount = 50
        if direction == 'left':
            self.active_window.move(-move_amount, 0)
            self.set_status(f"Moved {self.active_window.title} left")
        elif direction == 'right':
            self.active_window.move(move_amount, 0)
            self.set_status(f"Moved {self.active_window.title} right")
        elif direction == 'up':
            self.active_window.move(0, -move_amount)
            self.set_status(f"Moved {self.active_window.title} up")
        elif direction == 'down':
            self.active_window.move(0, move_amount)
            self.set_status(f"Moved {self.active_window.title} down")
    
    def handle_push(self):
        """Handle push gesture - maximize window"""
        if self.active_window:
            self.active_window.width = min(self.active_window.width + 50, 600)
            self.active_window.height = min(self.active_window.height + 40, 400)
            self.set_status(f"Enlarged {self.active_window.title}")
    
    def handle_pull(self):
        """Handle pull gesture - minimize window"""
        if self.active_window:
            self.active_window.width = max(self.active_window.width - 50, 200)
            self.active_window.height = max(self.active_window.height - 40, 150)
            self.set_status(f"Shrunk {self.active_window.title}")
    
    def set_status(self, message):
        """Set status message"""
        self.status_message = message
        self.message_timer = 60  # Show for 60 frames (2 seconds)