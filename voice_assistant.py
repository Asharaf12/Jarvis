import speech_recognition as sr
import pyttsx3
import os
import pywhatkit
import time
import threading

# Initialize speech engine only once
engine = pyttsx3.init()

def speak(text):
    """Speak the given text using the pyttsx3 engine."""
    engine.say(text)
    engine.runAndWait()  # Ensure the engine is not already running

def listen():
    """Listen to the user's voice command and return the recognized text."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
            audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds
        try:
            command = recognizer.recognize_google(audio)
            print(f"User said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
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

def set_alarm(time):
    """Set an alarm for the specified time."""
    speak(f"Alarm set for {time}")
    while True:
        current_time = time.strftime("%H:%M")
        if current_time == time:
            speak("Time to wake up!")
            break
        time.sleep(60)

def send_message(app, contact, message):
    """Send a message using the specified app."""
    if app == 'whatsapp':
        pywhatkit.sendwhatmsg_instantly(contact, message)
    elif app == 'instagram':
        speak("Instagram messaging is not supported yet.")
    elif app == 'message':
        speak("SMS messaging is not supported yet.")

def close_app(app_name):
    """Close the specified application."""
    os.system(f"taskkill /f /im {app_name}.exe")

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
            time = command.split('set alarm ')[1]
            set_alarm(time)
        elif 'send message' in command:
            parts = command.split(' ')
            app = parts[2]
            contact = parts[4]
            message = ' '.join(parts[6:])
            send_message(app, contact, message)
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