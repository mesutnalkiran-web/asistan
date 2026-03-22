import face_recognition
import cv2
import pickle
import os

DB = "faces.db"

def load_faces():
    if os.path.exists(DB):
        with open(DB,"rb") as f:
            return pickle.load(f)
    return {}

def save_faces(data):
    with open(DB,"wb") as f:
        pickle.dump(data,f)

known = load_faces()

def yuz_tara():

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None,None

    rgb = frame[:,:,::-1]
    locs = face_recognition.face_locations(rgb)

    if not locs:
        return None,None

    encs = face_recognition.face_encodings(rgb,locs)

    for enc in encs:
        for name,data in known.items():

            if face_recognition.compare_faces([data],enc)[0]:
                return name,enc

    return "unknown",encs[0]

def save_face(name,enc):

    known[name]=enc
    save_faces(known)
