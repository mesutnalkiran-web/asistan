import speech_recognition as sr
import asyncio
import edge_tts
import os
import random
import threading
import time
import tkinter as tk
import re
from datetime import datetime
from openai import OpenAI

# MODÜLLERİ BAĞLIYORUZ (yetenekler klasöründen)
try:
    from yetenekler import ezan, medya, vizyon, otonom, zeka
except ImportError as e:
    print(f"Hata: Modüller bulunamadı! 'yetenekler' klasörünü kontrol et. Detay: {e}")

# --- KİMLİK VE AYARLAR ---
PERPLEXITY_API_KEY = "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"
WAKE_WORD = "yusuf"
GMAIL_USER = "mesutnalkiran@gmail.com"
GMAIL_PASS = "nxru lvhd bquf hinx" # Uygulama şifren

client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

# Küresel Değişkenler
vakitler_cache = {}
alarm_vakti = None
alarm_notu = ""

# --- GÖRSEL ARAYÜZ (DJ FACE) ---
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

# --- SES VE MİKROFON ---
async def speak(text):
    global face_app
    text = zeka.metin_temizle(text)
    print(f"Yusuf: {text}")
    try:
        audio_file = f"output_{random.randint(1,1000)}.mp3"
        communicate = edge_tts.Communicate(text, "tr-TR-AhmetNeural", rate="+15%", pitch="-5Hz")
        await communicate.save(audio_file)
        if face_app: face_app.set_speaking(True)
        os.system(f"mpg123 -q {audio_file}")
        if face_app: face_app.set_speaking(False)
        if os.path.exists(audio_file): os.remove(audio_file)
    except:
        if face_app: face_app.set_speaking(False)

def listen(duration=4):
    r = sr.Recognizer()
    try:
        os.system(f"rec -c 1 -r 16000 input_audio.wav trim 0 {duration} > /dev/null 2>&1")
        with sr.AudioFile("input_audio.wav") as source:
            return r.recognize_google(r.record(source), language='tr-TR').lower()
    except: return ""

# --- OTONOM DÖNGÜLER ---
def takip_dongusu():
    global vakitler_cache, alarm_vakti, alarm_notu
    batarya_uyari_verildi = False
    
    while True:
        simdi_saat = datetime.now().strftime("%H:%M")
        
        # 1. ALARM TETİKLEYİCİ
        if alarm_vakti and simdi_saat == alarm_vakti:
            medya.her_seyi_sustur()
            os.system('mpv --no-video "ytdl://ytsearch:sabah neşesi hareketli enstrümantal" &')
            time.sleep(2)
            asyncio.run(speak(f"Mesut vakit geldi! Notun: {alarm_notu}"))
            alarm_vakti = None # Çaldıktan sonra iptal et

        # 2. Ezan Kontrol
        v = ezan.vakit_kontrol(vakitler_cache)
        if v:
            asyncio.run(speak(f"Mesut, {v} ezanına on dakika kaldı."))
        
        # 3. Batarya Kontrol
        cap, stat = otonom.batarya_durumu()
        if cap and cap <= 20 and stat == "Discharging" and not batarya_uyari_verildi:
            asyncio.run(speak(f"Mesut usta, şarjım yüzde {cap}. Beni fişe takar mısın?"))
            batarya_uyari_verildi = True
        elif stat == "Charging":
            batarya_uyari_verildi = False
            
        time.sleep(30)

# --- ANA MANTIK MERKEZİ ---
async def yusuf_logic():
    await speak("Yusuf modüler sistem ve alarm desteğiyle hazır Mesut. Kulaklarım sende.")
    
    while True:
        query = listen(3)
        if WAKE_WORD in query:
            if any(w in query for w in ["sus", "dur", "kes", "kapat"]):
                medya.her_seyi_sustur(); continue
            
            await speak("Buyurun.")
            cmd = listen(5)
            if not cmd: continue

            # TEYİT SİSTEMİ
            await speak(f"Mesut, {cmd} dedin, doğru mu?")
            onay = listen(3)
            if not any(w in onay for w in ["evet", "doğru", "yap", "aynen", "onay"]):
                await speak("İptal ettim."); continue

            # --- YETENEK DAĞITIMI ---
            
            # Alarm Kurma
            if any(w in cmd for w in ["kur", "hatırlat", "uyandır", "saat", "alarm"]):
                saat_bul = re.findall(r'(\d{1,2})[.:\s](\d{2})', cmd)
                if not saat_bul:
                    tek_saat = re.findall(r'\b(\d{1,2})\b', cmd)
                    if tek_saat: saat_bul = [(tek_saat[0], "00")]
                
                if saat_bul:
                    global alarm_vakti, alarm_notu
                    h, m = saat_bul[0]
                    alarm_vakti = f"{int(h):02d}:{int(m):02d}"
                    alarm_notu = cmd.replace(h, "").replace(m, "").replace("saat", "").replace("kur", "").strip()
                    await speak(f"Tamamdır Mesut, saat {alarm_vakti} için alarmı kurdum.")
                else:
                    await speak("Saati tam anlayamadım Mesut.")

            # Müzik ve Diğerleri
            elif any(w in cmd for w in ["çal", "aç"]):
                song = cmd.replace("aç", "").replace("çal", "").strip()
                medya.muzik_cal(song)
                await speak("Açıyorum.")
            
            elif any(w in cmd for w in ["analiz", "incele", "bak"]):
                await speak("Hemen bakıyorum.")
                p = vizyon.foto_cek()
                desc = vizyon.analiz_et(client, p)
                await speak(f"Gördüğüm şey: {desc}")
            
            elif any(w in cmd for w in ["mail", "e-posta"]):
                await speak("Gördüğümü mail atıyorum.")
                p = vizyon.foto_cek()
                desc = vizyon.analiz_et(client, p)
                vizyon.mail_gonder("Yusuf Analiz Raporu", desc, p, GMAIL_USER, GMAIL_PASS)
                await speak("Gönderdim usta.")
            
            else:
                uzun = any(w in cmd for w in ["uzun", "detay", "ayrıntı"])
                cevap = zeka.cevap_uret(client, cmd, uzun)
                await speak(cevap)
                
                # Yol tarifi linki varsa mail gönder
                if "http" in cevap or "maps" in cevap:
                    vizyon.mail_gonder("Yol Tarifi", cevap, "", GMAIL_USER, GMAIL_PASS)
                    await speak("Harita linkini mailine de gönderdim usta.")

# --- PROGRAMI BAŞLAT ---
if __name__ == "__main__":
    vakitler_cache = ezan.vakitleri_guncelle()
    face_app = YusufDJFace()
    
    threading.Thread(target=takip_dongusu, daemon=True).start()
    threading.Thread(target=lambda: asyncio.run(yusuf_logic()), daemon=True).start()
    
    face_app.root.mainloop()
