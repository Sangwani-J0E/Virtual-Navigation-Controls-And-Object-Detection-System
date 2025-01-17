import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import signal
from PIL import ImageFont, ImageDraw, Image

# Load Montserrat font (assuming you have downloaded and saved Montserrat-Regular.ttf in the current directory)
font_path = 'montserrat/Montserrat-Regular.ttf'  # Path to Montserrat font
font_size = 24  # Adjust the font size as needed

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.85, min_tracking_confidence=0.85)
mp_drawing = mp.solutions.drawing_utils

# Screen dimensions
screen_width, screen_height = pyautogui.size()

# Capture video from webcam
cap = cv2.VideoCapture(1)

# FPS tracking
prev_frame_time = 0
new_frame_time = 0

# Function to calculate the Euclidean distance between two points
def calculate_distance(point1, point2):
    return np.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

# Smoothing parameters
smooth_factor = 0.2
prev_x, prev_y = 0, 0

# Mini window dimensions
mini_window_width = 250
mini_window_height = 200

# Click debounce time
click_debounce_time = 0.5
last_left_click_time = 0
last_right_click_time = 0

# Analytics data
hand_used = "None"
action_performed = "None"
left_click_count = 0
right_click_count = 0

# Create a list to store the data for recording
data_log = []

# Signal handler for graceful exit and writing to a file
def signal_handler(sig, frame):
    cap.release()
    cv2.destroyAllWindows()

    # Append the simplified data to a text file
    with open('hand_tracking_data.txt', 'a') as file:  # 'a' opens the file in append mode
        file.write(f"\nSession on {time.ctime()}:\n")
        file.write(f"Left Clicks: {left_click_count}\n")
        file.write(f"Right Clicks: {right_click_count}\n")
        file.write(f"Last Hand Used: {hand_used}\n")
        file.write(f"Actions Performed: {action_performed}\n")
        file.write("\n--- Event Log ---\n")
        for log in data_log:
            file.write(log + "\n")

    print('Data appended to hand_tracking_data.txt')
    exit(0)

# Set the signal handler for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Function to draw text with a background
def draw_text_with_background(image, text, position, font_path=None, font_size=1, font_color=(255, 255, 255),
                              bg_color=(0, 0, 0), thickness=2, padding=5):
    if font_path:
        # Load the font from the specified path
        font = cv2.FONT_HERSHEY_SIMPLEX  # Replace this with your custom font loading logic if needed
    else:
        font = cv2.FONT_HERSHEY_SIMPLEX

    text_size, _ = cv2.getTextSize(text, font, font_size, thickness)

    text_w, text_h = text_size
    x, y = position

    # Draw background rectangle
    cv2.rectangle(image, (x - padding, y - text_h - padding), (x + text_w + padding, y + padding), bg_color, -1)

    # Draw text on top of background
    cv2.putText(image, text, (x, y), font, font_size, font_color, thickness)

    return image  # Ensure the modified image is returned

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
        for hand_landmarks, handedness_data in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Determine which hand is being used (left or right)
            hand_used = handedness_data.classification[0].label

            # Get the landmarks for the index finger, middle finger, and thumb
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
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

            # Normalize distances based on hand size
            hand_width = calculate_distance(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP],
                                            hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP])
            normalized_thumb_index_distance = thumb_index_distance / hand_width
            normalized_index_middle_distance = index_middle_distance / hand_width

            # Define thresholds for normalized distances (adjust as needed)
            left_click_threshold = 0.2
            right_click_threshold = 0.25

            current_time = time.time()

            # Check for gestures
            if normalized_thumb_index_distance < left_click_threshold and (
                    current_time - last_left_click_time) > click_debounce_time:
                pyautogui.click(button='left')
                last_left_click_time = current_time
                left_click_count += 1
                action_performed = "Left Click"
                data_log.append(f"Time: {time.ctime()}, Action: Left Click")
            elif normalized_index_middle_distance < right_click_threshold and (
                    current_time - last_right_click_time) > click_debounce_time:
                pyautogui.click(button='right')
                last_right_click_time = current_time
                right_click_count += 1
                action_performed = "Right Click"
                data_log.append(f"Time: {time.ctime()}, Action: Right Click")
    else:
        hand_used = "None"
        action_performed = "None"

    # Calculate FPS
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time

    # Draw text using the custom function
    image = draw_text_with_background(image, f'FPS: {int(fps)}', (10, 40), font_path, font_size=0.7)
    image = draw_text_with_background(image, f'Hand: {hand_used}', (10, 80), font_path, font_size=0.7)
    image = draw_text_with_background(image, f'Action: {action_performed}', (10, 120), font_path, font_size=0.7)
    image = draw_text_with_background(image, f'Left Clicks: {left_click_count}', (10, 160), font_path, font_size=0.7)
    image = draw_text_with_background(image, f'Right Clicks: {right_click_count}', (10, 200), font_path, font_size=0.7)

    # Display the resulting frame
    cv2.imshow('Hand Tracking', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        signal_handler(None, None)

# When everything is done, release the capture and close any OpenCV windows
cap.release()
cv2.destroyAllWindows()
