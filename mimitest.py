import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import webbrowser
import random
import os
from datetime import datetime

r = sr.Recognizer()

def record(ask=False):
    with sr.Microphone() as source:
        if ask:
            speak(ask)
        audio = r.listen(source)
        voice = ''
        try:
            voice = r.recognize_google(audio, language='tr-TR')
        except sr.UnknownValueError:
            speak('anlayamadım')
        except sr.RequestError:
            speak('sistem çalışmıyor')
        return voice

def speak(string):
    tts = gTTS(string, lang='tr')
    rand = random.randint(1, 10000)
    file = 'audio-' + str(rand) + '.mp3'
    tts.save(file)
    playsound(file)
    os.remove(file)

def response(voice):
    if 'nasılsın' in voice:
        speak('iyiyim siz nasılsınız')
    if 'saat kaç' in voice:
        speak(datetime.now().strftime('%H:%M:%S'))
    if 'arama yap' in voice:
        search = record("ne arama yapmak istiyorsun")
        webbrowser.open("https://google.com/search?q=" + search)

speak('Nasıl yardımcı olabilirim')

while True:
    voice = record()
    print(voice)
    response(voice)
