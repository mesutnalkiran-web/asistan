import cv2
import time

cap = cv2.VideoCapture(0)

last_frame = None
last_check = 0

def hareket_var_mi():

    global last_frame, last_check

    if time.time() - last_check < 2:
        return False

    last_check = time.time()

    ret, frame = cap.read()
    if not ret:
        return False

    frame = cv2.resize(frame, (320,240))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if last_frame is None:
        last_frame = gray
        return False

    diff = cv2.absdiff(last_frame, gray)
    last_frame = gray

    hareket = diff.sum()

    if hareket > 500000:
        return True

    return False
