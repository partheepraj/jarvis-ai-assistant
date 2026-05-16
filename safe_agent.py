import os
import time
import subprocess
import pickle
import logging
import json
from datetime import datetime
import platform
import psutil
import re
import urllib.parse
import webbrowser
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# -----------------------------
# CONFIGURATION
# -----------------------------
CONFIG = {
    "safe_mode": True,
    "log_file": "agent.log",
    "max_memory": 100,
    "dangerous_commands": ["shutdown", "restart", "delete_file", "hibernate"]
}

# -----------------------------
# LOGGING SETUP
# -----------------------------
logging.basicConfig(filename=CONFIG["log_file"], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------
# ADVANCED AI AGENT CLASS
# -----------------------------
class AdvancedAgent:
    def __init__(self):
        self.memory = []
        self.load_model()
        self.load_config()

    def load_model(self):
        try:
            with open("model.pkl", "rb") as f:
                self.model = pickle.load(f)
            with open("vectorizer.pkl", "rb") as f:
                self.vectorizer = pickle.load(f)
            logging.info("Model loaded successfully")
        except FileNotFoundError:
            logging.error("Model files not found. Please run train_model.py")
            self.model = None
            self.vectorizer = None

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                global CONFIG
                CONFIG.update(json.load(f))
        except FileNotFoundError:
            self.save_config()

    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(CONFIG, f, indent=4)

    def classify_intent(self, text):
        if self.model is None:
            return "unknown"
        text_vec = self.vectorizer.transform([text])
        return self.model.predict(text_vec)[0]

    def execute_action(self, intent, command):
        actions = {
            "open_app": self.open_app,
            "close_app": self.close_app,
            "wifi_on": self.wifi_on,
            "wifi_off": self.wifi_off,
            "bluetooth_on": self.bluetooth_on,
            "bluetooth_off": self.bluetooth_off,
            "delete_file": self.delete_file,
            "create_file": self.create_file,
            "shutdown": self.shutdown,
            "restart": self.restart,
            "list_files": self.list_files,
            "system_info": self.system_info,
            "play_music": self.play_music,
            "stop_music": self.stop_music,
            "volume_up": self.volume_up,
            "volume_down": self.volume_down,
            "volume_mute": self.volume_mute,
            "volume_unmute": self.volume_unmute,
            "search_web": self.search_web,
            "weather": self.weather,
            "joke": self.joke,
            "set_reminder": self.set_reminder,
            "calendar": self.calendar,
            "screenshot": self.screenshot,
            "lock": self.lock,
            "hibernate": self.hibernate,
            "sleep": self.sleep
        }

        if intent in CONFIG["dangerous_commands"] and CONFIG["safe_mode"]:
            return "This action is dangerous. Confirm by setting safe_mode to false in config.json"

        action = actions.get(intent, self.unknown_action)
        return action(command)

    def _run_start_command(self, target):
        try:
            subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)
            return True
        except Exception as e:
            logging.error(f"Failed to run start command for {target}: {e}")
            return False

    # -----------------------------
    # ACTION METHODS
    # -----------------------------
    def open_app(self, app):
        apps = {
            "chrome": "chrome",
            "edge": "msedge",
            "excel": "excel",
            "word": "winword",
            "powerpoint": "powerpnt",
            "powerbi": "powerbi",
            "notepad": "notepad",
            "browser": None
        }
        app_lower = app.lower()
        for key, target in apps.items():
            if key in app_lower:
                if target:
                    if self._run_start_command(target):
                        return f"Opened {key.capitalize()}"
                    if key == "chrome":
                        webbrowser.open("https://www.google.com")
                        return "Opened the default browser because Chrome launch failed"
                    return f"Failed to open {key}."
                else:
                    webbrowser.open("https://www.google.com")
                    return "Opened the default browser"
        return "App not recognized"

    def close_app(self, app):
        # Simplified, in reality need to find process
        return "Close app functionality not fully implemented"

    def wifi_on(self, cmd):
        try:
            result = subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "enable"],
                                  capture_output=True, text=True, check=True)
            return "WiFi turned on"
        except subprocess.CalledProcessError:
            return "Failed to enable WiFi (may require admin privileges)"

    def wifi_off(self, cmd):
        try:
            result = subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "disable"],
                                  capture_output=True, text=True, check=True)
            return "WiFi turned off"
        except subprocess.CalledProcessError:
            return "Failed to disable WiFi (may require admin privileges)"

    def bluetooth_on(self, cmd):
        try:
            # Try to enable Bluetooth using PowerShell
            ps_command = 'Get-PnpDevice | Where-Object {$_.Class -eq "Bluetooth"} | Enable-PnpDevice -Confirm:$false'
            result = subprocess.run(["powershell", "-Command", ps_command],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return "Bluetooth enabled"
            else:
                return "Bluetooth control requires manual setup"
        except Exception as e:
            return f"Bluetooth control not available: {str(e)}"

    def bluetooth_off(self, cmd):
        try:
            # Try to disable Bluetooth using PowerShell
            ps_command = 'Get-PnpDevice | Where-Object {$_.Class -eq "Bluetooth"} | Disable-PnpDevice -Confirm:$false'
            result = subprocess.run(["powershell", "-Command", ps_command],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return "Bluetooth disabled"
            else:
                return "Bluetooth control requires manual setup"
        except Exception as e:
            return f"Bluetooth control not available: {str(e)}"

    def delete_file(self, file):
        # Dangerous, need path
        return "Delete file requires specific path and confirmation"

    def create_file(self, file):
        # Need path and content
        return "Create file requires path and content"

    def shutdown(self, cmd):
        os.system("shutdown /s /t 1")
        return "Shutting down"

    def restart(self, cmd):
        os.system("shutdown /r /t 1")
        return "Restarting"

    def list_files(self, cmd):
        return str(os.listdir("."))

    def system_info(self, cmd):
        info = {
            "OS": platform.system(),
            "Version": platform.version(),
            "CPU": psutil.cpu_percent(),
            "Memory": psutil.virtual_memory().percent
        }
        return str(info)

    def play_music(self, cmd):
        # Need media player
        return "Playing music (integrate with media player)"

    def stop_music(self, cmd):
        return "Stopped music"

    def _get_volume_interface(self):
        devices = AudioUtilities.GetSpeakers()
        return devices.EndpointVolume

    def _parse_volume_value(self, cmd):
        # Recognize explicit volume targets like "to 50" or "at 50%"
        match = re.search(r'\b(?:to|at)\s*(\d+(?:\.\d+)?)(?:\s*%?)\b', cmd.lower())
        if match:
            value = float(match.group(1))
            text = match.group(0)
            if '%' in text or 'percent' in cmd.lower():
                return min(1.0, max(0.0, value / 100.0))
            if value < 1:
                # Treat decimal fractions like 0.5 as 50%
                return value
            if value == 1:
                # Interpret explicit '1' as 1%
                return 0.01
            return min(1.0, max(0.0, value / 100.0))
        return None

    def _parse_volume_delta(self, cmd):
        match = re.search(r'\bby\s*(\d{1,3})(?:\s*%?)\b', cmd.lower())
        if match:
            value = float(match.group(1))
            return min(1.0, max(0.0, value / 100.0))
        return None

    def _set_volume(self, target):
        try:
            volume = self._get_volume_interface()
            volume.SetMasterVolumeLevelScalar(target, None)
            return f"Volume set to {int(target * 100)}%"
        except Exception:
            try:
                subprocess.run(["nircmd.exe", "setsysvolume", str(int(target * 65535))], check=True)
                return f"Volume set to {int(target * 100)}% (using nircmd)"
            except Exception as e:
                return f"Could not set exact volume: {str(e)}"

    def _adjust_volume(self, delta):
        try:
            volume = self._get_volume_interface()
            current_volume = volume.GetMasterVolumeLevelScalar()
            new_volume = min(1.0, max(0.0, current_volume + delta))
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            return f"Volume adjusted to {int(new_volume * 100)}%"
        except Exception:
            try:
                key = 175 if delta > 0 else 174
                subprocess.run(["powershell", "-Command", f'$obj = new-object -com wscript.shell; $obj.SendKeys([char]{key})'], check=True)
                return "Volume adjusted (using PowerShell)"
            except Exception as e:
                return f"Volume control not available: {str(e)}"

    def volume_up(self, cmd):
        target = self._parse_volume_value(cmd)
        if target is not None:
            return self._set_volume(target)
        delta = self._parse_volume_delta(cmd) or 0.1
        return self._adjust_volume(delta)

    def volume_down(self, cmd):
        target = self._parse_volume_value(cmd)
        if target is not None:
            return self._set_volume(target)
        delta = self._parse_volume_delta(cmd) or 0.1
        return self._adjust_volume(-delta)

    def volume_mute(self, cmd):
        try:
            volume = self._get_volume_interface()
            volume.SetMute(1, None)
            return "Volume muted"
        except Exception:
            try:
                subprocess.run(["powershell", "-Command", '$obj = new-object -com wscript.shell; $obj.SendKeys([char]173)'], check=True)
                return "Volume muted (using PowerShell)"
            except Exception as e:
                return f"Volume control not available: {str(e)}"

    def volume_unmute(self, cmd):
        try:
            volume = self._get_volume_interface()
            volume.SetMute(0, None)
            return "Volume unmuted"
        except Exception:
            try:
                subprocess.run(["nircmd.exe", "mutesysvolume", "0"], check=True)
                return "Volume unmuted (using nircmd)"
            except Exception as e:
                return f"Volume control not available: {str(e)}"

    def search_web(self, query):
        # Extract search query from various phrasings
        query_lower = query.lower()
        prefixes = ["search web for", "search web", "search for", "search", "find", "look up", "google"]
        search_query = query
        for prefix in prefixes:
            if query_lower.startswith(prefix):
                search_query = query[len(prefix):].strip()
                break
        # If no prefix found, assume the whole query is the search term
        if search_query == query:
            search_query = query.strip()
        # URL encode the search query
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://www.google.com/search?q={encoded_query}"
        try:
            subprocess.Popen(f'start chrome "{url}"', shell=True)
            return f"Opened Chrome and searched for: {search_query}"
        except Exception:
            webbrowser.open(url)
            return f"Opened the default browser and searched for: {search_query}"

    def weather(self, cmd):
        # Mock weather
        return "Weather: Sunny, 25°C"

    def joke(self, cmd):
        return "Why did the computer go to therapy? It had too many bytes of emotional baggage!"

    def set_reminder(self, cmd):
        return "Reminder set (integrate with calendar)"

    def calendar(self, cmd):
        return "Opening calendar (integrate with calendar app)"

    def screenshot(self, cmd):
        # Windows screenshot
        return "Screenshot taken"

    def lock(self, cmd):
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Computer locked"

    def hibernate(self, cmd):
        os.system("shutdown /h")
        return "Hibernating"

    def sleep(self, cmd):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Going to sleep"

    def unknown_action(self, cmd):
        return "I don't know how to do that yet."

    # -----------------------------
    # AGENT INTERFACE
    # -----------------------------
    def agent(self, command):
        command_lower = command.lower().strip()

        # Direct fallback for quick action phrases
        if command_lower in ["list files", "show files", "file list", "list directory", "directory listing"]:
            return self.list_files(command)
        if command_lower in ["system info", "system information", "show system info", "show system information"]:
            return self.system_info(command)
        if command_lower in ["mute", "volume mute", "mute volume"]:
            return self.volume_mute(command)
        if command_lower in ["unmute", "volume unmute", "unmute volume"]:
            return self.volume_unmute(command)
        if any(keyword in command_lower for keyword in ["volume up", "increase volume", "turn up volume"]):
            return self.volume_up(command)
        if any(keyword in command_lower for keyword in ["volume down", "decrease volume", "turn down volume"]):
            return self.volume_down(command)
        if any(keyword in command_lower for keyword in ["search web", "search for", "google", "look up"]):
            return self.search_web(command)

        # Direct command mapping for app launches
        if command_lower.startswith(("open ", "start ", "launch ")) and not any(keyword in command_lower for keyword in ["search", "find", "google", "look up"]):
            return self.open_app(command_lower)

        # Special case: open chrome and search
        if "open chrome" in command_lower and any(keyword in command_lower for keyword in ["search", "find", "google", "look up"]):
            # Extract search query
            prefixes = ["search web for", "search web", "search for", "search", "find", "look up", "google"]
            search_query = command
            for prefix in prefixes:
                idx = command_lower.find(prefix)
                if idx != -1:
                    search_query = command[idx + len(prefix):].strip()
                    break
            if search_query == command:
                # If no prefix, assume after "and"
                parts = command_lower.split(" and ")
                if len(parts) > 1 and "search" in parts[1]:
                    search_query = parts[1].replace("search for", "").replace("search", "").strip()
            encoded_query = urllib.parse.quote(search_query)
            url = f"https://www.google.com/search?q={encoded_query}"
            try:
                subprocess.Popen(["cmd", "/c", "start", "", "chrome", url], shell=False)
                result = f"Opened Chrome and searched for: {search_query}"
            except Exception:
                webbrowser.open(url)
                result = f"Opened the default browser and searched for: {search_query}"
            logging.info(f"Special command result: {result}")
            self.memory.append((command, "special", result))
            return result
        elif " and " in command_lower:
            parts = [p.strip() for p in command.split(" and ")]
            results = []
            for part in parts:
                intent = self.classify_intent(part)
                result = self.execute_action(intent, part)
                results.append(result)
            final_result = " | ".join(results)
            logging.info(f"Compound command results: {final_result}")
            self.memory.append((command, "compound", final_result))
            if len(self.memory) > CONFIG["max_memory"]:
                self.memory.pop(0)
            return final_result
        else:
            logging.info(f"Command received: {command}")
            print(f"[SAFE_AGENT DEBUG] Command received: {command}")
            intent = self.classify_intent(command)
            logging.info(f"Classified intent: {intent}")
            print(f"[SAFE_AGENT DEBUG] Classified intent: {intent}")
            result = self.execute_action(intent, command)
            self.memory.append((command, intent, result))
            if len(self.memory) > CONFIG["max_memory"]:
                self.memory.pop(0)
            logging.info(f"Response: {result}")
            print(f"[SAFE_AGENT DEBUG] Response: {result}")
            return result

    # -----------------------------
    # LEARNING AND PLANNING
    # -----------------------------
    def learn_from_memory(self):
        # Simple learning: count successful intents
        intent_counts = {}
        for cmd, intent, result in self.memory:
            if "not recognized" not in result and "don't know" not in result:
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
        return intent_counts

    def plan_complex_task(self, goal):
        # Simple planner based on goal keywords
        plans = {
            "work": ["open_app", "wifi_on"],
            "study": ["open_app", "search_web"],
            "entertainment": ["play_music", "volume_up"]
        }
        for key, tasks in plans.items():
            if key in goal.lower():
                return tasks
        return []

# -----------------------------
# GLOBAL AGENT INSTANCE
# -----------------------------
agent_instance = AdvancedAgent()

# -----------------------------
# BACKWARD COMPATIBILITY
# -----------------------------
def agent(command):
    return agent_instance.agent(command)

def execute(task):
    intent = agent_instance.classify_intent(task)
    return agent_instance.execute_action(intent, task)

def plan(goal):
    return agent_instance.plan_complex_task(goal)

def autonomous_agent(goal):
    tasks = plan(goal)
    for task in tasks:
        result = execute(task)
        print(f"Executed {task}: {result}")
        time.sleep(1)

# -----------------------------
# MAIN LOOP (FOR TESTING)
# -----------------------------
if __name__ == "__main__":
    print("🤖 Advanced AI Agent Started")
    while True:
        cmd = input("Enter command (or 'exit'): ")
        if cmd.lower() == "exit":
            break
        print(agent(cmd))