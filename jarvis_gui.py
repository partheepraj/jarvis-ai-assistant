import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import speech_recognition as sr
import pyttsx3
import threading
import time
from safe_agent import agent

# -----------------------------
# INIT VOICE ENGINE
# -----------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 180)  # Speed of speech
engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

def speak(text):
    def speak_thread():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=speak_thread, daemon=True).start()

# -----------------------------
# MAIN APP
# -----------------------------
class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Jarvis AI Assistant")
        self.root.geometry("700x600")
        self.root.configure(bg='#2c3e50')

        # Style
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)
        style.configure('TLabel', font=('Arial', 10))

        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Chat", command=self.clear_chat, accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit, accelerator="Ctrl+Q")

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Voice Settings", command=self.voice_settings)
        settings_menu.add_command(label="About", command=self.show_about)

        # Main frame
        main_frame = tk.Frame(root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = tk.Label(main_frame, text="🤖 Jarvis AI Assistant",
                              font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(pady=5)

        # Chat area
        chat_frame = tk.Frame(main_frame, bg='#34495e', bd=2, relief=tk.SUNKEN)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.chat = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=('Arial', 11),
                                            bg='#ecf0f1', fg='#2c3e50', insertbackground='black')
        self.chat.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat.insert(tk.END, "Jarvis: Hello! I'm ready to help. Type a command or click the voice button.\n\n")

        # Quick actions frame
        actions_frame = tk.Frame(main_frame, bg='#2c3e50')
        actions_frame.pack(fill=tk.X, pady=5)

        ttk.Button(actions_frame, text="🔍 Search Web", command=lambda: self.quick_command("search web")).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="🌐 Open Chrome", command=lambda: self.quick_command("open chrome")).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="📁 List Files", command=lambda: self.quick_command("list files")).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="💻 System Info", command=lambda: self.quick_command("system info")).pack(side=tk.LEFT, padx=2)

        # Input frame
        input_frame = tk.Frame(main_frame, bg='#2c3e50')
        input_frame.pack(fill=tk.X, pady=5)

        self.entry = tk.Entry(input_frame, font=('Arial', 12), bg='white', fg='black', insertbackground='black')
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.entry.bind('<Return>', lambda e: self.send_command())
        self.entry.focus()

        # Buttons frame
        buttons_frame = tk.Frame(input_frame, bg='#2c3e50')
        buttons_frame.pack(side=tk.RIGHT)

        self.send_btn = ttk.Button(buttons_frame, text="📤 Send", command=self.send_command)
        self.send_btn.pack(side=tk.LEFT, padx=2)

        self.voice_btn = ttk.Button(buttons_frame, text="🎤 Voice", command=self.voice_command)
        self.voice_btn.pack(side=tk.LEFT, padx=2)

        self.clear_btn = ttk.Button(buttons_frame, text="🗑️ Clear", command=self.clear_chat)
        self.clear_btn.pack(side=tk.LEFT, padx=2)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
                             anchor=tk.W, bg='#bdc3c7', fg='#2c3e50')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Keyboard shortcuts
        root.bind('<Control-l>', lambda e: self.clear_chat())
        root.bind('<Control-q>', lambda e: root.quit())
        root.bind('<Control-r>', lambda e: self.voice_command())

        # Voice listening flag
        self.listening = False

    # -------------------------
    # TEXT COMMAND
    # -------------------------
    def send_command(self):
        command = self.entry.get().strip()
        if not command:
            return

        self.entry.delete(0, tk.END)
        self.status_var.set("Processing...")

        self.chat.insert(tk.END, f"You: {command}\n", 'user')
        self.chat.tag_config('user', foreground='#e74c3c', font=('Arial', 11, 'bold'))

        try:
            response = agent(command)
            self.chat.insert(tk.END, f"Jarvis: {response}\n\n", 'jarvis')
            self.chat.tag_config('jarvis', foreground='#27ae60', font=('Arial', 11, 'bold'))
            speak(response)
        except Exception as e:
            error_msg = f"Sorry, an error occurred: {str(e)}"
            self.chat.insert(tk.END, f"Jarvis: {error_msg}\n\n", 'error')
            self.chat.tag_config('error', foreground='#e67e22')
            speak("Sorry, an error occurred")

        self.chat.see(tk.END)
        self.status_var.set("Ready")

    # -------------------------
    # VOICE COMMAND
    # -------------------------
    def voice_command(self):
        if self.listening:
            return

        self.listening = True
        self.voice_btn.config(state='disabled')
        self.status_var.set("Listening...")

        def listen_thread():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.chat.insert(tk.END, "🎤 Listening...\n", 'system')
                self.chat.tag_config('system', foreground='#9b59b6', font=('Arial', 10, 'italic'))
                self.chat.see(tk.END)

                try:
                    audio = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(audio).lower()

                    self.chat.insert(tk.END, f"You (voice): {command}\n", 'voice_user')
                    self.chat.tag_config('voice_user', foreground='#e74c3c', font=('Arial', 11, 'bold', 'italic'))

                    response = agent(command)

                    self.chat.insert(tk.END, f"Jarvis: {response}\n\n", 'jarvis')
                    self.chat.tag_config('jarvis', foreground='#27ae60', font=('Arial', 11, 'bold'))
                    speak(response)

                except sr.WaitTimeoutError:
                    self.chat.insert(tk.END, "Jarvis: No speech detected\n\n", 'error')
                except sr.UnknownValueError:
                    self.chat.insert(tk.END, "Jarvis: Couldn't understand the audio\n\n", 'error')
                except sr.RequestError:
                    self.chat.insert(tk.END, "Jarvis: Speech recognition service unavailable\n\n", 'error')
                except Exception as e:
                    self.chat.insert(tk.END, f"Jarvis: Error: {str(e)}\n\n", 'error')
                    self.chat.tag_config('error', foreground='#e67e22')

                self.chat.see(tk.END)

            self.listening = False
            self.voice_btn.config(state='normal')
            self.status_var.set("Ready")

        threading.Thread(target=listen_thread, daemon=True).start()

    # -------------------------
    # QUICK COMMANDS
    # -------------------------
    def quick_command(self, command):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, command)
        self.send_command()

    # -------------------------
    # CLEAR CHAT
    # -------------------------
    def clear_chat(self):
        self.chat.delete(1.0, tk.END)
        self.chat.insert(tk.END, "Jarvis: Chat cleared. Ready for new commands!\n\n")

    # -------------------------
    # VOICE SETTINGS
    # -------------------------
    def voice_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Voice Settings")
        settings_window.geometry("300x200")

        tk.Label(settings_window, text="Voice Settings", font=('Arial', 14, 'bold')).pack(pady=10)

        # Voice rate
        rate_frame = tk.Frame(settings_window)
        rate_frame.pack(pady=5)
        tk.Label(rate_frame, text="Speech Rate:").pack(side=tk.LEFT)
        rate_scale = tk.Scale(rate_frame, from_=100, to=300, orient=tk.HORIZONTAL)
        rate_scale.set(180)
        rate_scale.pack(side=tk.LEFT)
        rate_scale.config(command=lambda v: engine.setProperty('rate', int(v)))

        # Voice volume
        vol_frame = tk.Frame(settings_window)
        vol_frame.pack(pady=5)
        tk.Label(vol_frame, text="Volume:").pack(side=tk.LEFT)
        vol_scale = tk.Scale(vol_frame, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL)
        vol_scale.set(0.9)
        vol_scale.pack(side=tk.LEFT)
        vol_scale.config(command=lambda v: engine.setProperty('volume', float(v)))

        tk.Button(settings_window, text="Test Voice", command=lambda: speak("This is a test of the voice settings")).pack(pady=10)

    # -------------------------
    # ABOUT
    # -------------------------
    def show_about(self):
        messagebox.showinfo("About Jarvis AI",
                           "Jarvis AI Assistant v2.0\n\n"
                           "An advanced AI agent with voice control,\n"
                           "system automation, and intelligent responses.\n\n"
                           "Features:\n"
                           "• Voice commands\n"
                           "• System control\n"
                           "• Web search\n"
                           "• File management\n"
                           "• And much more!")

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()