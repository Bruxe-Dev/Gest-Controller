import cv2
import numpy as np
from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from virtual_window import VirtualDesktop

class GestureControlApp:
    """Main application coordinating all components"""
    
    def __init__(self, camera_id= 0):

        self.hand_tracker = HandTracker(max_hands=1)
        self.gesture_recognizer = GestureRecognizer(history_size=10)
        self.virtual_desktop = VirtualDesktop(width=1280, height=720)
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # State
        self.running = True
        self.show_camera = True
        self.cursor_position = None
        
        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        
    def run(self):
        """Main application loop"""
        print("\n" + "="*60)
        print("GESTURE CONTROL SYSTEM - VIRTUAL DESKTOP MODE")
        print("="*60)
        print("\nControls:")
        print("  - Point with index finger to move cursor")
        print("  - Pinch (thumb + index) to grab and drag windows")
        print("  - Open hand (5 fingers) then swipe to move active window")
        print("  - Move hand toward camera (push) to enlarge window")
        print("  - Move hand away (pull) to shrink window")
        print("\nKeyboard:")
        print("  - 'c' : Toggle camera view")
        print("  - 'r' : Reset window positions")
        print("  - 'q' : Quit")
        print("="*60 + "\n")
        
        cv2.namedWindow("Virtual Desktop", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Virtual Desktop", 1280, 720)
        
        import time
        last_time = time.time()
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame from camera")
                break
            
            # Mirror the frame for natural interaction
            frame = cv2.flip(frame, 1)
            
            # Process hand tracking
            frame = self.hand_tracker.find_hands(frame, draw=True)
            
            # Get finger tip position
            finger_pos = self.hand_tracker.get_finger_tip_position()
            
            # Update gesture recognizer
            self.gesture_recognizer.update(finger_pos)
            
            # Map webcam coordinates to desktop coordinates
            if finger_pos:
                # Map from webcam (640x480) to desktop (1280x720)
                desktop_x = int((finger_pos[0] / 640) * 1280)
                desktop_y = int((finger_pos[1] / 480) * 720)
                self.cursor_position = (desktop_x, desktop_y)
            
            # Check for pinch gesture (for clicking/dragging)
            is_pinching = self.hand_tracker.is_pinching()
            
            # Handle cursor interaction
            if self.cursor_position:
                self.virtual_desktop.handle_cursor(
                    self.cursor_position[0],
                    self.cursor_position[1],
                    is_pinching
                )
            
            # Detect gestures
            # Only detect swipes when hand is open (5 fingers up)
            fingers_up = self.hand_tracker.count_fingers_up()
            
            if fingers_up == 5:  # Open hand for swipe gestures
                swipe_direction = self.gesture_recognizer.detect_swipe()
                if swipe_direction:
                    self.virtual_desktop.handle_swipe(swipe_direction)
            
            # Push/Pull gestures
            if self.gesture_recognizer.detect_push():
                self.virtual_desktop.handle_push()
            
            if self.gesture_recognizer.detect_pull():
                self.virtual_desktop.handle_pull()
            
            # Render virtual desktop
            desktop_frame = self.virtual_desktop.render()
            
            # Draw cursor on desktop
            if self.cursor_position:
                cursor_color = (0, 255, 0) if is_pinching else (255, 255, 0)
                cv2.circle(desktop_frame, self.cursor_position, 15, cursor_color, -1)
                cv2.circle(desktop_frame, self.cursor_position, 17, (255, 255, 255), 2)
            
            # Draw info overlay
            self._draw_info_overlay(desktop_frame, fingers_up, is_pinching)
            
            # Show camera feed (optional)
            if self.show_camera:
                # Resize camera feed to fit in corner
                small_frame = cv2.resize(frame, (320, 240))
                desktop_frame[10:250, 10:330] = small_frame
                cv2.rectangle(desktop_frame, (10, 10), (330, 250), (0, 255, 0), 2)
            
            # Calculate FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                last_time = current_time
            
            # Show FPS
            cv2.putText(desktop_frame, f"FPS: {self.fps}", (10, desktop_frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Display
            cv2.imshow("Virtual Desktop", desktop_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
            elif key == ord('c'):
                self.show_camera = not self.show_camera
            elif key == ord('r'):
                self.virtual_desktop._create_demo_windows()
                self.virtual_desktop.set_status("Windows reset to default positions")
        
        self.cleanup()
    
    def _draw_info_overlay(self, frame, fingers_up, is_pinching):
        """Draw information overlay"""
        info_y = 270 if self.show_camera else 20
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, info_y), (350, info_y + 130),
                     (40, 40, 40), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw info text
        y_offset = info_y + 25
        cv2.putText(frame, "GESTURE STATUS", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        y_offset += 30
        cv2.putText(frame, f"Fingers Up: {fingers_up}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        y_offset += 25
        pinch_status = "YES (Grabbing)" if is_pinching else "NO"
        pinch_color = (0, 255, 0) if is_pinching else (255, 255, 255)
        cv2.putText(frame, f"Pinching: {pinch_status}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, pinch_color, 1)
        
        y_offset += 25
        cursor_status = f"({self.cursor_position[0]}, {self.cursor_position[1]})" if self.cursor_position else "N/A"
        cv2.putText(frame, f"Cursor: {cursor_status}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def cleanup(self):
        """Release resources"""
        print("\nCleaning up...")
        self.cap.release()
        self.hand_tracker.release()
        cv2.destroyAllWindows()
        print("Application closed successfully!")


def main():
    """Entry point"""
    try:
        app = GestureControlApp(camera_id=0)
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()