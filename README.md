# Gesture Controlled PC 🖐️💻

A real-time, webcam-based hand gesture recognition system designed to control core computer functions without physical contact. By leveraging state-of-the-art computer vision and system APIs, this application maps intuitive hand motions to Windows volume levels, media playback controls, and mouse cursors.

---

## 🌟 Features

*   **Real-time Hand Tracking:** Fast hand coordinate extraction utilizing MediaPipe.
*   **Intuitive Gesture Recognition:** Custom math-based rule engine evaluating finger extension and proximity metrics.
*   **Precise Cursor Control:**
    *   Smooth movement using an **Exponential Moving Average (EMA)** filter to eliminate hand jitters.
    *   **Safety Calibration Zone:** Restricts active tracking to a central box in the camera feed, making reaching the screen's edges seamless without stretching your hand.
    *   **Pinch-to-Click:** Tap thumb and index finger together to trigger a native OS left mouse click.
*   **Fine-Grained Volume Adjustment:** Smooth scaling of system audio levels (0%-100%) mapped directly to the physical distance between your thumb and index finger.
*   **Debounced Actions:** 1.2-second cooldown on media keys to prevent accidental repeated triggers.
*   **Modern HUD (Heads-Up Display):** High-contrast, transparent overlay presenting real-time system states, active modes, volume bar, detected gestures, and FPS counter.

---

## 🛠️ Tech Stack

*   **Programming Language:** Python 3.10+
*   **Computer Vision:** OpenCV (Video Capture, HUD overlays)
*   **Hand Tracking:** MediaPipe Hands (21 Landmark models)
*   **System Controls:**
    *   PyAutoGUI (Mouse inputs and discrete Media keys)
    *   PyCaw (Direct Core Audio Endpoint API mapping for Windows volume controls)

---

## 🏗️ Project Architecture

```
Gesture_Controlled_PC/
│
├── requirements.txt         # Package dependencies
├── hand_detector.py         # MediaPipe abstraction & landmark locator
├── gesture_recognizer.py     # Feature extraction and rule-based classifier
├── pc_controller.py         # Native mouse & system sound control wrappers
├── utils.py                 # Mathematical helpers, FPS counter, & ScreenMapper
├── main.py                  # Core execution engine & application loop
└── README.md                # Project documentation
```

---

## 📁 Gesture to Action Reference Table

| Mode | Gesture | Physical Hand State | Action Executed |
| :--- | :--- | :--- | :--- |
| **Standard** | `Open Palm` | All 5 fingers extended | Play / Pause Media |
| **Standard** | `Fist` | All 5 fingers folded | Mute / Unmute Volume |
| **Standard** | `Peace Sign` | Index + Middle extended, others folded | Next Audio Track |
| **Standard** | `Thumb Up` | Only thumb extended upwards | Volume Incremental Up (+) |
| **Standard** | `Thumb Down` | Only thumb extended downwards | Volume Incremental Down (-) |
| **Mouse Mode** | `Index Only` | Only Index finger extended | Move Mouse Cursor |
| **Mouse Mode** | `Pinch` | Thumb Tip and Index Tip touching | Mouse Left Click |
| **Volume Mode**| `Thumb + Index Dist` | Thumb & Index extended, adjust distance | Continuous Volume Slider (0% - 100%) |

---

## 🚀 Installation & Setup

1.  **Clone or Navigate to the Directory:**
    ```bash
    cd Gesture_Controlled_PC
    ```

2.  **Install Dependencies:**
    It is recommended to run this in a Python Virtual Environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python main.py
    ```

---

## 🎮 How to Use

1.  Stand or sit in front of your webcam, ensuring good lighting.
2.  Press **`M`** on your keyboard to toggle **Mouse Control Mode**. Use your index finger inside the highlighted **Active Safety Zone** bounding box to guide the mouse, and pinch (index + thumb) to left click.
3.  Press **`V`** on your keyboard to toggle **Volume Control Mode**. Part your index and thumb to increase volume, and pinch them together to decrease it. Observe the HUD volume bar updating.
4.  Toggle off both modes (by pressing `M` or `V` again) to resume **Standard Gesture Controls** (Play/Pause, Next Track, Mute/Unmute, discrete Vol adjustments).
5.  Press **`Q`** to quit the application safely.

---

## 🚀 Future Enhancements

*   **Virtual Keyboard:** Typing interface by picking floating characters.
*   **Slide Controller:** Dedicated presenter mode matching PowerPoint controls.
*   **Dual Hand Support:** Separate mouse control to left hand and shortcuts to right hand.
*   **Mac/Linux Audio Wrapper Support:** Cross-platform native volume wrappers.

---
