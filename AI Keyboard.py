import cv2
import mediapipe as mp
import numpy as np
import os

# Initialize webcam and set properties
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize MediaPipe Hands solution
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

# Define the keys for the virtual keyboard
keys = [["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P", "^", "$"],
        ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M", "%", "*"],
        ["W", "X", "C", "V", "B", "N", ",", ";", ":", "!", ".", "?"]]

# Define the final text variable and clicked state
finalText = ""
clicked = False

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
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(colorImg, handLms, mpHands.HAND_CONNECTIONS)
            for id, lm in enumerate(handLms.landmark):
                h, w, c = colorImg.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarkList.append([id, cx, cy])
    return landmarkList

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

# Main loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    lmlist = handLandmarks(img)
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
                    elif button.text == "Delete":
                        finalText = finalText[:-1]
                    elif button.text == "Exit":
                        cap.release()
                        cv2.destroyAllWindows()
                        os.system('python AiVirtualMouse.py')
                        exit()
                    else:
                        finalText += button.text
                elif distance >= distance_threshold:
                    clicked = False

    # Display the final text
    drawRoundedRect(img, (50, 580), (1235, 680), (248, 131, 121), 20, -1)
    cv2.putText(img, finalText, (60, 645), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 4)

    # Show the image
    cv2.imshow('Virtual Keyboard', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()