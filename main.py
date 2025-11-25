import cv2
import mediapipe as mp
import pyautogui

#NOTE: as of 25/11/2025, use Python 3.12 or older as 3.13 is not suportted by mediapipe. 3.12 and 3.10 have been tested and worked fine
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Sensitivity (lower = more sensitive)
threshold = 0.03

# Key mappings for directions (you can customize these)
KEY_UP = 'w'
KEY_DOWN = 's'
KEY_LEFT = 'a'
KEY_RIGHT = 'd'

# Initialize previous coordinates
prev_wrist_x = None
prev_wrist_y = None

# Cooldown to prevent rapid key presses
last_key_time = 0
cooldown = 0.5  # seconds

# Start video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    current_wrist_x = None
    current_wrist_y = None

    # Draw hand landmarks if detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Get wrist coordinates (landmark index 0)
            current_wrist_x = hand_landmarks.landmark[0].x
            current_wrist_y = hand_landmarks.landmark[0].y

    # Check for movement in each direction
    if current_wrist_x is not None and current_wrist_y is not None:
        if prev_wrist_x is not None and prev_wrist_y is not None:
            # Calculate deltas
            delta_x = current_wrist_x - prev_wrist_x
            delta_y = current_wrist_y - prev_wrist_y

            # Up: y decreases
            if delta_y < -threshold and time.time() - last_key_time > cooldown:
                pyautogui.press(KEY_UP)
                cv2.putText(frame, "UP", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                last_key_time = time.time()

            # Down: y increases
            if delta_y > threshold and time.time() - last_key_time > cooldown:
                pyautogui.press(KEY_DOWN)
                cv2.putText(frame, "DOWN", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                last_key_time = time.time()

            # Left: x decreases
            if delta_x < -threshold and time.time() - last_key_time > cooldown:
                pyautogui.press(KEY_LEFT)
                cv2.putText(frame, "LEFT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                last_key_time = time.time()

            # Right: x increases
            if delta_x > threshold and time.time() - last_key_time > cooldown:
                pyautogui.press(KEY_RIGHT)
                cv2.putText(frame, "RIGHT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                last_key_time = time.time()

        # Update previous coordinates
        prev_wrist_x = current_wrist_x
        prev_wrist_y = current_wrist_y

    # Display the frame
    cv2.imshow('Hand Movement Control', frame)

    # Exit on ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()