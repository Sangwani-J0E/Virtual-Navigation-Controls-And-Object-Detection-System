import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import customtkinter
import sys
import os
import time

# Function to resize the background image
def resize_image(event):
    global background_image, background_photo, canvas
    window_width = event.width
    window_height = event.height
    resized_image = background_image.resize((window_width, window_height), Image.Resampling.LANCZOS)
    background_photo = ImageTk.PhotoImage(resized_image)
    canvas.itemconfig(background, image=background_photo)
    canvas.coords(background, 0, 0)

# Function to run Simple Hand Tracking
def Run_SHT():
    global subprocess_instance
    subprocess_instance = subprocess.Popen([sys.executable, 'AiVirtualMouse.py'])

# Function to run Virtual Keyboard
def Run_VirtualKeyboard():
    global subprocess_instance
    subprocess_instance = subprocess.Popen([sys.executable, 'AI KeyBoard.py'])

# Function to run Object Detection
def Run_ObjectDetection():
    global subprocess_instance
    subprocess_instance = subprocess.Popen([sys.executable, 'Object Detection.py'])

def AR():
    global subprocess_instance
    subprocess_instance = subprocess.Popen([sys.executable, 'AR.py'])

# Function to close subprocess
def close_subprocess():
    global subprocess_instance
    if subprocess_instance:
        subprocess_instance.terminate()
        subprocess_instance = None
        messagebox.showinfo("Info", "Process terminated successfully.")
    else:
        messagebox.showinfo("Info", "No subprocess running.")

# Function to open Tutorial window
def Open_Tutorial():
    window.withdraw()  # Hide the main window
    tutorial_window = tk.Toplevel(window)
    tutorial_window.title("Tutorial")
    tutorial_window.attributes("-fullscreen", True)  # Open the window maximized
    tutorial_window.protocol("WM_DELETE_WINDOW", lambda: on_tutorial_close(tutorial_window))

    # Load the background image for the tutorial window
    tutorial_background_image = Image.open("background.png")
    tutorial_background_photo = ImageTk.PhotoImage(tutorial_background_image)

    # Create a canvas for the tutorial window
    tutorial_canvas = tk.Canvas(tutorial_window, width=tutorial_background_image.width,
                                height=tutorial_background_image.height, bg="white")
    tutorial_canvas.pack(fill="both", expand=True)

    # Add the background image to the canvas
    tutorial_background = tutorial_canvas.create_image(0, 0, anchor="nw", image=tutorial_background_photo)

    # Bind the resize_image function to the canvas's resize event
    tutorial_canvas.bind("<Configure>",
                         lambda event: resize_tutorial_image(event, tutorial_background_image, tutorial_background,
                                                             tutorial_canvas))

    # Load tutorial images
    tutorial_images = [
        Image.open(f"TUT {i}.png") for i in range(1, 6)
    ]

    # Function to resize and display the current tutorial image
    def update_tutorial_image(index):
        nonlocal current_image_index
        current_image_index = index
        resized_image = tutorial_images[current_image_index].resize(
            (tutorial_window.winfo_width(), tutorial_window.winfo_height()), Image.Resampling.LANCZOS)
        tutorial_photo_image = ImageTk.PhotoImage(resized_image)
        tutorial_image_label.config(image=tutorial_photo_image)
        tutorial_image_label.image = tutorial_photo_image

    # Display the current tutorial image
    current_image_index = 0
    tutorial_photo_image = ImageTk.PhotoImage(tutorial_images[current_image_index])
    tutorial_image_label = tk.Label(tutorial_canvas, image=tutorial_photo_image)
    tutorial_image_label.image = tutorial_photo_image
    tutorial_image_label.place(relx=0.5, rely=0.5, anchor="center")

    # Function to go to the next tutorial image
    def next_image():
        nonlocal current_image_index
        if current_image_index < len(tutorial_images) - 1:
            current_image_index += 1
            update_tutorial_image(current_image_index)

    # Function to go to the previous tutorial image
    def previous_image():
        nonlocal current_image_index
        if current_image_index > 0:
            current_image_index -= 1
            update_tutorial_image(current_image_index)

    # Create buttons
    next_button = customtkinter.CTkButton(tutorial_window, text="Next", fg_color="#B71C1C", bg_color='#FFFFFF',
                                          font=("Arial", 24, "bold"), command=next_image, corner_radius=20, width=190,
                                          height=70)
    previous_button = customtkinter.CTkButton(tutorial_window, text="Previous", fg_color="#B71C1C", bg_color='#FFFFFF',
                                              font=("Arial", 24, "bold"), command=previous_image, corner_radius=20,
                                              width=200, height=70)
    back_button = customtkinter.CTkButton(tutorial_window, text="Back", text_color="#B71C1C", fg_color="#FFFFFF", bg_color='#B71C1C',
                                          font=("Arial", 24, "bold"), command=lambda: on_tutorial_close(tutorial_window),
                                          corner_radius=20, width=120, height=65)

    next_button.place(relx=0.99, rely=0.55, anchor="se")
    previous_button.place(relx=0.01, rely=0.55, anchor="sw")
    back_button.place(relx=0.08, rely=0.9, anchor="s")

# Function to handle Tutorial window close event
def on_tutorial_close(tutorial_window):
    tutorial_window.destroy()
    window.deiconify()  # Bring back the main window

# Function to resize the tutorial background image
def resize_tutorial_image(event, image, image_item, canvas):
    new_width = event.width
    new_height = event.height
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    photo_image = ImageTk.PhotoImage(resized_image)
    canvas.itemconfig(image_item, image=photo_image)
    canvas.image = photo_image

# Function to view data from a file
def view_data(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
        messagebox.showinfo("Data from " + filename, data)
    except FileNotFoundError:
        messagebox.showwarning("File not found", f"The file {filename} does not exist.")
# Function to view object detection data from a file
def view_object_detection_data():
    view_data('object_detection_data.txt')

# Function to open a window with options to view virtual keyboard, hand tracking, and object detection data
def open_data_viewer():
    # Create a new Toplevel window
    data_window = tk.Toplevel(window)
    data_window.title("Data Viewer")
    data_window.attributes("-fullscreen", True)  # Open in fullscreen
    data_window.protocol("WM_DELETE_WINDOW", lambda: on_data_viewer_close(data_window))

    # Load the background image
    background_image = Image.open("background2.png")
    background_photo = ImageTk.PhotoImage(background_image)

    # Create a canvas in the Toplevel window
    canvas = tk.Canvas(data_window, bg="white")
    canvas.pack(fill="both", expand=True)

    # Add the background image to the canvas
    background = canvas.create_image(0, 0, anchor="nw", image=background_photo)

    # Bind the resize_image function to dynamically adjust the background
    canvas.bind(
        "<Configure>",
        lambda event: resize_image(event, canvas, background_photo, background)
    )

    # Keep references to avoid garbage collection
    canvas.photo_ref = background_photo
    canvas.image_ref = background_image

    #button Sizes
    button_width = 300
    button_height = 70

    #black Backgroud
    data_label1 = customtkinter.CTkLabel(canvas, fg_color="#36454F", bg_color='#36454F',
                                          text_color="#36454F", font=("Arial", 24, "bold"),
                                          corner_radius=5, width=1059, height=350)

    # Text Label
    data_label2 = customtkinter.CTkLabel(canvas,
                                                text="Operate your device without a physical keyboard using virtual keyboard functionality."
                                                    "                                                                     "
                                                    "--------------------------------------------------------------------------------------------"
                                                    "AI Virtual Mouse enables seamless device navigation without a physical mouse."
                                                    "                                                                         "
                                                    "--------------------------------------------------------------------------------------------"
                                                    "Real-time Object Detection identifies objects via camera and tracks distances dynamically."
                                                    "                                                            "
                                                    "--------------------------------------------------------------------------------------------"
                                                    "Augmented Reality overlays videos onto scanned objects for an interactive experience.",
                                                text_color="#899499", fg_color="#28323e",
                                                bg_color='#36454F', font=("Arial", 20, "bold"),
                                                corner_radius=5, width=700, height=330, wraplength=650)

    # Create buttons for viewing data
    virtual_keyboard_button = customtkinter.CTkButton(data_window, text="View Keyboard Data", fg_color="#899499", bg_color='#36454F',
                                                font=("Arial", 24, "bold"), corner_radius=20,
                                                width=button_width, height=button_height,
                                                command=lambda: view_data('virtual_keyboard_data.txt'),)
    hand_tracking_button = customtkinter.CTkButton(data_window, text="View AI Mouse Data", fg_color="#899499", bg_color='#36454F',
                                                font=("Arial", 24, "bold"), corner_radius=20,
                                                width=button_width, height=button_height,
                                                command=lambda: view_data('hand_tracking_data.txt'))
    object_detection_button = customtkinter.CTkButton(data_window, text="View Detection Data", fg_color="#899499", bg_color='#36454F',
                                                font=("Arial", 24, "bold"), corner_radius=20,
                                                width=button_width, height=button_height,
                                                command=view_object_detection_data,)  # New button for object detection
    AR_detection_button = customtkinter.CTkButton(data_window, text="View A.R. Data",
                                                fg_color="#899499", bg_color='#36454F',
                                                font=("Arial", 24, "bold"), corner_radius=20,
                                                width=button_width, height=button_height)  # New button for AR
    back_button = customtkinter.CTkButton(data_window, text="Back", text_color="#B71C1C", fg_color="#FFFFFF",
                                                bg_color='#28323e', font=("Arial", 24, "bold"),
                                                command=lambda: on_data_viewer_close(data_window),
                                                corner_radius=20, width=120, height=65)

    # Position the buttons
    virtual_keyboard_button.place(relx=0.25, rely=0.3, anchor="center")
    hand_tracking_button.place(relx=0.25, rely=0.4, anchor="center")
    object_detection_button.place(relx=0.25, rely=0.5, anchor="center")
    AR_detection_button.place(relx=0.25, rely=0.6, anchor="center")
    back_button.place(relx=0.05, rely=0.10, anchor="s")

    #position of background Elements
    data_label1.place(relx=0.49, rely=0.45, anchor="center")    # Place the terminate button at 450% height
    data_label2.place(relx=0.6, rely=0.45, anchor="center")    # Place the terminate button at 450% height

# Function to handle data viewer close event
def on_data_viewer_close(data_window):
    data_window.destroy()
    window.deiconify()  # Bring back the main window

# Create a window
window = tk.Tk()
window.title("AI Virtual System")

# Load the background image
background_image = Image.open("background2.png")
background_photo = ImageTk.PhotoImage(background_image)

# Create a canvas
canvas = tk.Canvas(window, width=background_image.width, height=background_image.height, bg="white")
canvas.pack(fill="both", expand=True)

# Add the background image to the canvas
background = canvas.create_image(0, 0, anchor="nw", image=background_photo)

# Bind the resize_image function to the canvas's resize event
canvas.bind("<Configure>", resize_image)

# Label for "AI Virtual System" text
title_label1 = customtkinter.CTkLabel(canvas, text="AI VIRTUAL SYSTEM", text_color="#FF5733", font=("Arial", 60, "bold"), bg_color='#36454F', fg_color="#28323e")
# Set common button size for consistency
button_width = 300
button_height = 70

#White bottom label
title_label4 = customtkinter.CTkLabel(canvas,fg_color="#E5E4E2", bg_color='#36454F',
                                text_color="#E5E4E2", font=("Arial", 24, "bold"),
                                corner_radius=5, width=1059, height=90)

#Black background Element Label
title_label2 = customtkinter.CTkLabel(canvas,fg_color="#36454F", bg_color='#36454F',
                                text_color="#FFFFFF", font=("Arial", 24, "bold"),
                                corner_radius=5, width=1059, height=350)

#Text Label
title_label3 = customtkinter.CTkLabel(canvas, text="Operate your device without a physical keyboard using virtual keyboard functionality."
                                                   "                                                                     "
                                                   "--------------------------------------------------------------------------------------------"
                                                   "AI Virtual Mouse enables seamless device navigation without a physical mouse."
                                                   "                                                                         "
                                                   "--------------------------------------------------------------------------------------------"
                                                   "Real-time Object Detection identifies objects via camera and tracks distances dynamically."
                                                   "                                                            "
                                                   "--------------------------------------------------------------------------------------------"
                                                   "Augmented Reality overlays videos onto scanned objects for an interactive experience.",
                                  text_color="#899499", fg_color="#28323e",
                                  bg_color='#36454F', font=("Arial", 20, "bold"),
                                  corner_radius=5, width=700, height=330, wraplength=650)

#Buttons Label
button2 = customtkinter.CTkButton(window, text="AI Virtual Keyboard",  fg_color="#899499", bg_color='#36454F',
                                font=("Arial", 24, "bold"), command=Run_VirtualKeyboard, corner_radius=20,
                                width=button_width, height=button_height)
button3 = customtkinter.CTkButton(window, text="AI Virtual Mouse", fg_color="#899499", bg_color='#36454F',
                                font=("Arial", 24, "bold"), command=Run_SHT, corner_radius=20,
                                width=button_width, height=button_height)
button4 = customtkinter.CTkButton(window, text="Object Detection", fg_color="#899499", bg_color='#36454F',
                                font=("Arial", 24, "bold"), command=Run_ObjectDetection, corner_radius=20,
                                width=button_width, height=button_height)
button5 = customtkinter.CTkButton(window, text="Augemented Reality", fg_color="#899499", bg_color='#36454F',
                                font=("Arial", 24, "bold"), command=AR, corner_radius=20,
                                width=button_width, height=button_height)
button6 = customtkinter.CTkButton(window, text="Data Viewer", fg_color="#36454F", text_color="#FF5733", bg_color='#E5E4E2',
                                font=("Arial", 24, "bold"), command=open_data_viewer, corner_radius=20,
                                width=button_width, height=button_height)
button7 = customtkinter.CTkButton(window, text="Tutorial", fg_color="#36454F", text_color="#FF5733", bg_color='#E5E4E2',
                                font=("Arial", 24, "bold"), command=Open_Tutorial, corner_radius=20,
                                width=button_width, height=button_height)
button8 = customtkinter.CTkButton(window, text="Terminate", text_color="#FF5733", fg_color="#36454F",
                                bg_color='#E5E4E2', font=("Arial", 24, "bold"), command=close_subprocess,
                                corner_radius=20, width=button_width, height=button_height)

# Position the buttons
button2.place(relx=0.25, rely=0.3, anchor="center")  # Place the first button at 30% height
button3.place(relx=0.25, rely=0.4, anchor="center")  # Place the second button at 40% height
button4.place(relx=0.25, rely=0.5, anchor="center")  # Place the third button at 50% height
button5.place(relx=0.25, rely=0.6, anchor="center")  # Place the fourth button at 60% height
button6.place(relx=0.29, rely=0.723, anchor="center")  # Place the fifth button at 70% height
button7.place(relx=0.71, rely=0.723, anchor="center")  # Place the terminate button at 70% height
button8.place(relx=0.50, rely=0.723, anchor="center")  # Place the terminate button at 70% height

#label Positioning
title_label1.place(relx=0.52, rely=0.15, anchor="center")
title_label2.place(relx=0.49, rely=0.45, anchor="center")
title_label3.place(relx=0.6, rely=0.45, anchor="center")  # Place the terminate button at 45% height
title_label4.place(relx=0.49, rely=0.72, anchor="center")  # Place the terminate button at 72% height

window.mainloop()
