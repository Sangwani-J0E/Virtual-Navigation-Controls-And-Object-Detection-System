import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import signal

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_drawing = mp.solutions.drawing_utils

# Screen dimensions
screen_width, screen_height = pyautogui.size()

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Function to calculate the Euclidean distance between two points
def calculate_distance(point1, point2):
    return np.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

# Smoothing parameters
smooth_factor = 0.2
prev_x, prev_y = 0, 0

# Mini window dimensions
mini_window_width = 300
mini_window_height = 250

# Click debounce time
click_debounce_time = 0.5
last_left_click_time = 0
last_right_click_time = 0

# Signal handler for graceful exit
def signal_handler(sig, frame):
    cap.release()
    cv2.destroyAllWindows()
    print('Program terminated gracefully')
    exit(0)

# Set the signal handler for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)
    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image and detect hands
    results = hands.process(image_rgb)

    # Draw the mini window in the center
    image_height, image_width, _ = image.shape
    mini_window_x = (image_width - mini_window_width) // 2
    mini_window_y = (image_height - mini_window_height) // 2
    cv2.rectangle(image, (mini_window_x, mini_window_y),
                  (mini_window_x + mini_window_width, mini_window_y + mini_window_height), (0, 255, 0), 2)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the landmarks for the index finger, middle finger, and thumb
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Convert the landmark coordinates to image coordinates
            x = int(index_finger_tip.x * image_width)
            y = int(index_finger_tip.y * image_height)

            # Check if the finger is within the mini window
            if mini_window_x <= x <= mini_window_x + mini_window_width and mini_window_y <= y <= mini_window_y + mini_window_height:
                # Map the mini window coordinates to screen coordinates
                mapped_x = int((x - mini_window_x) * (screen_width / mini_window_width))
                mapped_y = int((y - mini_window_y) * (screen_height / mini_window_height))

                # Smooth the coordinates
                smoothed_x = int(prev_x + (mapped_x - prev_x) * smooth_factor)
                smoothed_y = int(prev_y + (mapped_y - prev_y) * smooth_factor)

                # Move the mouse
                pyautogui.moveTo(smoothed_x, smoothed_y)

                # Update previous coordinates
                prev_x, prev_y = smoothed_x, smoothed_y

            # Calculate distances
            index_middle_distance = calculate_distance(index_finger_tip, middle_finger_tip)
            thumb_index_distance = calculate_distance(index_finger_tip, thumb_tip)

            # Define thresholds for distances (these values may need to be adjusted)
            left_click_threshold = 0.05
            right_click_threshold = 0.05

            current_time = time.time()

            # Check for gestures
            if thumb_index_distance < left_click_threshold and (current_time - last_left_click_time) > click_debounce_time:
                pyautogui.click(button='left')
                last_left_click_time = current_time
                cv2.putText(image, "Left Click", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif index_middle_distance < right_click_threshold and (current_time - last_right_click_time) > click_debounce_time:
                pyautogui.click(button='right')
                last_right_click_time = current_time
    else:
        cv2.putText(image, "Hand Not Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the resulting frame
    cv2.imshow('Hand Tracking', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close OpenCV window
cap.release()
cv2.destroyAllWindows()