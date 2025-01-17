import cv2
import mediapipe as mp
import numpy as np
import os
import time

# Initialize webcam and set properties
cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize MediaPipe Hands solution
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Define the keys for the virtual keyboard
keys = [["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P", "^", "$"],
        ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M", "%", "*"],
        ["W", "X", "C", "V", "B", "N", ",", ";", ":", "!", ".", "?"]]

# Define the final text variable and clicked state
finalText = ""
clicked = False
left_clicks = 0
right_clicks = 0
last_hand_used = "None"
action_log = []
fps_log = []

# Define a class for buttons
class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.text = text
        self.size = size

# Create button instances for the virtual keyboard
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

# Add space, delete, and exit buttons
buttonList.append(Button([50, 350], "Space", [885, 85]))
buttonList.append(Button([950, 350], "Delete", [285, 85]))
buttonList.append(Button([50, 450], "Exit", [1185, 85]))

# Function to detect hand landmarks
def handLandmarks(colorImg):
    landmarkList = []
    results = hands.process(colorImg)
    hand_type = "None"
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(colorImg, handLms, mpHands.HAND_CONNECTIONS)
            hand_type = "Right" if results.multi_handedness[0].classification[0].label == 'Right' else "Left"
            for id, lm in enumerate(handLms.landmark):
                h, w, c = colorImg.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarkList.append([id, cx, cy])
    return landmarkList, hand_type if results.multi_handedness else ("None")

# Function to draw rounded rectangle
def drawRoundedRect(img, top_left, bottom_right, color, radius, thickness=1):
    x1, y1 = top_left
    x2, y2 = bottom_right

    if thickness < 0:
        thickness = cv2.FILLED

    # Draw straight edges
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
    cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)

    # Draw four corners
    cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness)
    cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness)
    cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness)
    cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness)

# Function to draw all buttons
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        drawRoundedRect(img, (x, y), (x + w, y + h), (255, 255, 255), 20, -1)  # Change color to white
        drawRoundedRect(img, (x, y), (x + w, y + h), (255, 255, 255), 20, 1)  # Change color to a darker shade for border
        cv2.putText(img, button.text, (x + 25, y + 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    return img

# Function to calculate FPS
def calculate_fps(start_time, frame_count):
    current_time = time.time()
    fps = frame_count / (current_time - start_time)
    return fps

# Function to log actions and events
def log_action(action, hand_used, fps):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    action_log.append(f"Time: {current_time}, Action: {action}")
    fps_log.append(f"FPS: {fps}")
    return hand_used

# Function to save logs to a file
def save_logs(left_clicks, right_clicks, last_hand_used, action_log, fps_log, filename="virtual_keyboard_data.txt"):
    with open(filename, "a") as file:
        session_time = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
        file.write(f"\n\nSession on {session_time}:\n")
        file.write(f"Left Clicks: {left_clicks}\n")
        file.write(f"Right Clicks: {right_clicks}\n")
        file.write(f"Last Hand Used: {last_hand_used}\n")
        file.write("Actions Performed: \n")
        for action in action_log:
            file.write(f"{action}\n")
        file.write("\nFPS Log:\n")
        for fps in fps_log:
            file.write(f"{fps}\n")
        file.write("\n--- Event Log ---\n")

# Main loop
start_time = time.time()
frame_count = 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    lmlist, hand_used = handLandmarks(img)
    img = drawAll(img, buttonList)

    if lmlist:
        # Forefinger tip and middle finger tip landmarks
        forefinger_tip = lmlist[8]
        middle_finger_tip = lmlist[12]

        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < forefinger_tip[1] < x + w and y < forefinger_tip[2] < y + h:
                drawRoundedRect(img, (x, y), (x + w, y + h), (248, 131, 121), 20, -1)
                drawRoundedRect(img, (x, y), (x + w, y + h), (248, 131, 121), 20, 3)
                cv2.putText(img, button.text, (x + 25, y + 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

                # Check if the tip of the forefinger is close enough to the tip of the middle finger
                distance_threshold = 30  # Adjust this value as needed
                distance = ((forefinger_tip[1] - middle_finger_tip[1]) ** 2 + (forefinger_tip[2] - middle_finger_tip[2]) ** 2) ** 0.5
                if distance < distance_threshold and not clicked:
                    clicked = True
                    if button.text == "Space":
                        finalText += " "
                        action = "Left Click"
                        left_clicks += 1
                    elif button.text == "Delete":
                        finalText = finalText[:-1]
                        action = "Right Click"
                        right_clicks += 1
                    elif button.text == "Exit":
                        save_logs(left_clicks, right_clicks, last_hand_used, action_log, fps_log)
                        cap.release()
                        cv2.destroyAllWindows()
                        os.system('python AiVirtualMouse.py')
                        exit()
                    else:
                        finalText += button.text
                        action = "Left Click"
                        left_clicks += 1
                    last_hand_used = log_action(action, hand_used, calculate_fps(start_time, frame_count))
                elif distance >= distance_threshold:
                    clicked = False

    # Display the final text
    drawRoundedRect(img, (50, 580), (1235, 680), (248, 131, 121), 20, -1)
    cv2.putText(img, finalText, (60, 645), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 4)

    # Calculate and display FPS
    frame_count += 1
    fps = calculate_fps(start_time, frame_count)
    cv2.putText(img, f"FPS: {int(fps)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Virtual Keyboard", img)

    if cv2.waitKey(1) == ord('q'):
        save_logs(left_clicks, right_clicks, last_hand_used, action_log, fps_log)
        break

cap.release()
cv2.destroyAllWindows()
