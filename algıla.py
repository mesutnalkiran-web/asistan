import cv2
import face_recognition
import time

video = cv2.VideoCapture(0)

son_konusma = 0

while True:

    ret, frame = video.read()
    rgb = frame[:, :, ::-1]

    faces = face_recognition.face_locations(rgb)

    if len(faces) > 0:

        simdi = time.time()

        if simdi - son_konusma > 10:

            print("Merhaba hoş geldiniz")
            son_konusma = simdi

    cv2.imshow("kamera", frame)

    if cv2.waitKey(1) == 27:
        break
