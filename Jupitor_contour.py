import numpy as np
import cv2
cap = cv2.VideoCapture('Jup_054415.avi')
 
while True:
    _, frame = cap.read()
    blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
 
    lower_limit = np.array([0, 10, 10])
    upper_limit = np.array([180, 180, 180])
    mask = cv2.inRange(hsv, lower_limit, upper_limit)
 
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
 
    for contour in contours:
        area = cv2.contourArea(contour)
 
        if area > 1000:
            cv2.drawContours(frame, contour, -1, (255, 255, 255), 3)
 
 
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)
 
    key = cv2.waitKey(1)
    if key == 27:
        break
 
cap.release()
cv2.destroyAllWindows()

#registax
