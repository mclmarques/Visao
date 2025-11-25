## 📌 Description

This is a **Python-based hand movement controller** that uses **OpenCV** and **MediaPipe** to track hand movements via a webcam and map them to **keyboard inputs** (e.g., `W`, `A`, `S`, `D` for up, left, down, right). 

**Current Features**:
- Real-time hand movement detection (via MediaPipe).
- Keyboard input mapping (configurable).
- Adjustable sensitivity and cooldown to reduce false triggers.
- Visual feedback on the screen.

---

## 🛠️ Installation

### 🐍 Python Version

- **Preferred**: Python **3.12** or **3.10** (as of 25/11/2025, Python 3.13 is not supported by MediaPipe).
- **Tested**: Python 3.12 and 3.10.

### 📦 Dependencies

Install the required packages using `pip`:

```bash
pip install opencv-python mediapipe pyautogui
```

---

## 📦 Usage

### 🚀 Running the Code

1. Save the code below as `main.py` (or any preferred name).
2. Run the script:

```bash
python main.py
```

3. A window will open, displaying your webcam feed with hand landmarks.
4. Move your hand up, down, left, or right to trigger corresponding keyboard actions (`W`, `A`, `S`, `D` by default).

### 🔄 Key Mapping

- **Up**: `W` (default)
- **Down**: `S` (default)
- **Left**: `A` (default)
- **Right**: `D` (default)

You can change these by modifying the `KEY_UP`, `KEY_DOWN`, etc., variables in the code.

---

## 📌 Code Overview

### ✅ Core Logic

- **Hand Detection**: Uses MediaPipe's `Hands` module to detect hand landmarks.
- **Movement Tracking**: Compares current and previous wrist positions to detect directional movement.
- **Keyboard Input**: Uses `pyautogui` to send key presses based on movement.
- **Visual Feedback**: Displays movement labels (`UP`, `DOWN`, etc.) on the screen.

### 📏 Adjustable Parameters

- **Sensitivity**: `threshold = 0.03` (lower = more sensitive).
- **Cooldown**: `cooldown = 0.5` (seconds between key presses to prevent spamming).

You can tweak these values in the script to suit your use case.
