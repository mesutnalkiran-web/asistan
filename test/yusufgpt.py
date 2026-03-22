import speech_recognition as sr
import asyncio
import os
import subprocess
import json
import requests
import smtplib
import base64
import tkinter as tk
import random
import threading
import webbrowser
import time
from datetime import datetime
from email.message import EmailMessage
from openai import OpenAI
import re
import sys

# --- KİMLİK VE AYARLAR ---
PERPLEXITY_API_KEY = "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"
ELEVENLABS_API_KEY = "sk_506308c8ee74b791eb88570227b42311cfb1a59d5c4130fa" # <--- Kendi anahtarını buraya yaz
VOICE_ID = "01p4omegjS2n3rSDCM5u" # <--- Senin istediğin yeni ses ID'si
WAKE_WORD = "yusuf"
MEMORY_FILE = "yusuf_hafiza.json"
GMAIL_ADRESIM = "mesutnalkiran@gmail.com"
GMAIL_SIFREM = "nxru lvhd bquf hinx"

client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

import pyttsx3

engine = pyttsx3.init()

def speak_offline(text):
    def _run():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            if face_app: face_app.set_speaking(True)
            engine.say(text)
            engine.runAndWait()
            if face_app: face_app.set_speaking(False)
        except Exception as e:
            print(f"Offline ses hatası: {e}")

    threading.Thread(target=_run, daemon=True).start()

def check_internet_status():
    try:
        requests.get("https://google.com", timeout=2)
        return True
    except:
        return False

# --- ALARM VE HATIRLATICI DEĞİŞKENLERİ ---
alarm_vakti = None 
alarm_notu = ""

# --- 🎤 ELEVENLABS SES MOTORU (DÜZENLENDİ) ---
async def speak(text):
    global face_app
    print(f"Yusuf: {text}")
    text = text.replace("°C", " derece").replace("%", " yüzde ").replace("-", " tire ")

    if check_internet_status():
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                audio_file = f"yusuf_ses_{random.randint(1,1000)}.mp3"
                with open(audio_file, "wb") as f: f.write(response.content)
                os.system("pkill -9 mpg123 > /dev/null 2>&1")
                if face_app: face_app.set_speaking(True)
                process = subprocess.Popen(["mpg123", "-q", audio_file])
                process.wait()
                if face_app: face_app.set_speaking(False)
                if os.path.exists(audio_file): os.remove(audio_file)
            else:
                print(f"ElevenLabs Hatası: {response.status_code}")
                speak_offline(text)
        except Exception as e:
            print(f"ElevenLabs hatası: {e}")
            speak_offline(text)
    else:
        speak_offline(text)

internet_koptu_uyarisi_verildi = False
def internet_kontrol_dongusu():
    global internet_koptu_uyarisi_verildi
    while True:
        try:
            requests.get("https://google.com", timeout=3)
            internet_koptu_uyarisi_verildi = False
        except:
            if not internet_koptu_uyarisi_verildi:
                asyncio.run(speak("Mesut usta, internet bağlantım koptu."))
                internet_koptu_uyarisi_verildi = True
        time.sleep(60)

def alarm_kontrol_dongusu():
    global alarm_vakti, alarm_notu
    while True:
        if alarm_vakti:
            simdi = datetime.now().strftime("%H:%M")
            if simdi == alarm_vakti:
                os.system("pkill -9 mpv")
                os.system('mpv --no-video "ytdl://ytsearch:sabah neşesi hareketli enstrümantal" &')
                time.sleep(5) 
                asyncio.run(speak(f"Mesut usta vakit geldi! Hatırlatman var: {alarm_notu}"))
                alarm_vakti = None 
        time.sleep(30)

vakitler_cache = {}
def vakitleri_guncelle():
    global vakitler_cache
    try:
        url = "https://api.aladhan.com/v1/timingsByCity?city=Istanbul&country=Turkey&method=13"
        vakitler_cache = requests.get(url).json()['data']['timings']
    except: pass

def vakit_kontrol_dongusu():
    vakitleri_guncelle()
    hatirlatilanlar = []
    while True:
        simdi = datetime.now()
        if simdi.hour == 0 and simdi.minute == 5:
            vakitleri_guncelle(); hatirlatilanlar = []
        if vakitler_cache:
            for isim, saat in vakitler_cache.items():
                if isim in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                    v_vakti = datetime.strptime(f"{simdi.strftime('%Y-%m-%d')} {saat}", "%Y-%m-%d %H:%M")
                    fark = (v_vakti - simdi).total_seconds() / 60
                    if 9.5 <= fark <= 10.5 and isim not in hatirlatilanlar:
                        v_tr = {"Fajr":"İmsak", "Dhuhr":"Öğle", "Asr":"İkindi", "Maghrib":"Akşam", "Isha":"Yatsı"}
                        asyncio.run(speak(f"Mesut, {v_tr[isim]} ezanına on dakika kaldı."))
                        hatirlatilanlar.append(isim)
        time.sleep(60)

class YusufDJFace:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight(), bg='black', highlightthickness=0)
        self.canvas.pack()
        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.is_speaking = False
        self.bars = []
        self.draw_static_elements(); self.create_spectrum_bars(); self.animate()

    def draw_static_elements(self):
        cx, cy = self.sw // 2, self.sh // 2 - 50
        self.canvas.create_arc(cx-260, cy-350, cx+260, cy+170, start=0, extent=180, outline="#00CCFF", width=35, style='arc')
        self.canvas.create_oval(cx-300, cy-110, cx-220, cy+110, fill="#111111", outline="#00CCFF", width=6)
        self.canvas.create_oval(cx+220, cy-110, cx+300, cy+110, fill="#111111", outline="#00CCFF", width=6)
        for x in range(-130, 140, 25):
            for y in range(-200, 160, 25):
                if (x*x)/(130**2) + (y*y)/(200**2) <= 1:
                    self.canvas.create_oval(cx+x-2, cy+y-2, cx+x+2, cy+y+2, fill="#222222", outline="")

    def create_spectrum_bars(self):
        cx, cy = self.sw // 2, self.sh // 2 + 300
        for i in range(30):
            x = cx - 300 + (i * 20)
            bar = self.canvas.create_rectangle(x, cy, x + 15, cy - 10, fill="#00CCFF", outline="")
            self.bars.append(bar)

    def animate(self):
        cy = self.sh // 2 + 300
        for bar in self.bars:
            h = random.randint(40, 200) if self.is_speaking else random.randint(5, 20)
            coords = self.canvas.coords(bar)
            self.canvas.coords(bar, coords[0], cy - h, coords[2], cy)
        self.root.after(80, self.animate)

    def set_speaking(self, status): self.is_speaking = status

face_app = None

def sustur():
    os.system("pkill -9 mpv > /dev/null 2>&1")
    os.system("pkill -9 mpg123 > /dev/null 2>&1")

def take_photo():
    p = "snap.jpg"
    os.system(f"fswebcam -r 1280x720 -S 30 --no-banner {p} > /dev/null 2>&1")
    return p

def get_vision_analysis(img):
    try:
        with open(img, "rb") as f: b64 = base64.b64encode(f.read()).decode('utf-8')
        resp = client.chat.completions.create(
            model="sonar-reasoning-pro",
            messages=[{"role": "user", "content": [{"type": "text", "text": "Bu nedir? Kısa ve öz söyle."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
        )
        return resp.choices[0].message.content
    except: return "Analiz edilemedi."

def send_mail(subj, cont, img=""):
    msg = EmailMessage()
    msg['Subject'], msg['From'], msg['To'] = subj, GMAIL_ADRESIM, GMAIL_ADRESIM
    msg.set_content(cont)
    if img != "" and os.path.exists(img):
        with open(img, 'rb') as f: msg.add_attachment(f.read(), maintype='image', subtype='jpeg', filename="analiz.jpg")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(GMAIL_ADRESIM, GMAIL_SIFREM); s.send_message(msg)
        return True
    except: return False

def listen_and_process(duration=4):
    r = sr.Recognizer()
    audio_file = "input_audio.wav"
    try:
        os.system(f"rec -c 1 -r 16000 {audio_file} trim 0 {duration} > /dev/null 2>&1")
        with sr.AudioFile(audio_file) as source:
            try:
                return r.recognize_google(r.record(source), language='tr-TR').lower()
            except:
                return ""
    except:
        return ""

def check_internet():
    try:
        requests.get("https://google.com", timeout=2)
        return "İnternet bağlantım gayet iyi Mesut usta."
    except: return "Şu an internete bağlanamıyorum."

batarya_uyarisi_verildi = False
def batarya_kontrol_dongusu():
    global batarya_uyarisi_verildi
    while True:
        try:
            bat_path = "/sys/class/power_supply/BAT0"
            if not os.path.exists(bat_path): bat_path = "/sys/class/power_supply/BAT1"
            if os.path.exists(bat_path):
                with open(f"{bat_path}/capacity", "r") as f: cap = int(f.read().strip())
                with open(f"{bat_path}/status", "r") as f: stat = f.read().strip()
                if cap <= 20 and stat == "Discharging" and not batarya_uyarisi_verildi:
                    asyncio.run(speak(f"Efendim, batarya % {cap}. Şarja takınız."))
                    batarya_uyarisi_verildi = True
                elif stat == "Charging":
                    batarya_uyarisi_verildi = False
        except:
            pass
        time.sleep(300)


internet_koptu_uyarisi_verildi = False
def internet_kontrol_dongusu():
    global internet_koptu_uyarisi_verildi
    while True:
        if check_internet_status():
            internet_koptu_uyarisi_verildi = False
        else:
            if not internet_koptu_uyarisi_verildi:
                asyncio.run(speak("Efendim, internet bağlantısı yok."))
                internet_koptu_uyarisi_verildi = True
        time.sleep(60)

# --- ANA MANTIK ---
async def yusuf_logic():
    global face_app, alarm_vakti, alarm_notu
    await speak("Yusuf otonom sistemleri devrede. Gözüm hem atölyede hem kendi üzerimde usta.")
    
    while True:
        query = listen_and_process(duration=3)
        if WAKE_WORD in query:
            if any(w in query for w in ["sus", "dur", "kes"]):
                sustur(); continue
                
            await speak("Buyurun.")
            cmd = listen_and_process(duration=5)
            if not cmd: continue

            if any(w in cmd for w in ["kur", "hatırlat", "alarm"]):
                saat_bul = re.findall(r'(\d{1,2})[.:\s](\d{2})', cmd)
                if saat_bul:
                    h, m = saat_bul[0]
                    alarm_vakti = f"{int(h):02d}:{int(m):02d}"
                    alarm_notu = cmd.replace(h, "").replace(m, "").strip()
                    await speak(f"Tamamdır Mesut usta, saat {alarm_vakti} için alarmı kurdum."); continue

            if any(w in cmd for w in ["şarj", "batarya", "internet"]):
                if "internet" in cmd: await speak(check_internet())
                else: await speak(check_battery())
                continue

            if any(w in cmd for w in ["analiz", "incele", "bak"]):
                await speak("Hemen bakıyorum.")
                p = take_photo(); desc = get_vision_analysis(p)
                await speak(f"Gördüğüm şey: {desc}"); continue

            if any(w in cmd for w in ["mail", "e-posta"]):
                await speak("Mail gönderiyorum.")
                p = take_photo(); desc = get_vision_analysis(p)
                send_mail("Yusuf Analiz Raporu", desc, p)
                await speak("Gördüm ve gönderdim."); continue

            if any(w in cmd for w in ["çal", "aç"]):
                song = cmd.replace("çal", "").replace("aç", "").strip()
                os.system("pkill -9 mpv > /dev/null 2>&1")
                await speak("Açıyorum."); os.system(f'mpv --no-video "ytdl://ytsearch:{song}" &'); continue

            if any(w in cmd for w in ["namaz", "vakit", "ezan"]):
                if vakitler_cache:
                    v = vakitler_cache
                    await speak(f"Öğle {v['Dhuhr']}, İkindi {v['Asr']}, Akşam {v['Maghrib']}."); continue

             # --- GENEL SORU VE AKILLI ROTA (SADECE ONAY VERİR, DETAYI MAİLE ATAR) ---
            try:
                # Yusuf'a sadece kısa bir onay vermesini, detaylı linki hazırlamasını söylüyoruz
                sys_msg = "Sen Yusufsun. Çok kısa konuş. Yol tarifi istenirse sadece 'Hemen hazırlayıp mailine gönderdim usta' de ve Google Maps linkini ekle. Asla adresi sesli okuma."
                
                response = client.chat.completions.create(
                    model="sonar",
                    messages=[
                        {"role": "system", "content": sys_msg},
                        {"role": "user", "content": cmd}
                    ]
                )
                cevap_tam = response.choices[0].message.content
                # Kaynak numaralarını [1] temizle
                cevap_tam = re.sub(r"\[\d+\]", "", cevap_tam)
                
                # --- SESLİ OKUMA TEMİZLİĞİ ---
                # Linkleri, tire işaretlerini ve parantez içlerini sesli okumadan atıyoruz
                sesli_cevap = re.sub(r'https?://\S+', '', cevap_tam) # Linkleri sil
                sesli_cevap = sesli_cevap.replace("-", " ").replace("tire", "") # Tireleri sil
                sesli_cevap = re.sub(r'\(.*?\)', '', sesli_cevap) # Parantez içlerini sil
                sesli_cevap = sesli_cevap.strip()
                
                # Yusuf sadece kısa onayını verir
                if len(sesli_cevap) > 100: # Eğer cevap hala çok uzunsa ilk cümleyi al
                    sesli_cevap = sesli_cevap.split('.')[0] + "."
                
                await speak(sesli_cevap)
                
                # --- MAİL GÖNDERİMİ (TÜM DETAY VE LİNK BURADA) ---
                if "http" in cevap_tam:
                    send_mail("Yusuf Navigasyon ve Rota Detayı", cevap_tam)
                    # Eğer Yusuf onayda mailden bahsetmediyse ekle
                    if "mail" not in sesli_cevap.lower():
                        await speak("Detaylı rotayı mailine bıraktım usta.")
                        
            except Exception as e:
                print(f"Hata: {e}")
                await speak("Bağlantıda bir aksaklık oldu usta.")

if __name__ == "__main__":
    vakitleri_guncelle()
    face_app = YusufDJFace()
    threading.Thread(target=lambda: asyncio.run(yusuf_logic()), daemon=True).start()
    threading.Thread(target=vakit_kontrol_dongusu, daemon=True).start()
    threading.Thread(target=alarm_kontrol_dongusu, daemon=True).start()
    threading.Thread(target=internet_kontrol_dongusu, daemon=True).start()
    threading.Thread(target=batarya_kontrol_dongusu, daemon=True).start()
    face_app.root.mainloop()
