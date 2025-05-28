import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
def speak(text):
    engine.say(text)
    engine.runAndWait()

#testing

if __name__ =="__main__":
    speak("hello how are you doing?")