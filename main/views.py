import os
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import cv2
import pickle
import cvzone
import numpy as np
from collections import deque
import pyrebase
import threading
import time
from django.http import StreamingHttpResponse
from django.conf import settings 

BASE_DIR = settings.BASE_DIR
 
# Create your views here.
def login_index(request):
    if request.user.is_authenticated:
        return redirect(reverse('parking_spot'))
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect(reverse('parking_spot'))
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'index.html')





def logout_view(request):
    logout(request)
    return redirect(reverse('login'))



def parking_spot(request):
    
    return render(request, 'parking_spot.html', )



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

# firebaseConfig = {
#     'apiKey': "",
#     'authDomain': "",
#     'databaseURL': '',
#     'projectId': "",
#     'storageBucket': "",
#     'messagingSenderId': "",
#     'appId': "",
#     'measurementId': ""
# }

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
file_path  = os.path.join(BASE_DIR, 'venv', 'CarParkPos')
video = os.path.join(BASE_DIR, 'venv', 'vid7.mp4')

cap = cv2.VideoCapture(video)

with open(file_path, 'rb') as f:
    posList = pickle.load(f)
width, height = 75, 135

# Initialize deque to store pixel counts for smoothing
pixel_counts = [deque(maxlen=5) for _ in posList]

# Initialize previous status for each parking space
prev_status = [""] * len(posList)

    

# width, height = 75, 135
# pixel_counts = [deque(maxlen=5) for _ in posList]
# totalSpaces = len(posList)
lastFirebaseUpdate = time.time()

def checkParkingSpace(imgPro, img):
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
            status = "Free"
        else:
            color = (0, 0, 255)
            thickness = 3
            status = "Occupied"
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, status, (x, y + height + 20), scale=1, thickness=1, offset=0)
        # Update Firebase only when status changes
        if status != prev_status[i]:
            prev_status[i] = status
            threading.Thread(target=updateFirebase, args=(i, status)).start()
    return img


def updateFirebase(space_id, status):
    global lastFirebaseUpdate
    if time.time() - lastFirebaseUpdate > 1:  # Update every 1 second
        db.child("parking_data").child(f"space_{space_id+1}").update({"status": status})
        lastFirebaseUpdate = time.time()

def video_feed():
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
            img = checkParkingSpace(imgDilate, img)
            ret, jpeg = cv2.imencode('.jpg', img)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

# def video_feed_view(request):
#     return StreamingHttpResponse(video_feed(), content_type='multipart/x-mixed-replace; boundary=frame')
