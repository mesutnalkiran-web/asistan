import face_recognition
import os
import cv2
import pickle

DB_FILE = "yuzler.pkl"

def veritabani_yukle():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def veritabani_kaydet(db):
    with open(DB_FILE, "wb") as f:
        pickle.dump(db, f)

def fotograf_cek():
    path = "kisi.jpg"
    os.system(f"fswebcam -r 640x480 --no-banner {path} > /dev/null 2>&1")
    return path

def kisi_tani():
    db = veritabani_yukle()

    foto = fotograf_cek()
    image = face_recognition.load_image_file(foto)

    enc = face_recognition.face_encodings(image)

    if len(enc) == 0:
        return None

    enc = enc[0]

    for isim, veri in db.items():
        match = face_recognition.compare_faces([veri], enc)
        if match[0]:
            return isim

    return None


def kisi_kaydet(isim):

    db = veritabani_yukle()

    image = face_recognition.load_image_file("kisi.jpg")
    enc = face_recognition.face_encodings(image)

    if len(enc) == 0:
        return False

    db[isim] = enc[0]

    veritabani_kaydet(db)

    return True
