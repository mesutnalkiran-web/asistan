import speech_recognition as sr
import asyncio
import edge_tts
import os
import subprocess
import requests
import json

# --- AYARLAR ---
API_KEY = "AIzaSyCp11_b1iYI_UW2xIEAqLcAOyFNjptDseg"
MODEL_NAME = "gemini-2.5-flash"
# Güncel v1beta adresini kullanıyoruz
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

async def speak(text):
    """Yusuf'un sesli yanıt vermesini sağlar."""
    print(f"Yusuf: {text}")
    if os.path.exists("output.mp3"):
        try: os.remove("output.mp3")
        except: pass
    
    communicate = edge_tts.Communicate(text, "tr-TR-AhmetNeural")
    await communicate.save("output.mp3")
    subprocess.run(["mpg123", "-q", "output.mp3"])

def get_gemini_response(prompt):
    """Google Search aracını en yeni kurala göre çalıştırır."""
    headers = {'Content-Type': 'application/json'}
    
    # Hata veren 'google_search_retrieval' yerine 'google_search' yazdık
    payload = {
        "contents": [{
            "parts": [{"text": f"Senin adın Yusuf. Kullanıcın Mesut'u tanıyorsun. Atölyesinde çalışan birisin. Güncel bilgileri internetten kontrol et ve samimi cevap ver: {prompt}"}]
        }],
        "tools": [
            {
                "google_search": {} # YENİ KURAL: Sadece bu yeterli
            }
        ]
    }
    
    try:
        response = requests.post(MODEL_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            # Cevabı ayıklıyoruz
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"Hata: {response.status_code} - {response.text}")
            return "Abi Google kapıyı açmadı, güncel bilgiye ulaşamadım."
    except Exception as e:
        return f"Bağlantı koptu abi: {e}"

def listen_and_process():
    """Sesi kaydeder ve metne çevirir."""
    r = sr.Recognizer()
    audio_file = "input_audio.wav"
    try:
        print("\n[Yusuf]: Dinliyorum Mesut abi...")
        os.system(f"rec -c 1 -r 16000 {audio_file} trim 0 4 > /dev/null 2>&1")
        
        if os.path.exists(audio_file):
            with sr.AudioFile(audio_file) as source:
                audio = r.record(source)
                query = r.recognize_google(audio, language='tr-TR')
                print(f"Duyulan: {query}")
                return query
    except:
        return ""
    return ""

async def main():
    await speak("Selam Mesut abi, Google arama modülünü en yeni sürümüyle güncelledim. Şimdi sormak istediğin her şeyi sorabilirsin.")
    
    while True:
        query = listen_and_process().lower()
        if not query: continue
        
        # YouTube Kontrolü
        if "çal" in query or "youtube" in query:
            song = query.replace("çal", "").replace("youtube", "").strip()
            await speak(f"Tamam abi, {song} hemen açılıyor.")
            subprocess.Popen(["cvlc", "--no-video", f"ytsearch1:{song}"])
            continue

        # Kapatma
        if "kapat" in query or "görüşürüz" in query:
            await speak("Görüşürüz Mesut abi, iyi çalışmalar.")
            break
            
        # Sohbet (Güncel Arama ile)
        answer = get_gemini_response(query)
        await speak(answer)

if __name__ == "__main__":
    os.system("pkill -9 mpg123 > /dev/null 2>&1")
    if os.path.exists("input_audio.wav"): os.remove("input_audio.wav")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSistem kapatıldı.")
