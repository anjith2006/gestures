import cv2
import math
import subprocess
import numpy
import ghmm
import models

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

path = []

def diffImg(t0, t1, t2):
    d1 = cv2.absdiff(t2, t1)
    d2 = cv2.absdiff(t1, t0)
    return cv2.bitwise_and(d1, d2)

def pointer_pos(img):
    moments = cv2.moments(img)
    area = moments['m00']
    
    if area > 100000:
        x = moments['m10'] / area
        y = moments['m01'] / area

        return x, y

    return (None, None)

def execute(emission_seq, models):
    max_comm = None
    max_val = 0
    for model, command in models:
        #print(model.forward(emission_seq))
        res = model.forward(emission_seq)

        if res[1][-1] > max_val:
            max_val = res[1][-1]
            max_comm = command

    if max_val >= 0.4:
        subprocess.call(max_comm)
        print(max_comm)


cam = cv2.VideoCapture(0)
 
winName = "Movement Indicator"
cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)

img = cv2.cvtColor(cam.read()[1], cv2.COLOR_BGR2HSV)
cv2.imwrite("test.jpg", img)
img = cv2.inRange(img, (70, 100, 100), (150, 255, 255))
img = cv2.erode(img, numpy.array([[1,1,1],[1,1,1],[1,1,1]]))
img = cv2.dilate(img, numpy.array([[1,1,1],[1,1,1],[1,1,1]]), iterations=3)

x1, y1 = pointer_pos(img)

not_changed = 0

while True:
    x0 = x1
    y0 = y1
    
    img = cv2.cvtColor(cam.read()[1], cv2.COLOR_BGR2HSV)
    img = cv2.inRange(img, (70, 50, 50), (150, 255, 255))
    img = cv2.erode(img, numpy.array([[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1]]), iterations=2)
    img = cv2.dilate(img, numpy.array([[1,1,1],[1,1,1],[1,1,1]]), iterations=3)
    x1, y1 = pointer_pos(img)

    if x1 != None and x0 != None and y1 != None and y0 != None:
        x_delta = x1 - x0
        y_delta = y1 - y0
        
        if abs(x_delta) > 10 or abs(y_delta) > 10:
            degree = math.atan2(y_delta, x_delta)
            if -0.75 * math.pi <= degree < -0.25 * math.pi:
                path.append(UP)
            elif -0.25 * math.pi <= degree < 0.25 * math.pi:
                path.append(LEFT)
            elif 0.25 * math.pi <= degree < 0.75 * math.pi:
                path.append(DOWN)
            else:
                path.append(RIGHT)
            #print("Appended to")
            #print(path)
        else:
            not_changed += 1
    if not_changed > 5:
        if len(path) >= 2:
            print(path)
            execute(ghmm.EmissionSequence(models.sigma, path), models.models)
        path = []
        not_changed = 0
    
    cv2.imshow(winName, img)

    key = cv2.waitKey(50)
    if key == 27:
        cv2.destroyWindow(winName)
        break
 
print "Goodbye"
