# yuzmodulu.py
import cv2
import face_recognition
import time
import threading

class YuzModulu:
    def __init__(self, kamera_no=0):
        print("Yüz tanıma modülü başlatıldı...")
        self.video_capture = cv2.VideoCapture(kamera_no)
        self.known_face_encodings = []
        self.known_face_names = []
        self.running = True

    def yuz_tespit(self):
        while self.running:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Kamera açılamıyor!")
                time.sleep(1)
                continue

            rgb_frame = frame[:, :, ::-1]  # BGR -> RGB
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Bilinmeyen"
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    print(f"Tanındı: {name}")
                else:
                    print("Tanımadım, tanışalım mı?")

            time.sleep(1)

    def baslat(self):
        t = threading.Thread(target=self.yuz_tespit, daemon=True)
        t.start()

    def durdur(self):
        self.running = False
        self.video_capture.release()
        print("Yüz tanıma durduruldu.")
