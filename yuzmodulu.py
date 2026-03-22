import cv2
import face_recognition
import pickle
import os
import time

faces_dir = "faces"

video = cv2.VideoCapture(0)

last_greet = 0
greet_delay = 30

known_faces = []
known_names = []

def load_faces():

    global known_faces, known_names

    for file in os.listdir(faces_dir):

        if file.endswith(".pkl"):

            with open(os.path.join(faces_dir,file),"rb") as f:

                data = pickle.load(f)

                known_faces.append(data["encoding"])
                known_names.append(data["name"])

load_faces()

def save_face(name,encoding):

    data = {
        "name":name,
        "encoding":encoding
    }

    with open(f"{faces_dir}/{name}.pkl","wb") as f:
        pickle.dump(data,f)

    known_faces.append(encoding)
    known_names.append(name)

def yuz_tara():

    global last_greet

    ret, frame = video.read()

    frame = cv2.resize(frame,(640,360))

    rgb = frame[:,:,::-1]

    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb,locations)

    for face_encoding in encodings:

        matches = face_recognition.compare_faces(known_faces,face_encoding)

        name = "unknown"

        if True in matches:

            index = matches.index(True)
            name = known_names[index]

        now = time.time()

        if now-last_greet > greet_delay:

            last_greet = now

            return name,face_encoding

    return None,None
