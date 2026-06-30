import cv2
import mediapipe as mp

class HandDetector:
    """
    A class to encapsulate MediaPipe Hands detection functionality.
    """
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.7):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, img, draw=True):
        """
        Processes the image and detects hand landmarks.
        Optionally draws the landmarks and connections on the image.
        """
        # Convert the BGR image to RGB as required by MediaPipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_lms, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
        return img

    def get_landmarks(self, img):
        """
        Returns a list of landmark coordinates (x, y) in pixel values.
        Returns an empty list if no hand is detected.
        """
        lm_list = []
        if self.results and self.results.multi_hand_landmarks:
            # We track the first hand detected
            my_hand = self.results.multi_hand_landmarks[0]
            h, w, c = img.shape
            for lm in my_hand.landmark:
                # Convert normalized coordinates to pixel coordinates
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))
        return lm_list
