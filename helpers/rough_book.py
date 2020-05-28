#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 23:19:00 2020

@author: akhilvempali
"""
import cv2
import time
import copy
import numpy as np
from keras.models import model_from_json

cap_region_x_begin = 0.5  # start point/total width
cap_region_y_end = 0.8  # start point/total width
threshold = 90  # binary threshold
blurValue = 21  # GaussianBlur parameter
bgSubThreshold = 50
image_size = (224, 224)
learningRate = 0
font = cv2.FONT_HERSHEY_SIMPLEX
# fontScale
fontScale = 3
# Blue color in BGR
color = (255, 255, 255)
# Line thickness of 2 px
thickness = 2

json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model_weights.h5")
print("Loaded model from disk")
inv_gestures = {1: 'open_hand', 2: 'close_fist', 0: 'null'}


def live_video(camera_port=0):
    """
    Opens a window with live video.
    :param camera_port:
    :return:
    """
    t1 = time.time()
    video_capture = cv2.VideoCapture(camera_port)
    fgbg = None
    init = True
    while True:
        t2 = time.time()
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        frame = cv2.bilateralFilter(frame, 5, 50, 100)
        frame = cv2.flip(frame, 1)
        if init:
            fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=30, detectShadows=False)
            if t2 - t1 > 0.5:
                init = False
                continue

        img = frame[0:int(cap_region_y_end * frame.shape[0]), int(cap_region_x_begin * frame.shape[1]):frame.shape[1]]
        img = cv2.GaussianBlur(img, (blurValue, blurValue), 0)
        mask = fgbg.apply(img, learningRate=learningRate)
        img = cv2.bitwise_and(img, img, mask=mask)
        mask = process_image(img)
        img = cv2.bitwise_and(img, img, mask=mask)
        img_copy = copy.deepcopy(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow('img', img)
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        if len(contours) == 0:
            continue
        biggest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest_contour)
        cv2.drawContours(img_copy, biggest_contour, -1, (0, 255, 0), 2)
        mask = np.zeros(img.shape, dtype='uint8')
        cv2.fillPoly(mask, pts=[biggest_contour], color=(255, 255, 255))
        roi = cv2.resize(mask, image_size)
        roi = np.expand_dims(roi, axis=0)
        prediction = get_prediction(roi)
        image = roi
        print(f'prediction {prediction}')
        image = image.reshape(image.shape[1:])
        cv2.imshow("frame", image)
        if cv2.waitKey(1) & 0xFF == ord('r'):
            cv2.imwrite("images/closed_fist/g2_" + str(int(t2)) + ".jpg", mask)
        # Display the resulting frame
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


# TODO: insert rgb values of lower and upper threshold
def process_image(frame):
    kernel = np.ones((3, 3), np.uint8)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of skin color in HSV
    lower_skin = np.array([0, 36, 0], dtype=np.uint8)
    upper_skin = np.array([57, 158, 255], dtype=np.uint8)
    # extract skin colur image
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    # extrapolate the hand to fill dark spots within
    frame = cv2.dilate(mask, kernel, iterations=4)
    # blur the image
    return frame


def get_region_of_interest(frame):
    start_point = (760, 110)
    end_point = (1200, 530)
    color = (255, 0, 0)
    thickness = 1
    frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
    return frame[start_point[1]:end_point[1], start_point[0]: end_point[0]]


def remove_background(frame, background_frame):
    img = abs(frame - background_frame)
    return img


def segment_hand_from_image(frame):
    roi = None
    blurValue = 41  # GaussianBlur parameter
    frame = cv2.bilateralFilter(frame, 5, 50, 100)
    frame = cv2.flip(frame, 1)
    img = frame
    img = cv2.GaussianBlur(img, (blurValue, blurValue), 0)
    img_copy = copy.deepcopy(img)
    img = process_image(img)
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi = img_copy[y: y + h, x: x + w]
        roi = process_image(roi)
    return roi


def get_prediction(roi):
    roi_copy = copy.deepcopy(roi)
    roi = np.stack((roi, roi_copy, roi_copy), axis=3)
    prediction = loaded_model.predict(roi)[0]
    if np.max(prediction) > 0.3:
        prediction = inv_gestures[int(np.argmax(prediction))]
    else:
        prediction = inv_gestures[0]
    return prediction


if __name__ == '__main__':
    live_video()
