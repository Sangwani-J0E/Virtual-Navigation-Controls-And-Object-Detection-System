import cv2
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime, timedelta
from ultralytics import YOLO
import pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Function to speak the alert message
def speak_alert(message):
    engine.say(message)
    engine.runAndWait()

# Threshold for detection confidence
thres = 0.45

# Capture video from camera
cap = cv2.VideoCapture(1)
cap.set(3, 1280)  # Set width
cap.set(4, 720)  # Set height
cap.set(10, 70)  # Set brightness

# Load YOLOv5 model (the pretrained model from Ultralytics)
model = YOLO("yolov5s.pt")

# Real-world dimensions of objects (in meters)
object_real_sizes = {
    "person": 1.7,
    "car": 4.5,
    "chair": 0.8,
    "bicycle": 1.2,
    "dog": 0.5,
    "cat": 0.3,
    "tree": 5.0,
}

# Focal length (example value)
focal_length = 700

# Create a custom Tkinter window
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

window = ctk.CTk()
window.title("Object Detection with YOLOv5")
window.geometry("1500x720")

# Create an image label to display the video feed
window.image_label = ctk.CTkLabel(window)
window.image_label.pack(side=ctk.LEFT, padx=10, pady=10)

# Define custom colors
PRIMARY_COLOR = "#FF0000"
SECONDARY_COLOR = "#FFFFFF"
ACCENT_COLOR = "#000000"

# Apply custom colors to the window
window.configure(bg=SECONDARY_COLOR)

# Create a frame to display detected objects
listbox_frame = ctk.CTkFrame(window, fg_color=SECONDARY_COLOR)
listbox_frame.pack(side=ctk.RIGHT, fill=ctk.Y, padx=(2, 10), pady=10)

# Create a canvas and scrollbar for the listbox_frame
canvas = tk.Canvas(listbox_frame, bg=SECONDARY_COLOR)
scrollbar = ctk.CTkScrollbar(listbox_frame, orientation="vertical", command=canvas.yview)
scrollable_frame = ctk.CTkFrame(canvas, fg_color=SECONDARY_COLOR)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=ctk.LEFT, fill="both", expand=True)
scrollbar.pack(side=ctk.RIGHT, fill="y")

selected_objects = set()  # Set to track selected objects
detected_objects = {}
last_update_time = datetime.now()

# Variables to track clicks and actions
left_clicks = 0
right_clicks = 0
actions_performed = []

def estimate_distance(box_width_in_pixels, real_width, focal_length):
    if box_width_in_pixels == 0:
        return float('inf')
    distance = (real_width * focal_length) / box_width_in_pixels
    return distance

# Function to update the detected objects in the listbox
def update_listbox():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    for obj in detected_objects.keys():
        item_frame = ctk.CTkFrame(scrollable_frame, fg_color=SECONDARY_COLOR)
        item_frame.pack(fill="x", padx=5, pady=5)

        item_label = ctk.CTkLabel(item_frame, text=obj, fg_color=SECONDARY_COLOR, text_color=ACCENT_COLOR)
        item_label.pack(side="left", padx=5)

        select_button = ctk.CTkButton(item_frame, text="Select",
                                       command=lambda o=obj: on_select(o),
                                       fg_color=PRIMARY_COLOR, text_color=SECONDARY_COLOR, hover_color=ACCENT_COLOR)
        select_button.pack(side="left", padx=5)

        unselect_button = ctk.CTkButton(item_frame, text="Unselect",
                                         command=lambda o=obj: unselect_class(o),
                                         fg_color=PRIMARY_COLOR, text_color=SECONDARY_COLOR, hover_color=ACCENT_COLOR)
        unselect_button.pack(side="left", padx=5)

# Function to update the selected class
def on_select(class_name):
    selected_objects.add(class_name)
    update_frame()

# Function to unselect the current class
def unselect_class(class_name):
    selected_objects.discard(class_name)
    update_frame()

# Function to log data to the text file
def log_data():
    with open("Object_detection_data.txt", "a") as log_file:
        now = datetime.now()
        log_file.write(f"--- Event Log ---\n")
        log_file.write(f"Session on {now}:\n")
        log_file.write(f"Left Clicks: {left_clicks}\n")
        log_file.write(f"Right Clicks: {right_clicks}\n")
        log_file.write(f"Actions Performed: {actions_performed[-1] if actions_performed else 'None'}\n")
        log_file.write(f"Objects Detected: {', '.join(detected_objects.keys())}\n")
        average_distance = sum([estimate_distance(100, object_real_sizes[obj], focal_length) for obj in detected_objects.keys() if obj in object_real_sizes]) / len(detected_objects) if detected_objects else 0
        log_file.write(f"Average Distance From Objects: {round(average_distance, 2)} m\n")
        log_file.write("\n")
        for action in actions_performed:
            log_file.write(f"Time: {action['time']}, Action: {action['action']}\n")
        log_file.write("\n")
        log_file.flush()

# Function to update the frame and detect objects
frame_count = 0

def update_frame():
    global detected_objects, last_update_time, frame_count, left_clicks, right_clicks, actions_performed
    success, img = cap.read()
    if not success:
        return

    # Only run detection every 3 frames
    if frame_count % 3 == 0:
        results = model(img)
        current_time = datetime.now()
        new_objects = set()

        for result in results:
            for detection in result.boxes.data:
                class_id = int(detection[5])
                class_name = model.names[class_id]
                confidence = detection[4].item()
                bbox = detection[:4].numpy().astype(int)

                # Draw bounding boxes
                box_color = (0, 255, 0) if class_name not in selected_objects else (255, 0, 0)
                cv2.rectangle(img, bbox, color=box_color, thickness=2)
                cv2.putText(img, f"{class_name.upper()} {round(confidence * 100, 2)}%", (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, box_color, 2)

                if class_name in object_real_sizes:
                    box_width_in_pixels = bbox[2] - bbox[0]
                    real_width = object_real_sizes[class_name]
                    distance = estimate_distance(box_width_in_pixels, real_width, focal_length)
                    cv2.putText(img, f"Distance: {round(distance, 2)} m", (bbox[0], bbox[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                    # Check for distance thresholds
                    if distance < 10:
                        speak_alert(f"In {round(distance, 2)} meters, you are about to reach a {class_name}")
                    elif distance < 15:  # Additional alert for 15 meters
                        speak_alert(f"You are within 15 meters of a {class_name}")

                new_objects.add(class_name)

        detected_objects = {obj: time for obj, time in detected_objects.items() if current_time - time < timedelta(seconds=10)}
        detected_objects.update({obj: current_time for obj in new_objects})
        update_listbox()
        last_update_time = current_time

        # Log data to the text file
        log_data()

    frame_count += 1

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    imgtk = ImageTk.PhotoImage(image=img_pil)
    window.image_label.configure(image=imgtk)
    window.image_label.image = imgtk

    window.after(10, update_frame)

# Track mouse clicks
def on_left_click(event):
    global left_clicks
    left_clicks += 1
    actions_performed.append({'time': datetime.now(), 'action': 'Left Click'})
    log_data()  # Log the click event

def on_right_click(event):
    global right_clicks
    right_clicks += 1
    actions_performed.append({'time': datetime.now(), 'action': 'Right Click'})
    log_data()  # Log the click event

# Bind mouse click events
window.bind("<Button-1>", on_left_click)  # Left click
window.bind("<Button-3>", on_right_click)  # Right click

# Start the video stream and GUI
update_frame()
window.mainloop()

# Release the video capture when done
cap.release()
