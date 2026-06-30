import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Optimizations for responsiveness
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True  # Move mouse to any corner to abort execution

class PCController:
    """
    Interfaces with the operating system to control Mouse, Media, and Volume.
    """
    def __init__(self):
        # Initialize Audio Endpoint Volume for Windows volume control
        try:
            self.devices = AudioUtilities.GetSpeakers()
            self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_ctrl = cast(self.interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            print(f"Warning: Audio device initialization failed. Pycaw functions may fail: {e}")
            self.volume_ctrl = None

    def play_pause(self):
        """Simulates play/pause media key."""
        pyautogui.press('playpause')

    def next_track(self):
        """Simulates next track media key."""
        pyautogui.press('nexttrack')

    def volume_up(self):
        """Simulates volume up media key."""
        pyautogui.press('volumeup')

    def volume_down(self):
        """Simulates volume down media key."""
        pyautogui.press('volumedown')

    def toggle_mute(self):
        """Toggles system mute using pycaw, falls back to media key if unavailable."""
        if self.volume_ctrl:
            try:
                current_mute = self.volume_ctrl.GetMute()
                self.volume_ctrl.SetMute(1 - current_mute, None)
                return "UNMUTED" if current_mute else "MUTED"
            except Exception as e:
                print(f"Error toggling mute via pycaw: {e}")
        
        pyautogui.press('volumemute')
        return "MUTE_TOGGLED"

    def get_volume(self):
        """Returns the system volume as a float between 0.0 and 1.0."""
        if self.volume_ctrl:
            try:
                return self.volume_ctrl.GetMasterVolumeLevelScalar()
            except Exception as e:
                print(f"Error getting volume: {e}")
        return 0.0

    def set_volume(self, val):
        """Sets the system volume. val must be between 0.0 and 1.0."""
        if self.volume_ctrl:
            try:
                val = max(0.0, min(1.0, val))
                self.volume_ctrl.SetMasterVolumeLevelScalar(val, None)
            except Exception as e:
                print(f"Error setting volume: {e}")

    def move_mouse(self, x, y):
        """Moves mouse cursor to target screen coordinates."""
        try:
            pyautogui.moveTo(x, y)
        except Exception as e:
            print(f"Error moving mouse: {e}")

    def click(self):
        """Triggers a left mouse click."""
        try:
            pyautogui.click()
        except Exception as e:
            print(f"Error clicking mouse: {e}")
