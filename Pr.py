import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import face_recognition
import os
from PIL import Image, ImageTk
import numpy as np

# Database setup
DATABASE_FILE = "person_database.db"

def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            place TEXT NOT NULL,
            state TEXT NOT NULL,
            photo_path TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Function to upload a photo
def upload_photo(photo_path_label):
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
    if file_path:
        photo_path_label.config(text=file_path)

def add_details():
    def save_details():
        name = name_entry.get()
        dob = dob_entry.get()
        address = address_entry.get()
        phone = phone_entry.get()
        place = place_entry.get()
        state = state_entry.get()
        photo_path = photo_path_label.cget("text")

        if not all([name, dob, address, phone, place, state, photo_path]):
            messagebox.showerror("Error", "All fields are required!")
            return

        # Check if the person already exists
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM persons WHERE photo_path = ?", (photo_path,))
        existing_person = cursor.fetchone()

        if existing_person:
            # Ask the user if they want to replace the existing details
            replace = messagebox.askyesno("Person Exists", "This person already exists. Do you want to replace their details?")
            if not replace:
                conn.close()
                return

            # Update existing person's details
            cursor.execute('''
                UPDATE persons
                SET name = ?, dob = ?, address = ?, phone = ?, place = ?, state = ?
                WHERE photo_path = ?
            ''', (name, dob, address, phone, place, state, photo_path))
            messagebox.showinfo("Success", "Details updated successfully!")
        else:
            # Insert new person's details
            cursor.execute('''
                INSERT INTO persons (name, dob, address, phone, place, state, photo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, dob, address, phone, place, state, photo_path))
            messagebox.showinfo("Success", "Details added successfully!")

        conn.commit()
        conn.close()
        clear_form()

    def clear_form():
        name_entry.delete(0, tk.END)
        dob_entry.delete(0, tk.END)
        address_entry.delete(0, tk.END)
        phone_entry.delete(0, tk.END)
        place_entry.delete(0, tk.END)
        state_entry.delete(0, tk.END)
        photo_path_label.config(text="")

    add_window = tk.Toplevel()
    add_window.title("Add Person Details")
    add_window.geometry("400x400")

    tk.Label(add_window, text="Name:").pack()
    name_entry = tk.Entry(add_window)
    name_entry.pack()

    tk.Label(add_window, text="DOB:").pack()
    dob_entry = tk.Entry(add_window)
    dob_entry.pack()

    tk.Label(add_window, text="Address:").pack()
    address_entry = tk.Entry(add_window)
    address_entry.pack()

    tk.Label(add_window, text="Phone:").pack()
    phone_entry = tk.Entry(add_window)
    phone_entry.pack()

    tk.Label(add_window, text="Place:").pack()
    place_entry = tk.Entry(add_window)
    place_entry.pack()

    tk.Label(add_window, text="State:").pack()
    state_entry = tk.Entry(add_window)
    state_entry.pack()

    tk.Label(add_window, text="Photo:").pack()
    photo_path_label = tk.Label(add_window, text="", fg="blue")
    photo_path_label.pack()
    tk.Button(add_window, text="Upload Photo", command=lambda: upload_photo(photo_path_label)).pack()

    tk.Button(add_window, text="Add Details", command=save_details).pack(pady=10)

def delete_person_by_photo():
    def delete_details():
        search_photo_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if not search_photo_path:
            return

        try:
            # Load and encode the uploaded image
            uploaded_image = face_recognition.load_image_file(search_photo_path)
            uploaded_image = resize_image(uploaded_image)  # Resize image to reduce processing time
            uploaded_encodings = face_recognition.face_encodings(uploaded_image)

            if not uploaded_encodings:
                messagebox.showerror("Error", "No face detected in the uploaded photo!")
                return

            uploaded_encoding = uploaded_encodings[0]

            # Compare with all stored photos
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons")
            persons = cursor.fetchall()
            conn.close()

            match_found = False

            for person in persons:
                person_id, name, dob, address, phone, place, state, photo_path = person

                if not os.path.exists(photo_path):
                    continue  # Skip if file does not exist

                stored_image = face_recognition.load_image_file(photo_path)
                stored_image = resize_image(stored_image)  # Resize image to reduce processing time
                stored_encodings = face_recognition.face_encodings(stored_image)

                if not stored_encodings:
                    continue  # Skip if no face detected

                stored_encoding = stored_encodings[0]
                match = face_recognition.compare_faces([stored_encoding], uploaded_encoding)

                if match[0]:
                    # Confirm deletion
                    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {name}'s details?")
                    if confirm:
                        conn = sqlite3.connect(DATABASE_FILE)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM persons WHERE id = ?", (person_id,))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Success", "Details deleted successfully!")
                    match_found = True
                    break

            if not match_found:
                messagebox.showinfo("Search Result", "No match found!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    delete_window = tk.Toplevel()
    delete_window.title("Delete Person by Photo")
    delete_window.geometry("300x100")

    tk.Button(delete_window, text="Upload Photo to Delete", command=delete_details).pack(pady=20)

def replace_details():
    def replace_person_details():
        search_photo_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if not search_photo_path:
            return

        try:
            # Load and encode the uploaded image
            uploaded_image = face_recognition.load_image_file(search_photo_path)
            uploaded_image = resize_image(uploaded_image)  # Resize image to reduce processing time
            uploaded_encodings = face_recognition.face_encodings(uploaded_image)

            if not uploaded_encodings:
                messagebox.showerror("Error", "No face detected in the uploaded photo!")
                return

            uploaded_encoding = uploaded_encodings[0]

            # Compare with all stored photos
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons")
            persons = cursor.fetchall()
            conn.close()

            match_found = False

            for person in persons:
                person_id, name, dob, address, phone, place, state, photo_path = person

                if not os.path.exists(photo_path):
                    continue  # Skip if file does not exist

                stored_image = face_recognition.load_image_file(photo_path)
                stored_image = resize_image(stored_image)  # Resize image to reduce processing time
                stored_encodings = face_recognition.face_encodings(stored_image)

                if not stored_encodings:
                    continue  # Skip if no face detected

                stored_encoding = stored_encodings[0]
                match = face_recognition.compare_faces([stored_encoding], uploaded_encoding)

                if match[0]:
                    # Open a new window to replace details
                    replace_window = tk.Toplevel()
                    replace_window.title("Replace Person Details")
                    replace_window.geometry("400x400")

                    tk.Label(replace_window, text="Name:").pack()
                    name_entry = tk.Entry(replace_window)
                    name_entry.insert(0, name)
                    name_entry.pack()

                    tk.Label(replace_window, text="DOB:").pack()
                    dob_entry = tk.Entry(replace_window)
                    dob_entry.insert(0, dob)
                    dob_entry.pack()

                    tk.Label(replace_window, text="Address:").pack()
                    address_entry = tk.Entry(replace_window)
                    address_entry.insert(0, address)
                    address_entry.pack()

                    tk.Label(replace_window, text="Phone:").pack()
                    phone_entry = tk.Entry(replace_window)
                    phone_entry.insert(0, phone)
                    phone_entry.pack()

                    tk.Label(replace_window, text="Place:").pack()
                    place_entry = tk.Entry(replace_window)
                    place_entry.insert(0, place)
                    place_entry.pack()

                    tk.Label(replace_window, text="State:").pack()
                    state_entry = tk.Entry(replace_window)
                    state_entry.insert(0, state)
                    state_entry.pack()

                    def save_replaced_details():
                        new_name = name_entry.get()
                        new_dob = dob_entry.get()
                        new_address = address_entry.get()
                        new_phone = phone_entry.get()
                        new_place = place_entry.get()
                        new_state = state_entry.get()

                        if not all([new_name, new_dob, new_address, new_phone, new_place, new_state]):
                            messagebox.showerror("Error", "All fields are required!")
                            return

                        conn = sqlite3.connect(DATABASE_FILE)
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE persons
                            SET name = ?, dob = ?, address = ?, phone = ?, place = ?, state = ?
                            WHERE id = ?
                        ''', (new_name, new_dob, new_address, new_phone, new_place, new_state, person_id))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Success", "Details replaced successfully!")
                        replace_window.destroy()

                    tk.Button(replace_window, text="Save Changes", command=save_replaced_details).pack(pady=10)
                    match_found = True
                    break

            if not match_found:
                messagebox.showinfo("Search Result", "No match found!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    replace_window = tk.Toplevel()
    replace_window.title("Replace Person Details")
    replace_window.geometry("300x100")

    tk.Button(replace_window, text="Upload Photo to Replace", command=replace_person_details).pack(pady=20)

def search_person():
    def search_by_photo():
        search_photo_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if not search_photo_path:
            return

        try:
            # Load and encode the uploaded image
            uploaded_image = face_recognition.load_image_file(search_photo_path)
            uploaded_image = resize_image(uploaded_image)  # Resize image to reduce processing time
            uploaded_encodings = face_recognition.face_encodings(uploaded_image)

            if not uploaded_encodings:
                messagebox.showerror("Error", "No face detected in the uploaded photo!")
                return

            uploaded_encoding = uploaded_encodings[0]

            # Compare with all stored photos
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons")
            persons = cursor.fetchall()
            conn.close()

            match_found = False

            for person in persons:
                person_id, name, dob, address, phone, place, state, photo_path = person

                if not os.path.exists(photo_path):
                    continue  # Skip if file does not exist

                stored_image = face_recognition.load_image_file(photo_path)
                stored_image = resize_image(stored_image)  # Resize image to reduce processing time
                stored_encodings = face_recognition.face_encodings(stored_image)

                if not stored_encodings:
                    continue  # Skip if no face detected

                stored_encoding = stored_encodings[0]
                match = face_recognition.compare_faces([stored_encoding], uploaded_encoding)

                if match[0]:
                    result = (
                        f"Name: {name}\n"
                        f"DOB: {dob}\n"
                        f"Address: {address}\n"
                        f"Phone: {phone}\n"
                        f"Place: {place}\n"
                        f"State: {state}"
                    )
                    messagebox.showinfo("Search Result", result)
                    match_found = True
                    break

            if not match_found:
                messagebox.showinfo("Search Result", "No match found!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    search_window = tk.Toplevel()
    search_window.title("Search Person")
    search_window.geometry("300x100")

    tk.Button(search_window, text="Upload Photo to Search", command=search_by_photo).pack(pady=20)

def resize_image(image, max_size=500):
    """Resize the image to a maximum dimension while maintaining aspect ratio."""
    pil_image = Image.fromarray(image)
    width, height = pil_image.size
    if max(width, height) > max_size:
        ratio = max_size / max(width, height)
        new_size = (int(width * ratio), int(height * ratio))
        pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)  # Updated resampling method
        return np.array(pil_image)  # Convert PIL.Image back to NumPy array
    return image

# Main application
def main():
    initialize_database()

    root = tk.Tk()
    root.title("Person Database")
    root.geometry("800x600")  # Adjust window size to fit the background image

    # Load the background image
    background_image_path = "bg2.webp"  # Replace with your image path
    if not os.path.exists(background_image_path):
        messagebox.showerror("Error", "Background image not found!")
        return

    background_image = Image.open(background_image_path)
    background_image = background_image.resize((800, 600), Image.Resampling.LANCZOS)  # Resize to fit window
    background_photo = ImageTk.PhotoImage(background_image)

    # Create a Canvas widget to display the background image
    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo, anchor="nw")

    # Add buttons on top of the background image
    add_button = tk.Button(root, text="Add Person Details", command=add_details, bg="white", fg="black")
    search_button = tk.Button(root, text="Search Person", command=search_person, bg="white", fg="black")
    delete_button = tk.Button(root, text="Delete Person by Photo", command=delete_person_by_photo, bg="white", fg="black")
    replace_button = tk.Button(root, text="Replace Person Details", command=replace_details, bg="white", fg="black")

    # Place buttons on the canvas
    canvas.create_window(400, 200, window=add_button)
    canvas.create_window(400, 300, window=search_button)
    canvas.create_window(400, 400, window=delete_button)
    canvas.create_window(400, 500, window=replace_button)

    root.mainloop()

if __name__ == "__main__":
    main()