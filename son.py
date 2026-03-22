import speech_recognition as sr
import asyncio
import edge_tts
import os
import subprocess
import json
import requests
import smtplib
import base64
import tkinter as tk
import random
import threading
import time
import psutil
from datetime import datetime
from email.message import EmailMessage
from openai import OpenAI
import re

# --- KİMLİK VE AYARLAR ---
PERPLEXITY_API_KEY = "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"
WAKE_WORD = "yusuf"
GMAIL_USER = "mesutnalkiran@gmail.com"
GMAIL_PASS = "nxru lvhd bquf hinx"

client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

chat_history = [] 
vakitler_cache = {}
alarm_vakti = None
alarm_notu = ""

# --- HARİTA LİNKİ OLUŞTURUCU ---
def harita_linki_yap(metin):
    hedef = metin.replace(" ", "+")
    return f"https://www.google.com/maps/search/{hedef}"

def metin_temizle(metin):
    metin = metin.replace("°C", " derece").replace("°", " derece")
    metin = metin.replace("%", " yüzde ").replace("-", " tire ")
    metin = re.sub(r'https?://\S+', '', metin)
    metin = re.sub(r'[^\w\s.,?!:;çğıöşüÇĞİÖŞÜ]', '', metin) 
    return metin.strip()

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

    def set_speaking(self, status):
        self.is_speaking = status

face_app = None

async def speak(text):
    global face_app
    temiz_metin = metin_temizle(text)
    print(f"Yusuf: {temiz_metin}")
    try:
        audio_file = f"output_{random.randint(1,1000)}.mp3"
        communicate = edge_tts.Communicate(temiz_metin, "tr-TR-AhmetNeural", rate="+15%", pitch="-5Hz")
        await communicate.save(audio_file)
        if face_app: face_app.set_speaking(True)
        process = subprocess.Popen(["mpg123", "-q", audio_file])
        process.wait()
        if face_app: face_app.set_speaking(False)
        if os.path.exists(audio_file): os.remove(audio_file)
    except:
        if face_app: face_app.set_speaking(False)

def listen(duration=5):
    r = sr.Recognizer()
    try:
        os.system(f"rec -c 1 -r 16000 input_audio.wav trim 0 {duration} > /dev/null 2>&1")
        with sr.AudioFile("input_audio.wav") as source:
            return r.recognize_google(r.record(source), language='tr-TR').lower()
    except: return ""

def send_mail(subj, cont, img=""):
    msg = EmailMessage()
    msg['Subject'], msg['From'], msg['To'] = subj, GMAIL_USER, GMAIL_USER
    msg.set_content(cont)
    if img != "" and os.path.exists(img):
        with open(img, 'rb') as f: msg.add_attachment(f.read(), maintype='image', subtype='jpeg', filename="foto.jpg")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(GMAIL_USER, GMAIL_PASS); s.send_message(msg)
    except: pass

def takip_dongusu():
    global vakitler_cache, alarm_vakti, alarm_notu
    batarya_uyari_verildi = False
    while True:
        simdi = datetime.now()
        simdi_str = simdi.strftime("%H:%M")
        battery = psutil.sensors_battery()
        if battery and battery.percent <= 20 and not battery.power_plugged and not batarya_uyari_verildi:
            asyncio.run(speak("Efendim, şarjım yüzde yirmi. Beni fişe takar mısın?"))
            batarya_uyari_verildi = True
        elif battery and battery.power_plugged: batarya_uyari_verildi = False

        if alarm_vakti and simdi_str == alarm_vakti:
            os.system("pkill -9 mpv")
            os.system('mpv --no-video "ytdl://ytsearch:hareketli enstrümantal" &')
            asyncio.run(speak(f"Efendim vakit geldi. Notun: {alarm_notu}"))
            alarm_vakti = None
            
        if vakitler_cache:
            for isim, saat in vakitler_cache.items():
                if isim in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                    try:
                        v_vakti = datetime.strptime(f"{simdi.strftime('%Y-%m-%d')} {saat}", "%Y-%m-%d %H:%M")
                        if 9.5 <= (v_vakti - simdi).total_seconds() / 60 <= 10.5:
                            v_tr = {"Fajr":"İmsak", "Dhuhr":"Öğle", "Asr":"İkindi", "Maghrib":"Akşam", "Isha":"Yatsı"}
                            asyncio.run(speak(f"Efendim, {v_tr[isim]} ezanına on dakika kaldı."))
                    except: pass
        time.sleep(40)

async def yusuf_logic():
    global chat_history, alarm_vakti, alarm_notu
    await speak("Sistemler aktif. Dinliyorum.")
    while True:
        query = listen(5)
        if WAKE_WORD in query:
            query_sozcukler = query.split()
            if any(w in query_sozcukler for w in ["sus", "dur", "kes", "kapat"]):
                os.system("pkill -9 mpv; pkill -9 mpg123"); continue

            cmd = query.replace(WAKE_WORD, "").strip()
            if not cmd:
                await speak("Efendim?")
                cmd = listen(5)
                if not cmd: continue

            await speak(f"Efendim, {cmd} dediniz, doğru mu?")
            onay = listen(4)
            if not any(w in onay for w in ["evet", "doğru", "yap", "aynen", "tamam", "olur"]):
                await speak("İptal ettim."); continue

            # --- ⏰ ALARM KURMA (HATANIN DÜZELDİĞİ YER) ---
            saat_bul = re.findall(r'(\d{1,2})[\s.:]?(\d{2})', cmd)
            if any(w in cmd for w in ["alarm", "kur", "hatırlat"]) and saat_bul:
                h, m = saat_bul[0]
                alarm_vakti = f"{int(h):02d}:{int(m):02d}"
                alarm_notu = cmd.replace("kur", "").replace("alarm", "").strip()
                await speak(f"Tamamdır efendim, saat {alarm_vakti} için alarmı kurdum.")
                continue

            # --- 👁️ ANALİZ VE MAİL ---
            if any(w in cmd for w in ["analiz", "incele", "bak", "gör", "mail"]):
                await speak("Hemen bakıyorum.")
                p = "snap.jpg"
                if os.path.exists(p): os.remove(p)
                os.system(f"fswebcam -r 1280x720 -S 15 --no-banner {p} > /dev/null 2>&1")
                time.sleep(1.5)
                if os.path.exists(p):
                    try:
                        with open(p, "rb") as f: b64 = base64.b64encode(f.read()).decode('utf-8')
                        if "mail" in cmd:
                            resp = client.chat.completions.create(model="sonar", messages=[{"role": "user", "content": [{"type": "text", "text": "Bu fotoğrafı teknik rapor olarak analiz et."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}] )
                            send_mail("Yusuf Analiz Raporu", resp.choices[0].message.content, p)
                            await speak("Efendim, analiz edip maili gönderdim.")
                        else:
                            resp = client.chat.completions.create(model="sonar", messages=[{"role": "user", "content": [{"type": "text", "text": "Gördüğünü sadece 1-2 kelimeyle söyle."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}] )
                            await speak(f"Gördüğüm: {resp.choices[0].message.content}")
                    except: 
                        await speak("Bağlantı koptu.")
                else: await speak("Kamerayı göremedim.")

            elif any(w in cmd for w in ["şarj", "batarya", "pil"]):
                battery = psutil.sensors_battery()
                await speak(f"Efendim şarjım yüzde {battery.percent}.")

            elif any(w in cmd for w in ["çal", "aç"]):
                song = cmd.replace("aç", "").replace("çal", "").strip()
                os.system(f'mpv --no-video "ytdl://ytsearch:{song}" &')
                await speak("Açıyorum.")

            else:
                try:
                    sys_prompt = "Sen Yusufsun. Efendim diye hitap et. 1 cümleyi geçme. Asla vclock gibi sitelerden bahsetme."
                    resp = client.chat.completions.create(model="sonar", messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": cmd}])
                    cevap = re.sub(r"\[\d+\]", "", resp.choices[0].message.content)
                    await speak(cevap)

                    if any(w in cmd.lower() for w in ["yol", "tarif", "git", "nerede"]):
                        link = harita_linki_yap(cmd)
                        send_mail("Yusuf Yol Tarifi", f"Tarif: {cevap}\n\nHarita: {link}")
                        await speak("Harita linkini mailinize attım.")
                except: await speak("İnternet sorunu efendim.")

if __name__ == "__main__":
    try:
        url = "https://api.aladhan.com/v1/timingsByCity?city=Istanbul&country=Turkey&method=13"
        vakitler_cache = requests.get(url).json()['data']['timings']
    except: pass
    face_app = YusufDJFace()
    threading.Thread(target=takip_dongusu, daemon=True).start()
    threading.Thread(target=lambda: asyncio.run(yusuf_logic()), daemon=True).start()
    face_app.root.mainloop()
