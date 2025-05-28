import speech_recognition as sr

recognizer = sr.Recognizer()

def record_audio(timeout=3, phrase_time_limit=50, retries=3):
    for attempt in range(retries):
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Recording started. Speak now...")
                audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                print("Recording complete")
                return audio_data
        except sr.WaitTimeoutError:
            print(f"Listening timed out, retrying... ({attempt + 1}/{retries})")
    return None

def transcribe_audio(audio_data):
    try:
        print("Processing speech...")
        text = recognizer.recognize_google(audio_data)
        return text
    except Exception as e:
        return "Error in transcribing audio"

#testing
if __name__=="__main__":
    audio = record_audio()
    print(transcribe_audio(audio))