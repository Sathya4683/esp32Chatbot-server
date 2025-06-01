import requests
import sounddevice as sd
import numpy as np
import tempfile
import librosa

# 1. Replace this with your actual .wav file or simulate
audio_file_path = "test_pcm.wav"  # simulate what the mic recorded

# 2. Send POST request
with open(audio_file_path, "rb") as f:
    files = {"audio": ("input.wav", f, "audio/wav")}
    try:
        response = requests.post("http://localhost:8000/convert", files=files)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        exit()

# 3. Play response audio using sounddevice
if response.ok:
    print("Playing response audio...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(response.content)
        tmp_file.flush()

        # Decode mp3 to NumPy array for playback
        y, sr = librosa.load(tmp_file.name, sr=None)

        sd.play(y, sr)
        sd.wait()
