import cv2
import pickle
import numpy as np

img = cv2.imread('camimg2.png')
temp_img = img.copy()

cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", img.shape[1], img.shape[0])

# Check if CarParkPos file exists
try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except FileNotFoundError:
    # If file does not exist, create it with default values
    posList = []
    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)

width, height = 70, 130
thickness = 2

dragging = False
drag_index = -1

def mouseClick(event, x, y, flags, params):
    global temp_img, dragging, drag_index, posList
    if event == cv2.EVENT_RBUTTONDOWN:
        posList.append((x, y))
        with open('CarParkPos', 'wb') as f:  # Save posList to file
            pickle.dump(posList, f)
        temp_img = img.copy()
        for pos in posList:
            cv2.rectangle(temp_img, pos, (pos[0] + width, pos[1] + height), (255, 0, 0), thickness)
    elif event == cv2.EVENT_LBUTTONDOWN:
        delete_index = -1
        for i, pos in enumerate(posList):
            if abs(x - pos[0]) < width and abs(y - pos[1]) < height:
                delete_index = i
                break
        if delete_index != -1:
            del posList[delete_index]
            with open('CarParkPos', 'wb') as f:  # Save posList to file
                pickle.dump(posList, f)
            temp_img = img.copy()
            for pos in posList:
                cv2.rectangle(temp_img, pos, (pos[0] + width, pos[1] + height), (255, 0, 0), thickness)

cv2.setMouseCallback("Image", mouseClick)

while True:
    cv2.imshow("Image", temp_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

