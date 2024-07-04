import cv2
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime, timedelta

thres = 0.45

# Capture video from camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
cap.set(10, 70)

classNames = []
classFile = 'coco.names'
with open(classFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

#Error handling, making it easier to debg the system
try:
    net = cv2.dnn_DetectionModel(weightsPath, configPath)
    net.setInputSize(320, 320)
    net.setInputScale(1.0 / 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)
except cv2.error as e:
    print(f"Error loading the model: {e}")
    exit(1)

# Create a custom Tkinter window
ctk.set_appearance_mode("light")  # Modes for window lighting: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")

window = ctk.CTk()
window.title("Object Detection")
window.geometry("1500x720")  # Screen Width and height

# Define custom colors
PRIMARY_COLOR = "#FF0000"  # Red
SECONDARY_COLOR = "#FFFFFF"  # White
ACCENT_COLOR = "#000000"  # Black

# Apply custom colors to the window
window.configure(bg=SECONDARY_COLOR)

# Create a frame to display detected objects
listbox_frame = ctk.CTkFrame(window, fg_color=SECONDARY_COLOR)
listbox_frame.pack(side=ctk.RIGHT, fill=ctk.Y, padx=(2, 10), pady=10) #Moving side panel

# Create a canvas and scrollbar for the listbox_frame
canvas = tk.Canvas(listbox_frame, bg=SECONDARY_COLOR)
scrollbar = ctk.CTkScrollbar(listbox_frame, orientation="vertical", command=canvas.yview)
scrollable_frame = ctk.CTkFrame(canvas, fg_color=SECONDARY_COLOR)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=ctk.LEFT, fill="both", expand=True)
scrollbar.pack(side=ctk.RIGHT, fill="y")

selected_class = tk.StringVar()
detected_objects = {}
last_update_time = datetime.now()

# Function to update the selected class
def on_select(class_name):
    selected_class.set(class_name)

# Function to unselect the current class
def unselect_class():
    selected_class.set("")

# Function to update the detected objects in the listbox
def update_listbox():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    for obj in detected_objects.keys():
        item_frame = ctk.CTkFrame(scrollable_frame, fg_color=SECONDARY_COLOR)
        item_frame.pack(fill="x", padx=5, pady=5)

        item_label = ctk.CTkLabel(item_frame, text=obj, fg_color=SECONDARY_COLOR, text_color=ACCENT_COLOR)
        item_label.pack(side="left", padx=5)

        select_button = ctk.CTkButton(item_frame, text="Select", command=lambda o=obj: on_select(o),
                                      fg_color=PRIMARY_COLOR, text_color=SECONDARY_COLOR, hover_color=ACCENT_COLOR)
        select_button.pack(side="left", padx=5)

        unselect_button = ctk.CTkButton(item_frame, text="Unselect", command=unselect_class,
                                        fg_color=PRIMARY_COLOR, text_color=SECONDARY_COLOR, hover_color=ACCENT_COLOR)
        unselect_button.pack(side="left", padx=5)

def update_frame():
    global detected_objects, last_update_time
    success, img = cap.read()
    if not success:
        return

    classIds, confs, bbox = net.detect(img, confThreshold=thres)

    current_time = datetime.now()
    new_objects = set()

    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            if 0 < classId <= len(classNames):
                class_name = classNames[classId - 1].upper()
                new_objects.add(class_name)
                if selected_class.get() == class_name:
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, class_name, (box[0] + 10, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    for obj in new_objects:
        detected_objects[obj] = current_time

    # Remove old detected objects
    detected_objects = {obj: time for obj, time in detected_objects.items() if current_time - time < timedelta(seconds=10)}

    if current_time - last_update_time >= timedelta(seconds=10):
        update_listbox()
        last_update_time = current_time

    # Convert the image to PIL format
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img_pil)

    # Update the Tkinter label with the new image
    if hasattr(window, 'image_label'):
        window.image_label.configure(image=imgtk)
        window.image_label.image = imgtk
    else:
        window.image_label = ctk.CTkLabel(window, image=imgtk, fg_color=SECONDARY_COLOR)
        window.image_label.image = imgtk
        window.image_label.pack(side=ctk.LEFT, padx=10, pady=10)

    # Call this function again after 10 ms
    window.after(10, update_frame)

# Start the frame update loop
update_frame()

# Run the Tkinter main loop
window.mainloop()

cap.release()
cv2.destroyAllWindows()
