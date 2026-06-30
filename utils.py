import math
import time
import cv2
import numpy as np

def get_distance(p1, p2):
    """
    Calculates Euclidean distance between two 2D points.
    """
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

class FPSCounter:
    """
    Calculates and tracks Frames Per Second.
    """
    def __init__(self):
        self.prev_time = 0

    def get_fps(self):
        current_time = time.time()
        fps = 0
        if self.prev_time != 0:
            fps = 1 / (current_time - self.prev_time)
        self.prev_time = current_time
        return int(fps)

class ScreenMapper:
    """
    Maps webcam coordinates to screen coordinates with smoothing.
    """
    def __init__(self, screen_w, screen_h, ema_alpha=0.2):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.ema_alpha = ema_alpha  # Smoothing factor (lower = smoother but slower)
        self.prev_x = 0
        self.prev_y = 0

    def map_and_smooth(self, x, y, active_rect):
        """
        Maps coordinates from the active calibration rectangle to the screen.
        Applies Exponential Moving Average (EMA) smoothing.
        
        active_rect: (x_start, y_start, x_end, y_end) normalized or absolute coordinates
        """
        rx_start, ry_start, rx_end, ry_end = active_rect
        rect_w = rx_end - rx_start
        rect_h = ry_end - ry_start

        clamped_x = max(rx_start, min(x, rx_end))
        clamped_y = max(ry_start, min(y, ry_end))

        norm_x = (clamped_x - rx_start) / rect_w
        norm_y = (clamped_y - ry_start) / rect_h

        target_x = int(norm_x * self.screen_w)
        target_y = int(norm_y * self.screen_h)

        smooth_x = int(self.ema_alpha * target_x + (1 - self.ema_alpha) * self.prev_x)
        smooth_y = int(self.ema_alpha * target_y + (1 - self.ema_alpha) * self.prev_y)

        self.prev_x = smooth_x
        self.prev_y = smooth_y

        return smooth_x, smooth_y
