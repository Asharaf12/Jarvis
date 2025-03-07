import speech_recognition as sr
import pyttsx3
import os
import pywhatkit
import time
import threading
import datetime

# Initialize speech engine only once
engine = pyttsx3.init()

# Contact book mapping names to phone numbers
contact_book = {
    "john": "+1234567890",  # Replace with actual phone numbers
    "alice": "+9876543210",
    "jarvis": "+1111111111",
    "amma": "+919876543210",  # Example Indian number
}

def speak(text):
    """Speak the given text using the pyttsx3 engine."""
    engine.say(text)
    if not engine._inLoop:  # Check if the engine is already running
        engine.runAndWait()

def listen():
    """Listen to the user's voice command and return the recognized text."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            # Adjust for ambient noise and set a higher timeout for better recognition
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=60, phrase_time_limit=8)  # Listen for 5 seconds
        try:
            command = recognizer.recognize_google(audio)
            print(f"User said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("I didn't catch that. Could you please repeat?")
            return ""
        except sr.RequestError:
            speak("Sorry, my speech service is down. Please check your internet connection.")
            return ""
    except OSError:
        speak("Microphone not found. Please check your microphone.")
        return ""

def open_app(app_name):
    """Open the specified application or website."""
    apps = {
        'google': 'start chrome https://www.google.com',
        'whatsapp': 'start chrome https://web.whatsapp.com',
        'instagram': 'start chrome https://www.instagram.com',
        'youtube': 'start chrome https://www.youtube.com',
        'drive': 'start chrome https://drive.google.com',
        'facebook': 'start chrome https://www.facebook.com',
        'chrome': 'start chrome',
        'clock': 'start ms-clock:',
        'twitter': 'start chrome https://twitter.com',
        'snapchat': 'start chrome https://www.snapchat.com',
        'notepad': 'notepad',
        'message': 'start ms-messaging:',
        'camera': 'start microsoft.windows.camera:',
        'file manager': 'explorer',
        'gmail': 'start chrome https://mail.google.com',
        'music': 'start wmplayer',
        'settings': 'start ms-settings:'
    }
    if app_name in apps:
        os.system(apps[app_name])
    else:
        speak("App not found.")

def set_alarm(alarm_time):
    """Set an alarm for the specified time."""
    speak(f"Alarm set for {alarm_time}")
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")
        if current_time == alarm_time:
            speak("Time to wake up!")
            break
        time.sleep(30)  # Check every 30 seconds to reduce CPU usage

def send_message(command):
    """Send a message using the specified app."""
    parts = command.split(' ')
    if len(parts) < 4:
        speak("Invalid command format. Please say 'send message to <contact> <message>'.")
        return

    # Default app is WhatsApp
    app = 'whatsapp'
    contact = parts[3].strip().lower()  # Contact name (trimmed and lowercase)
    message = ' '.join(parts[4:])  # Message

    print(f"Contact book: {contact_book}")  # Debug
    print(f"Looking for contact: {contact}")  # Debug

    if app == 'whatsapp':
        try:
            # Look up the phone number from the contact book
            if contact in contact_book:
                phone_number = contact_book[contact]
                print(f"Phone number for {contact}: {phone_number}")  # Debug
                print(f"Message: {message}")  # Debug

                # Add a delay to ensure WhatsApp Web is ready
                speak("Sending message. Please wait...")
                time.sleep(5)  # Wait for 5 seconds

                # Send the message instantly
                pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=15, tab_close=True)
                speak(f"Message sent to {contact}.")
            else:
                speak(f"Contact '{contact}' not found in the contact book.")
        except Exception as e:
            speak(f"Failed to send message. Error: {e}")
            print(f"Error: {e}")  # Debug
    elif app == 'instagram':
        speak("Instagram messaging is not supported yet.")
    elif app == 'message':
        speak("SMS messaging is not supported yet.")

def close_app(app_name):
    """Close the specified application."""
    app_mapping = {
        'chrome': 'chrome.exe',
        'file manager': 'explorer.exe',
        'notepad': 'notepad.exe',
        'music': 'wmplayer.exe',
    }
    executable = app_mapping.get(app_name, f"{app_name}.exe")
    os.system(f"taskkill /f /im {executable}")

def analyze_photo(photo_path):
    """Analyze a photo (not implemented)."""
    speak("Photo analysis is not implemented yet.")

def search(query):
    """Search the web for the given query."""
    pywhatkit.search(query)

def main():
    """Main function to run the voice assistant."""
    speak("Hello, I am Jarvis. How can I assist you?")
    while True:
        command = listen()
        if not command:
            continue  # Skip if no command is recognized

        if 'hello jarvis' in command:
            speak("Hello, how can I assist you?")
        elif 'open' in command:
            app_name = command.split('open ')[1]
            open_app(app_name)
        elif 'set alarm' in command:
            alarm_time = command.split('set alarm ')[1]
            set_alarm(alarm_time)
        elif 'send message' in command:
            send_message(command)  # Updated call
        elif 'close' in command:
            app_name = command.split('close ')[1]
            close_app(app_name)
        elif 'analyze photo' in command:
            photo_path = command.split('analyze photo ')[1]
            analyze_photo(photo_path)
        elif 'search' in command:
            query = command.split('search ')[1]
            search(query)
        elif 'ok jarvis go to sleep' in command:
            speak("Goodbye Sir!")
            break

if __name__ == "__main__":
    # Run the voice assistant in a separate thread
    voice_thread = threading.Thread(target=main, daemon=True)
    voice_thread.start()

    # Keep the main thread alive to allow the voice assistant to run
    while True:
        time.sleep(1)