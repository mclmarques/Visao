import cv2
import mediapipe as mp
import pyautogui
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- CONFIGURATION ---
MODEL_PATH = 'hand_landmarker.task'

# SENSITIVITY
# How much the hand must move between frames to register (0.01 - 0.1)
# Higher = You must move faster/further to trigger.
MOVEMENT_THRESHOLD = 0.04

# COOLDOWN
# Time in seconds to wait before accepting another input from the SAME hand.
# This allows you to return your hand to the center without triggering a "back" command.
COOLDOWN_SECONDS = 0.6

# Key Mappings
CONTROLS_LEFT_HAND = {'UP': 'w', 'DOWN': 's', 'LEFT': 'a', 'RIGHT': 'd'}
CONTROLS_RIGHT_HAND = {'UP': 'up', 'DOWN': 'down', 'LEFT': 'left', 'RIGHT': 'right'}


# --- LOGIC CLASS ---
class HandController:
    def __init__(self, label, controls):
        self.label = label
        self.controls = controls
        self.prev_x = None
        self.prev_y = None
        self.last_trigger_time = 0
        self.triggered_text = ""
        self.text_timer = 0

    def process(self, current_x, current_y, frame):
        current_time = time.time()
        h, w, _ = frame.shape

        # Calculate visual position
        cx, cy = int(current_x * w), int(current_y * h)

        # 1. Initialization check
        if self.prev_x is None:
            self.prev_x = current_x
            self.prev_y = current_y
            return

        # 2. Cooldown Check
        # If we are in cooldown, just update previous coordinates and exit
        # This prevents the "Recoil" from being registered if done quickly
        if current_time - self.last_trigger_time < COOLDOWN_SECONDS:
            # Update prev so we don't have a huge jump when cooldown ends
            self.prev_x = current_x
            self.prev_y = current_y

            # Draw Cooldown Indicator (Red Circle)
            cv2.circle(frame, (cx, cy), 15, (0, 0, 255), 2)
            return

        # 3. Calculate Delta (Movement since last frame)
        delta_x = current_x - self.prev_x
        delta_y = current_y - self.prev_y

        # Draw Active Indicator (Green Circle)
        cv2.circle(frame, (cx, cy), 15, (0, 255, 0), 2)

        action = None

        # 4. Check Thresholds
        # We prioritize the larger movement (Horizontal vs Vertical)
        if abs(delta_x) > MOVEMENT_THRESHOLD or abs(delta_y) > MOVEMENT_THRESHOLD:

            if abs(delta_x) > abs(delta_y):
                # Horizontal Move
                if delta_x > MOVEMENT_THRESHOLD:
                    action = 'RIGHT'
                elif delta_x < -MOVEMENT_THRESHOLD:
                    action = 'LEFT'
            else:
                # Vertical Move
                if delta_y > MOVEMENT_THRESHOLD:
                    action = 'DOWN'  # Y grows downwards
                elif delta_y < -MOVEMENT_THRESHOLD:
                    action = 'UP'

        # 5. Execute Action
        if action:
            pyautogui.press(self.controls[action])
            print(f"{self.label} Hand: {action}")

            self.last_trigger_time = current_time
            self.triggered_text = action
            self.text_timer = current_time

        # 6. Display Text Overlay
        if current_time - self.text_timer < 1.0:  # Show text for 1 second
            cv2.putText(frame, f"{self.label}: {self.triggered_text}", (cx - 40, cy - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 7. Update Previous Coordinates
        self.prev_x = current_x
        self.prev_y = current_y


# --- GLOBAL VARIABLES ---
current_result = None
left_controller = HandController("Left", CONTROLS_LEFT_HAND)
right_controller = HandController("Right", CONTROLS_RIGHT_HAND)


# --- CALLBACK ---
def save_result(result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global current_result
    current_result = result


# --- MAIN ---
def main():
    global current_result

    base_options = python.BaseOptions(
        model_asset_path=MODEL_PATH,
        delegate=python.BaseOptions.Delegate.CPU
    )
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        result_callback=save_result
    )

    cap = cv2.VideoCapture()

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        print("System started. Move hands decisively.")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            # 1. Flip Frame (Mirror Mode)
            frame = cv2.flip(frame, 1)

            timestamp = int(time.time() * 1000)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            landmarker.detect_async(mp_image, timestamp)

            if current_result and current_result.hand_landmarks:
                for i, landmarks in enumerate(current_result.hand_landmarks):
                    if i < len(current_result.handedness):
                        # Get Hand Label
                        label = current_result.handedness[i][0].category_name
                        wrist = landmarks[0]

                        # Process movement
                        if label == "Left":
                            left_controller.process(wrist.x, wrist.y, frame)
                        else:
                            right_controller.process(wrist.x, wrist.y, frame)

            cv2.imshow('Gesture Control (No Anchor)', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()