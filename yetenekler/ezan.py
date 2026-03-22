import requests
import time
from datetime import datetime

vakitler_cache = {}

def vakitleri_guncelle():
    global vakitler_cache
    try:
        url = "https://api.aladhan.com/v1/timingsByCity?city=Istanbul&country=Turkey&method=13"
        resp = requests.get(url).json()
        vakitler_cache = resp['data']['timings']
        return vakitler_cache
    except: return None

def vakit_kontrol():
    v = vakitleri_guncelle()
    if not v: return None
    
    simdi = datetime.now()
    bugun = simdi.strftime("%Y-%m-%d")
    
    # Sadece ana vakitleri kontrol et
    v_tr = {"Fajr":"İmsak", "Dhuhr":"Öğle", "Asr":"İkindi", "Maghrib":"Akşam", "Isha":"Yatsı"}
    
    for isim, saat in v.items():
        if isim in v_tr:
            v_vakti = datetime.strptime(f"{bugun} {saat}", "%Y-%m-%d %H:%M")
            fark = (v_vakti - simdi).total_seconds() / 60
            if 9.5 <= fark <= 10.5:
                return v_tr[isim]
    return None
