import os
from voice_assistant import main as voice_assistant_main, speak, listen
from person_recognition import initialize_database, add_details, search_person, delete_person_by_photo, replace_details
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading

# Global variable to control the voice assistant thread
voice_thread = None
voice_assistant_running = False

def start_voice_assistant():
    global voice_thread, voice_assistant_running
    if not voice_assistant_running:
        voice_assistant_running = True
        voice_thread = threading.Thread(target=voice_assistant_main, daemon=True)
        voice_thread.start()
        speak("Voice assistant started. How can I assist you?")
    else:
        speak("Voice assistant is already running.")

def stop_voice_assistant():
    global voice_assistant_running
    if voice_assistant_running:
        speak("Going to sleep. Goodbye!")
        voice_assistant_running = False
    else:
        speak("Voice assistant is not running.")

def minimize_window(root):
    root.iconify()  # Minimize the window

def main():
    # Initialize the database
    initialize_database()

    # Create the main application window
    root = tk.Tk()
    root.title("Jarvis AI Assistant")
    root.attributes("-fullscreen", True)  # Set the window to full screen

    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Load the background image
    background_image_path = "bg2.webp"  # Replace with your image path
    if not os.path.exists(background_image_path):
        messagebox.showerror("Error", "Background image not found!")
        return

    # Open and resize the background image to fit the screen
    background_image = Image.open(background_image_path)
    background_image = background_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)

    # Create a Canvas widget to display the background image
    canvas = tk.Canvas(root, width=screen_width, height=screen_height)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Use ttk.Style to customize button appearance
    style = ttk.Style()

    # Configure button style
    style.configure(
        "Custom.TButton",
        font=("Helvetica", 12),
        padding=3,
        borderwidth=1,
        relief="flat",
    )

    # Add hover effects
    style.map(
        "Custom.TButton",
        background=[("active", "#e0e0e0")],
        foreground=[("active", "#000000")],
    )

    # Add buttons on top of the background image
    add_button = ttk.Button(root, text="Add Person Details", command=add_details, style="Custom.TButton")
    search_button = ttk.Button(root, text="Search Person", command=search_person, style="Custom.TButton")
    delete_button = ttk.Button(root, text="Delete Person by Photo", command=delete_person_by_photo, style="Custom.TButton")
    replace_button = ttk.Button(root, text="Replace Person Details", command=replace_details, style="Custom.TButton")
    start_voice_button = ttk.Button(root, text="Start Voice Assistant", command=start_voice_assistant, style="Custom.TButton")
    stop_voice_button = ttk.Button(root, text="Stop Voice Assistant", command=stop_voice_assistant, style="Custom.TButton")

    # Place the first 3 buttons in the bottom-right corner
    canvas.create_window(screen_width - 200, screen_height - 300, window=add_button)
    canvas.create_window(screen_width - 200, screen_height - 250, window=search_button)
    canvas.create_window(screen_width - 200, screen_height - 200, window=delete_button)

    # Place the next 3 buttons in the bottom-left corner
    canvas.create_window(200, screen_height - 300, window=replace_button)
    canvas.create_window(200, screen_height - 250, window=start_voice_button)
    canvas.create_window(200, screen_height - 200, window=stop_voice_button)

    # Add an exit button
    exit_button = ttk.Button(root, text="Exit", command=root.destroy, style="Custom.TButton")
    canvas.create_window(screen_width - 50, 20, window=exit_button)  # Place exit button

    #  Add a Minimize Button
    minimize_button = ttk.Button(root, text="Minimize", command=lambda: minimize_window(root), style="Custom.TButton")
    canvas.create_window(50, 20, window=minimize_button)  # Place minimize button
    root.mainloop()

if __name__ == "__main__":
    main()
