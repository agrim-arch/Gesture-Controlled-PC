import math
from utils import get_distance

class GestureRecognizer:
    """
    Analyzes hand landmarks and recognizes gestures.
    """
    def __init__(self):
        pass

    def get_finger_states(self, lm_list):
        """
        Returns a list of booleans indicating if fingers are up:
        [thumb, index, middle, ring, pinky]
        """
        if len(lm_list) < 21:
            return [False] * 5

        # Normalization reference: wrist (0) to middle MCP (9)
        palm_reference = get_distance(lm_list[0], lm_list[9])
        if palm_reference == 0:
            palm_reference = 1

        # Check fingers (Index, Middle, Ring, Pinky)
        # Finger is up if the tip (8, 12, 16, 20) is above the PIP joint (6, 10, 14, 18)
        # In screen coords, higher is lower y-value.
        index_up = lm_list[8][1] < lm_list[6][1]
        middle_up = lm_list[12][1] < lm_list[10][1]
        ring_up = lm_list[16][1] < lm_list[14][1]
        pinky_up = lm_list[20][1] < lm_list[18][1]

        # Check thumb
        # For thumb, check distance between thumb tip (4) and index MCP (5) relative to palm size.
        # If it's extended, the distance is large.
        thumb_index_dist = get_distance(lm_list[4], lm_list[5])
        thumb_up = thumb_index_dist > (0.6 * palm_reference)

        return [thumb_up, index_up, middle_up, ring_up, pinky_up]

    def detect_gesture(self, lm_list):
        """
        Determines the current gesture based on finger states and relative positions.
        """
        if len(lm_list) < 21:
            return "NO_HAND"

        fingers = self.get_finger_states(lm_list)
        
        palm_reference = get_distance(lm_list[0], lm_list[9])
        if palm_reference == 0:
            palm_reference = 1

        # 1. Open Palm: All fingers up
        if all(fingers):
            return "OPEN_PALM"

        # 2. Fist: All fingers down
        if not any(fingers):
            return "FIST"

        # 3. Peace Sign: Index and Middle up, others down
        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            return "PEACE"

        # 4. Index Finger Only: Only Index up (and thumb is close/not extended)
        if fingers[1] and not fingers[2] and not fingers[3] and not fingers[4] and not fingers[0]:
            return "INDEX_ONLY"

        # 5. Thumb Up / Thumb Down (when only thumb is up, others are down)
        if fingers[0] and not fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
            # Compare thumb tip (4) to thumb MCP (2)
            if lm_list[4][1] < lm_list[2][1]:
                return "THUMB_UP"
            elif lm_list[4][1] > lm_list[2][1]:
                return "THUMB_DOWN"

        # 6. Pinch Gesture: Check if Thumb (4) and Index (8) are extremely close
        # (This is used for mouse clicks and active volume adjustment)
        pinch_dist = get_distance(lm_list[4], lm_list[8])
        if pinch_dist < (0.15 * palm_reference):
            return "PINCH"

        return "UNKNOWN"
