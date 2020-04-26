import cv2
import numpy as np
import time
import copy


class CleanImage:
    def __init__(self):
        self.cap_region_x_begin = 0.5  # start point/total width
        self.cap_region_y_end = 0.8  # start point/total width
        self.threshold = 90  # binary threshold
        self.blurValue = 63  # GaussianBlur parameter
        self.bgSubThreshold = 50
        self.image_size = (224, 224)
        self.learningRate = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontScale = 1
        self.thickness = 2
        self.subtract_background = self.refresh_background()
        self.kernel = np.ones((3, 3), np.uint8)
        self.lower_skin = np.array([0, 36, 0], dtype=np.uint8)
        self.upper_skin = np.array([57, 158, 255], dtype=np.uint8)

    def live_video(self):
        t1 = time.time()
        video_capture = cv2.VideoCapture(0)
        capture_background_flag = True
        while True:
            t2 = time.time()
            ret, self.frame = video_capture.read()
            if t2 - t1 > 5:
                capture_background_flag = False
            if cv2.waitKey(1) & 0xFF == ord('r'):
                t1 = time.time()
                capture_background_flag = True
            if capture_background_flag:
                self.subtract_background = self.refresh_background()
                continue
            self.process()
            cv2.imshow('frame', self.frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video_capture.release()
        cv2.destroyAllWindows()

    def process(self):
        frame = cv2.bilateralFilter(self.frame, 5, 50, 100)
        frame = cv2.flip(frame, 1)
        img = frame[0:int(self.cap_region_y_end * frame.shape[0]),
                    int(self.cap_region_x_begin * frame.shape[1]):frame.shape[1]]
        img_ = cv2.GaussianBlur(img, (self.blurValue, self.blurValue), 0)
        img_copy = copy.deepcopy(img_)
        mask = self.subtract_background.apply(img_, learningRate=self.learningRate)
        img = cv2.bitwise_and(img, img, mask=mask)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.frame = img
        self.find_contours(img_copy)
        # cv2.putText(self.frame, "Press Q to quit | Press R to refresh", (0, 20),
        #             self.font, self.fontScale, (255, 255, 255))

    def filter_by_skin_color(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
        # extrapolate the hand to fill dark spots within
        frame = cv2.dilate(mask, self.kernel, iterations=4)
        return frame

    def find_contours(self, img_copy):
        contours, _ = cv2.findContours(self.frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        if len(contours) == 0:
            return None
        biggest_contour = max(contours, key=cv2.contourArea)
        biggest_hull = cv2.convexHull(biggest_contour)
        mask = np.zeros(self.frame.shape, dtype='uint8')
        cv2.fillPoly(mask, pts=[biggest_contour], color=(255, 255, 255))
        mask2 = cv2.bitwise_and(self.frame, self.frame, mask=mask)
        img_copy = cv2.bitwise_and(img_copy, img_copy, mask=mask2)
        self.frame = img_copy
        self.frame = self.filter_by_skin_color(self.frame)
        # cv2.drawContours(self.frame, [biggest_contour], -1, (255, 255, 255), 3)
        # cv2.drawContours(self.frame, [biggest_hull], -1, (255, 255, 255), 3)

    @staticmethod
    def refresh_background():
        time.sleep(1)
        return cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=30, detectShadows=False)


if __name__ == '__main__':
    image_cleaner = CleanImage()
    image_cleaner.live_video()
