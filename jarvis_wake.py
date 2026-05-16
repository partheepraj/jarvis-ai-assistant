import speech_recognition as sr
import pyttsx3
from safe_agent import agent

# -----------------------------
# INIT VOICE ENGINE
# -----------------------------
engine = pyttsx3.init()

def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

# -----------------------------
# LISTEN FUNCTION
# -----------------------------
def listen_command(timeout=5):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio)
            print("You:", command)
            return command.lower()

        except:
            return None

# -----------------------------
# WAKE WORD DETECTION
# -----------------------------
def listen_wake_word():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("👂 Waiting for 'Hey Jarvis'...")

        recognizer.adjust_for_ambient_noise(source)

        while True:
            try:
                audio = recognizer.listen(source, timeout=None)
                text = recognizer.recognize_google(audio).lower()

                if "hey jarvis" in text:
                    print("⚡ Wake word detected!")
                    speak("Yes, how can I help?")
                    return

            except:
                continue

# -----------------------------
# MAIN LOOP
# -----------------------------
print("🤖 JARVIS WITH WAKE WORD STARTED")

while True:

    # 1️⃣ Wait for wake word
    listen_wake_word()

    # 2️⃣ Listen for command
    command = listen_command()

    if command is None:
        speak("I didn't catch that")
        continue

    if "exit" in command:
        speak("Goodbye")
        break

    # 3️⃣ Execute
    response = agent(command)
    speak(response)