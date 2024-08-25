import cv2
import pickle
import cvzone
import numpy as np
from collections import deque
import pyrebase
import threading
import time

# Initialize Firebase
firebaseConfig = {
  'apiKey': "AIzaSyCfryOB57bf-oSSiZ3NUzTKLA7cvsuslJU",
  'authDomain': "parkease808802.firebaseapp.com",
  'databaseURL': 'https://parkease808802-default-rtdb.firebaseio.com',
  'projectId': "parkease808802",
  'storageBucket': "parkease808802.appspot.com",
  'messagingSenderId': "438355709019",
  'appId': "1:438355709019:web:099fb339bf16a05e21c37e",
  'measurementId': "G-99NHCESW0E"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# Video feed
cap = cv2.VideoCapture('vid7.mp4')
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)
width, height = 75, 135

# Initialize deque to store pixel counts for smoothing
pixel_counts = [deque(maxlen=5) for _ in posList]

# Firebase update variables
totalSpaces = len(posList)
lastFirebaseUpdate = time.time()

def checkParkingSpace(imgPro, img):
    spaceCounter = 0
    for i, pos in enumerate(posList):
        x, y = pos
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 0), 2)
        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)
        # Add current count to deque and calculate moving average
        pixel_counts[i].append(count)
        avg_count = np.mean(pixel_counts[i])
        cvzone.putTextRect(img, str(int(avg_count)), (x, y + height - 5), scale=1, thickness=1, offset=0)
        if avg_count < 7000:  # Adjusted threshold value
            color = (0, 255, 0)
            thickness = 3
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 3
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
    cvzone.putTextRect(img, f'Available: {spaceCounter}/{totalSpaces}', (10, 50), scale=2, thickness=2, offset=10)
    return img, spaceCounter

def updateFirebase(spaceCounter):
    global lastFirebaseUpdate
    if time.time() - lastFirebaseUpdate > 1:  # Update every 1 second
        db.child("parking_data").update({"available_spaces": spaceCounter, "total_spaces": totalSpaces})
        lastFirebaseUpdate = time.time()

# Start Firebase update thread
firebaseThread = threading.Thread(target=lambda: updateFirebase(0))
firebaseThread.daemon = True
firebaseThread.start()

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    if success:
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, imgThreshold = cv2.threshold(imgGray, 45, 200, cv2.THRESH_BINARY)
        imgBlur = cv2.GaussianBlur(imgThreshold, (5, 5), 0)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgBlur, kernel, iterations=2)
        img, spaceCounter = checkParkingSpace(imgDilate, img)
        updateFirebase(spaceCounter)
        cv2.imshow("Image", img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
cv2.destroyAllWindows()