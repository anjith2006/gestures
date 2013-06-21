#!/usr/bin/python2

import cv2
import math
import subprocess
import numpy
import ghmm
import models
import simplejson

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

def movement_direction(x_delta, y_delta, threshold = 10):
    if abs(x_delta) > threshold or abs(y_delta) > threshold:
        degree = math.atan2(y_delta, x_delta)
        if -0.875 * math.pi <= degree < -0.625 * math.pi:
            direction = models.UP_RIGHT
        elif -0.625 * math.pi <= degree < -0.375 * math.pi:
            direction = models.UP
        elif -0.375 * math.pi <= degree < -0.125 * math.pi:
            direction = models.UP_LEFT
        elif -0.125 * math.pi <= degree < 0.125 * math.pi:
            direction = models.LEFT
        elif 0.125 * math.pi <= degree < 0.375 * math.pi:
            direction = models.DOWN_LEFT
        elif 0.375 * math.pi <= degree < 0.625 * math.pi:
            direction = models.DOWN
        elif 0.625 * math.pi <= degree < 0.875 * math.pi:
            direction = models.DOWN_RIGHT
        else:
            direction = models.RIGHT

        return direction
    else:
        return None


def execute(emission_seq, models):
    max_comm = None
    max_val = 0
    for model, command in models:
        #print(model.forward(emission_seq))
        res = model.forward(emission_seq)

        if res[1][-1] > max_val:
            max_val = res[1][-1]
            max_comm = command

    if max_val >= 0.3:
        subprocess.call(max_comm)
        print(max_comm)


def train(emission_seq, model):
    model.baumWelch(emission_seq)

def current_image(cam):
    img = cam.read()[1]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Extract by color and make binary image (=black/white)
    img = cv2.inRange(img, (70, 50, 50), (130, 200, 200))
                        
    # erode and dilate to reduce noise
    img = cv2.erode(img, numpy.array([[1] * ed_size] * ed_size), iterations=2)
    img = cv2.dilate(img, numpy.array([[1] * ed_size] * ed_size), iterations=2)

    return img


# Two variables to determine changes in train-mode
train_mode_pre = False
train_mode = False
train_target = 0

ed_size = 50

cam = cv2.VideoCapture(0)
 
winName = "Movement Indicator"
cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)

img = current_image(cam)

x1, y1 = pointer_pos(img)

not_changed = 0

while True:
    # if we switched to train mode, delete all prior knowledge
    if train_mode_pre is False and train_mode is True:
        path = []
        not_changed = 0

    train_mode_pre = train_mode
    x0 = x1
    y0 = y1

    img = current_image(cam)
    x1, y1 = pointer_pos(img)

    if x1 is not None and x0 is not None and y1 is not None and y0 is not None:
        x_delta = x1 - x0
        y_delta = y1 - y0

        direction = movement_direction(x_delta, y_delta)
        if direction is not None:
            path.append(direction)
        else:
            not_changed += 1
    else:
        not_changed += 1
    if not_changed > 5:
        if len(path) >= 2:
            print(path)
            if train_mode == False:
                execute(ghmm.EmissionSequence(models.sigma, path), models.models)
            else:
                models.training_data[train_target].append(path)
                print("Training model %d" % (train_target,))
                train_mode = False
                print("Leaving training mode")

                with open("".join(('models/', str(train_target), '.train')), 'w') as f:
                    simplejson.dump(models.training_data[train_target], f)

        path = []
        not_changed = 0
    
    cv2.imshow(winName, img)

    key = cv2.waitKey(1)
    if key == 27:
        cv2.destroyWindow(winName)
        break
    elif key == ord('0'):
        train_mode = True
        train_target = 0
    elif key == ord('1'):
        train_mode = True
        train_target = 1
    elif key == ord('2'):
        train_mode = True
        train_target = 2
    elif key == ord('3'):
        train_mode = True
        train_target = 3

print "Goodbye"
