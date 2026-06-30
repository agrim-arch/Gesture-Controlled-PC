import cv2
import time
import pyautogui
import numpy as np
import sys
from utils import FPSCounter, ScreenMapper, get_distance
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from pc_controller import PCController

def main():
    print("==================================================")
    print("      Gesture Controlled PC - Starting Up...     ")
    print("==================================================")
    print("Keyboard Controls:")
    print("  'q' - Quit the application")
    print("  'm' - Toggle Mouse Control Mode")
    print("  'v' - Toggle Volume Control Mode")
    print("==================================================")

    try:
        detector = HandDetector(max_hands=1, detection_con=0.7, track_con=0.7)
        recognizer = GestureRecognizer()
        pc = PCController()
        fps_counter = FPSCounter()
    except Exception as e:
        print(f"Error initializing dependencies: {e}")
        print("Please ensure you have installed all requirements: pip install -r requirements.txt")
        sys.exit(1)

    screen_w, screen_h = pyautogui.size()
    mapper = ScreenMapper(screen_w, screen_h, ema_alpha=0.15)

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    cv2.namedWindow("Gesture Controlled PC HUD", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        "Gesture Controlled PC HUD",
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )

    if not cap.isOpened():
        print("[ERROR] Could not open webcam. Please check your connection and try again.")
        sys.exit(1)

    cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    rect_w, rect_h = 320, 240
    rect_x_start = (cam_w - rect_w) // 2
    rect_y_start = (cam_h - rect_h) // 2
    rect_x_end = rect_x_start + rect_w
    rect_y_end = rect_y_start + rect_h
    active_rect = (rect_x_start, rect_y_start, rect_x_end, rect_y_end)

    mouse_mode = False
    volume_mode = False
    
    last_action = "System Ready"
    last_action_time = 0
    
    cooldowns = {
        "OPEN_PALM": 1.2,
        "FIST": 1.2,
        "PEACE": 1.2,
        "THUMB_UP": 0.3,
        "THUMB_DOWN": 0.3,
        "PINCH": 0.4
    }

    print("[INFO] Camera started successfully. Press 'q' to quit.")

    while True:
        success, frame = cap.read()
        if not success:
            print("[WARNING] Failed to grab frame.")
            continue

        frame = cv2.flip(frame, 1)

        frame = detector.find_hands(frame, draw=True)
        lm_list = detector.get_landmarks(frame)

        current_time = time.time()
        detected_gesture = "NO_HAND"
        action_triggered = "None"

        if len(lm_list) > 0:
            detected_gesture = recognizer.detect_gesture(lm_list)
            
            # --- 4. Mouse Control Mode ---
            if mouse_mode:
                # Get coordinates of Index finger tip (Landmark 8)
                ix, iy = lm_list[8][0], lm_list[8][1]
                
                # Check if index finger is inside the active zone
                in_zone = (rect_x_start <= ix <= rect_x_end) and (rect_y_start <= iy <= rect_y_end)
                
                # Draw index indicator dot
                dot_color = (0, 255, 0) if in_zone else (0, 0, 255)
                cv2.circle(frame, (ix, iy), 8, dot_color, cv2.FILLED)

                # Map cursor to screen (we map even if slightly outside, clamped by the screen mapper)
                smooth_x, smooth_y = mapper.map_and_smooth(ix, iy, active_rect)
                pc.move_mouse(smooth_x, smooth_y)

                # Mouse Click (Pinch gesture)
                if detected_gesture == "PINCH":
                    if current_time - last_action_time > cooldowns["PINCH"]:
                        pc.click()
                        last_action = "Left Click"
                        last_action_time = current_time
                        action_triggered = "Left Click"

            # --- 5. Volume Control Mode ---
            elif volume_mode:
                # Measure distance between thumb tip (4) and index tip (8)
                dist = get_distance(lm_list[4], lm_list[8])
                palm_ref = get_distance(lm_list[0], lm_list[9])
                if palm_ref == 0: palm_ref = 1
                
                # Normalize distance based on palm size
                norm_dist = dist / palm_ref
                
                # Map scale: 0.2 (closed) -> 1.2 (wide open) to 0.0 -> 1.0 volume range
                vol_val = (norm_dist - 0.2) / 1.0
                vol_val = max(0.0, min(1.0, vol_val))
                
                pc.set_volume(vol_val)
                last_action = f"Set Volume: {int(vol_val * 100)}%"
                action_triggered = f"Vol Scalar Set: {int(vol_val * 100)}%"

            # --- 6. Discrete Gesture Control (Standard Mode) ---
            else:
                if detected_gesture in cooldowns:
                    req_cooldown = cooldowns[detected_gesture]
                    if current_time - last_action_time > req_cooldown:
                        
                        if detected_gesture == "OPEN_PALM":
                            pc.play_pause()
                            last_action = "Play / Pause"
                            action_triggered = "Media Play/Pause"
                            last_action_time = current_time
                            
                        elif detected_gesture == "FIST":
                            mute_state = pc.toggle_mute()
                            last_action = f"Volume: {mute_state}"
                            action_triggered = f"Toggle Mute ({mute_state})"
                            last_action_time = current_time
                            
                        elif detected_gesture == "PEACE":
                            pc.next_track()
                            last_action = "Next Track"
                            action_triggered = "Media Next Track"
                            last_action_time = current_time
                            
                        elif detected_gesture == "THUMB_UP":
                            pc.volume_up()
                            last_action = "Volume Up"
                            action_triggered = "Vol Up (+)"
                            last_action_time = current_time
                            
                        elif detected_gesture == "THUMB_DOWN":
                            pc.volume_down()
                            last_action = "Volume Down"
                            action_triggered = "Vol Down (-)"
                            last_action_time = current_time

        # Calculate FPS
        fps = fps_counter.get_fps()

        # --- 7. HUD Rendering / UI Overlay ---
        # Dark HUD Top-Bar
        hud_overlay = frame.copy()
        cv2.rectangle(hud_overlay, (0, 0), (cam_w, 70), (20, 20, 20), -1)
        # Translucent blending
        cv2.addWeighted(hud_overlay, 0.75, frame, 0.25, 0, frame)

        # Draw Active Calibration Boundary Box (Only in mouse mode)
        if mouse_mode:
            box_color = (0, 205, 255) # Light Cyan
            cv2.rectangle(frame, (rect_x_start, rect_y_start), (rect_x_end, rect_y_end), box_color, 2)
            cv2.putText(frame, "ACTIVE SAFETY ZONE", (rect_x_start, rect_y_start - 8), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 1)

        # Top Bar Info
        # FPS
        cv2.putText(frame, f"FPS: {fps}", (cam_w - 90, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        # Gesture Name
        cv2.putText(frame, f"GESTURE: {detected_gesture}", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        # Executed Action
        cv2.putText(frame, f"ACTION: {last_action}", (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Mode status (Mouse/Volume)
        # Draw small bottom bar
        cv2.rectangle(frame, (0, cam_h - 40), (cam_w, cam_h), (30, 30, 30), -1)
        
        # MOUSE Mode Indicator
        m_color = (57, 255, 20) if mouse_mode else (128, 128, 128)
        m_text = "MOUSE [ON]" if mouse_mode else "MOUSE [OFF]"
        cv2.putText(frame, m_text, (20, cam_h - 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, m_color, 2)
        
        # VOLUME Mode Indicator
        v_color = (0, 205, 255) if volume_mode else (128, 128, 128)
        v_text = "VOL MODE [ON]" if volume_mode else "VOL MODE [OFF]"
        cv2.putText(frame, v_text, (200, cam_h - 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, v_color, 2)

        # Cooldown Timer Indicator
        cooldown_elapsed = current_time - last_action_time
        if cooldown_elapsed < 1.0 and not mouse_mode and not volume_mode and last_action != "System Ready":
            # Show a red 'cooldown' overlay
            cv2.putText(frame, "COOLDOWN", (cam_w - 220, cam_h - 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Exit Instruction
        cv2.putText(frame, "Press 'Q' to Exit", (cam_w - 150, cam_h - 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Volume Bar (Vertical HUD overlay on the right, only in Volume mode)
        if volume_mode:
            vol_scalar = pc.get_volume()
            vol_pct = int(vol_scalar * 100)
            
            # Position of volume bar
            bar_x = cam_w - 40
            bar_y_start = 120
            bar_y_end = cam_h - 80
            bar_height = bar_y_end - bar_y_start
            
            # Draw empty background bar
            cv2.rectangle(frame, (bar_x, bar_y_start), (bar_x + 20, bar_y_end), (50, 50, 50), -1)
            # Calculate filled volume height
            fill_y = bar_y_end - int(vol_scalar * bar_height)
            # Draw filled progress bar
            cv2.rectangle(frame, (bar_x, fill_y), (bar_x + 20, bar_y_end), (0, 205, 255), -1)
            # Text volume percentage
            cv2.putText(frame, f"{vol_pct}%", (bar_x - 35, fill_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 205, 255), 1)

        # Display Frame
        cv2.imshow("Gesture Controlled PC HUD", frame)

        # --- 8. Key Controls Handler ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            mouse_mode = not mouse_mode
            if mouse_mode:
                volume_mode = False  # Deactivate volume mode if mouse mode is toggled
            print(f"[TOGGLE] Mouse Mode: {mouse_mode}")
        elif key == ord('v'):
            volume_mode = not volume_mode
            if volume_mode:
                mouse_mode = False  # Deactivate mouse mode if volume mode is toggled
            print(f"[TOGGLE] Volume Mode: {volume_mode}")

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("==================================================")
    print("      Gesture Controlled PC - Shutting Down.     ")
    print("==================================================")

if __name__ == "__main__":
    main()
