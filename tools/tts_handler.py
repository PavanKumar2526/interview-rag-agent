import subprocess

def speak(text: str):
    """Use Windows PowerShell built-in TTS — no conflicts."""
    print(f"🔊 Speaking: {text}")
    clean_text = text.replace("'", "")
    command = f"powershell -Command \"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = 1; $s.Speak('{clean_text}')\""
    subprocess.run(command, shell=True)

def configure_voice(rate: int = 170, volume: float = 1.0):
    pass

def get_available_voices():
    pass

if __name__ == "__main__":
    speak("Hello! I am your AI Interview Coach. Are you ready to begin your interview?")
    speak("This is a test of the voice system.")