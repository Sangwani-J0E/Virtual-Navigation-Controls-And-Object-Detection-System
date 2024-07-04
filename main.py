import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import customtkinter
import sys

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

# Create a window
window = tk.Tk()
window.title("AI Virtual System")

# Load the background image
background_image = Image.open("background.png")
background_photo = ImageTk.PhotoImage(background_image)

# Create a canvas
canvas = tk.Canvas(window, width=background_image.width, height=background_image.height, bg="white")
canvas.pack(fill="both", expand=True)

# Add the background image to the canvas
background = canvas.create_image(0, 0, anchor="nw", image=background_photo)

# Bind the resize_image function to the canvas's resize event
canvas.bind("<Configure>", resize_image)

# Label for "AI Virtual System" text
#title_label = tk.Label(canvas, text="AI Virtual System", font=("Arial", 50, "bold"), bg="#f2f2f2", fg="red", border=10)
#title_label.place(relx=0.5, rely=0.1, anchor="center")

# Custom buttons
buttons = [
    ("AI Mouse", Run_SHT),
    ("Virtual Keyboard", Run_VirtualKeyboard),
    ("Object Detection", Run_ObjectDetection),
    ("Tutorial", Open_Tutorial)
]

# Calculate the vertical position for the buttons
button_height = 70
total_button_height = len(buttons) * button_height
start_y = (background_image.height - total_button_height) // 2

# Create buttons
for i, (button_text, command) in enumerate(buttons):
    button_y = start_y + i * button_height
    button = customtkinter.CTkButton(canvas, text=button_text, fg_color="#B71C1C", bg_color='#FFFFFF',
                                     font=("Arial", 24, "bold"), command=command, corner_radius=20, width=350,
                                     height=button_height)
    button.place(relx=0.5, rely=(0.55 + (i - len(buttons) // 2) * 0.11), anchor="center")

# Back button
Back_button = customtkinter.CTkButton(canvas, text="Back", fg_color="#FFFFFF", bg_color='#B71C1C', text_color= "#B71C1C",
                                      font=("Arial", 22, "bold"), command=close_subprocess, corner_radius=20, width=120,
                                      height=65)
Back_button.place(relx=0.02, rely=0.9, anchor="sw")

# Initialize the subprocess instance variable
subprocess_instance = None

# Run the application
window.mainloop()