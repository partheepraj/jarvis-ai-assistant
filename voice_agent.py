import speech_recognition as sr
import pyttsx3
from safe_agent import agent   # import your AI agent

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
def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)

            print("You said:", command)
            return command.lower()

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand")
            return None
        except sr.RequestError:
            speak("Internet error")
            return None

# -----------------------------
# MAIN LOOP
# -----------------------------
print("🤖 Voice Jarvis Started (say 'exit' to stop)")

while True:
    command = listen()

    if command is None:
        continue

    if "exit" in command:
        speak("Goodbye")
        break

    # 🔥 send to your AI agent
    response = agent(command)

    speak(response)