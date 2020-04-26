import cv2
import time
import logging
import os, sys
import traceback
import numpy as np

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class DetectSkinColor:
    def __init__(self, username, camera_port=0, record=False):
        logging.info("Workflow initiated by user: " + username)
        self.camera_port = camera_port
        self.record = record
        self.username = username
        self.video_capture = cv2.VideoCapture(self.camera_port)
        if self.video_capture.isOpened():
            self.frame_width = self.video_capture.get(3)
            self.frame_height = self.video_capture.get(4)

    @staticmethod
    def create_rectangle(_x, _y, height, width):
        x1 = int(_x)
        y1 = int(_y + height)
        x2 = int(_x + width)
        y2 = int(_y)
        return (x1, y1), (x2, y2)

    def get_region_of_interest(self, frame, _x, _y, height, width):
        end_point, start_point = self.create_rectangle(_x, _y, height, width)
        color = (255, 0, 0)
        thickness = 1
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
        return frame[start_point[1] + thickness: end_point[1] - thickness,
                     end_point[0] + thickness: start_point[0] - thickness]

    @staticmethod
    def calculate_thresholds(hsv_result):
        roi_1_hsv_values = hsv_result[0]
        roi_2_hsv_values = hsv_result[1]
        roi_1_h = np.stack(tuple([itr[0] for itr in roi_1_hsv_values]), axis=0)
        roi_1_s = np.stack(tuple([itr[1] for itr in roi_1_hsv_values]), axis=0)
        roi_1_v = np.stack(tuple([itr[2] for itr in roi_1_hsv_values]), axis=0)

        roi_2_h = np.stack(tuple([itr[0] for itr in roi_2_hsv_values]), axis=0)
        roi_2_s = np.stack(tuple([itr[1] for itr in roi_2_hsv_values]), axis=0)
        roi_2_v = np.stack(tuple([itr[2] for itr in roi_2_hsv_values]), axis=0)

        offsetLowThreshold = 80
        offsetHighThreshold = 30

        h_low_threshold = int(max(0, min(roi_1_h.mean(), roi_2_h.mean()) - offsetLowThreshold))
        h_high_threshold = int(min(255, max(roi_1_h.mean(), roi_2_h.mean()) + offsetHighThreshold))

        s_low_threshold = int(max(0, min(roi_1_s.mean(), roi_2_s.mean()) - offsetLowThreshold))
        s_high_threshold = int(min(255, max(roi_1_s.mean(), roi_2_s.mean()) + offsetHighThreshold))

        v_low_threshold = int(max(0, min(roi_1_v.mean(), roi_2_v.mean()) - offsetLowThreshold))
        v_high_threshold = int(min(255, max(roi_1_v.mean(), roi_2_v.mean()) + offsetHighThreshold))
        low = [h_low_threshold, s_low_threshold, v_low_threshold]
        high = [h_high_threshold, s_high_threshold, v_high_threshold]
        return low, high

    def record_skin_color(self):
        logging.info("Please enter 'r' to begin recording.")
        result = []
        roi_1_hsv_values = []
        roi_2_hsv_values = []
        while True:
            _time = time.time()
            # Capture frame-by-frame
            ret, frame = self.video_capture.read()
            frame = cv2.flip(frame, 1)
            roi1 = self.get_region_of_interest(frame, self.frame_width * 0.7, self.frame_height / 2, 50, 50)
            roi2 = self.get_region_of_interest(frame, self.frame_width * 0.7, self.frame_height / 3, 50, 50)
            if cv2.waitKey(1) & 0xFF == ord('r'):
                logging.info("Recording started!")
                self.record = True
            if self.record:
                hsv = cv2.cvtColor(roi1, cv2.COLOR_BGR2HSV)
                h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
                roi_1_hsv_values.append((h, s, v))
                hsv = cv2.cvtColor(roi2, cv2.COLOR_BGR2HSV)
                h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
                roi_2_hsv_values.append((h, s, v))
            # Display the resulting frame
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.record = False
                logging.info("Recording finished!")
                break
        # When everything is done, release the capture
        self.video_capture.release()
        cv2.destroyAllWindows()
        result.append(roi_1_hsv_values)
        result.append(roi_2_hsv_values)
        return result


if __name__ == '__main__':
    try:
        logging.info("Starting application...")
        user_name = input("Please enter your name: ")
        obj = DetectSkinColor(user_name)
        hsv_result = obj.record_skin_color()
        print("Length: " + str(len(hsv_result)))
        hsv_thresholds = obj.calculate_thresholds(hsv_result)
        print(hsv_thresholds[0])
        print(hsv_thresholds[1])
    except KeyboardInterrupt:
        logging.info("Exiting because of KeyboardInterrupt")
        exit(0)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise e
    finally:
        logging.info("Exiting application.")
