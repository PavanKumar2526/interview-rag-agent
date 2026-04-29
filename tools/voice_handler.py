import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import time

# Load whisper model once (tiny = fast, low RAM)
print("Loading Whisper model...")
model = whisper.load_model("tiny")
print("Whisper ready!")

def record_audio(duration: int = 10, sample_rate: int = 16000) -> str:
    """Record audio from microphone and save to temp file."""
    print(f"\n🎙️ Get ready! Recording starts in...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print(f"  🔴 SPEAK NOW! ({duration} seconds)")
    
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.float32
    )
    sd.wait()
    print("✅ Recording complete!")
    
    # Save to temp file
    temp_file = tempfile.mktemp(suffix=".wav")
    sf.write(temp_file, audio, sample_rate)
    return temp_file

def transcribe_audio(audio_path: str) -> str:
    """Convert audio file to text using Whisper."""
    print("🔄 Transcribing...")
    result = model.transcribe(audio_path, language="en")
    text = result["text"].strip()
    
    # Cleanup temp file
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    return text

def listen_and_transcribe(duration: int = 10) -> str:
    """Full pipeline: record mic → return text."""
    audio_path = record_audio(duration)
    return transcribe_audio(audio_path)

if __name__ == "__main__":
    print("🎤 Voice Handler Test")
    print("You will have 8 seconds to speak.\n")
    text = listen_and_transcribe(duration=8)
    if text:
        print(f"\n✅ Final transcript: {text}")
    else:
        print("\n⚠️ No speech detected. Check your microphone volume in Windows settings.")