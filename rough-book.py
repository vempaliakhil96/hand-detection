#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 23:19:00 2020

@author: akhilvempali
"""
import cv2
import numpy as np


def live_video(camera_port=0):
    """
    Opens a window with live video.
    :param camera_port:
    :return:
    """
    video_capture = cv2.VideoCapture(camera_port)
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        frame = cv2.flip(frame, 1)
        frame = process_image(frame)
        roi = get_region_of_interest(frame)
        # Display the resulting frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


def process_image(frame):
    kernel = np.ones((1, 1), np.uint8)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of skin color in HSV
    lower_skin = np.array([0, 33, 0], dtype=np.uint8)
    upper_skin = np.array([37, 148, 255], dtype=np.uint8)
    # extract skin colur image
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    # extrapolate the hand to fill dark spots within
    mask = cv2.dilate(mask, kernel, iterations=4)
    # blur the image
    frame = cv2.GaussianBlur(mask, (5, 5), 100)
    return frame


def get_region_of_interest(frame):
    start_point = (760, 110)
    end_point = (1200, 530)
    color = (255, 0, 0)
    thickness = 1
    frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
    return frame[start_point[1]:end_point[1], start_point[0]: end_point[0]]


if __name__ == '__main__':
    live_video()
