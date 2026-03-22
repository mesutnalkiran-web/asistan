import re

def metin_temizle(metin):
    # Hava durumu ve sembol temizliği
    metin = metin.replace("°C", " derece").replace("°", " derece")
    metin = metin.replace("%", " yüzde ").replace("-", " eksi ")
    metin = re.sub(r'https?://\S+', '', metin)
    metin = re.sub(r'[^\w\s.,?!:;çğıöşüÇĞİÖŞÜ]', '', metin) 
    return metin.strip()

def cevap_uret(client, cmd, uzun_cevap=False):
    if uzun_cevap:
        talimat = "Sen Yusufsun. Detaylı ve uzun uzun cevap ver. Emoji/sembol kullanma. Sayıları yazıyla yaz."
    else:
        talimat = "Sen Yusufsun. İki cümleyi geçme. Kısa ve öz ol. Emoji/sembol kullanma. Sayıları yazıyla yaz."
    
    try:
        resp = client.chat.completions.create(
            model="sonar",
            messages=[{"role": "system", "content": talimat}, {"role": "user", "content": cmd}]
        )
        ham = re.sub(r"\[\d+\]", "", resp.choices[0].message.content)
        return ham
    except: return "Bağlantı sorunu usta."
