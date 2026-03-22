import os
import base64
import smtplib
from email.message import EmailMessage

def foto_cek():
    p = "snap.jpg"
    os.system(f"fswebcam -r 1280x720 -S 30 --no-banner {p} > /dev/null 2>&1")
    return p

def analiz_et(client, img_path):
    try:
        with open(img_path, "rb") as f: 
            b64 = base64.b64encode(f.read()).decode('utf-8')
        resp = client.chat.completions.create(
            model="sonar-reasoning-pro",
            messages=[{"role": "user", "content": [{"type": "text", "text": "Bu nedir? Kısa ve öz söyle."}, 
                      {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
        )
        return resp.choices[0].message.content
    except: return "Analiz edilemedi."

def mail_gonder(subj, cont, img, GMAIL_USER, GMAIL_PASS):
    msg = EmailMessage()
    msg['Subject'], msg['From'], msg['To'] = subj, GMAIL_USER, GMAIL_USER
    msg.set_content(cont)
    if os.path.exists(img):
        with open(img, 'rb') as f: 
            msg.add_attachment(f.read(), maintype='image', subtype='jpeg', filename="analiz.jpg")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(GMAIL_USER, GMAIL_PASS)
            s.send_message(msg)
        return True
    except: return False
