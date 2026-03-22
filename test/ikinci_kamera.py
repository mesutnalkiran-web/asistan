# ikinci_kamera.py
import cv2
def baslat():
    cap = cv2.VideoCapture(1)  # ikinci kamera
    if not cap.isOpened():
        print("İkinci kamera açılamıyor!")
        return
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow("İkinci Kamera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
