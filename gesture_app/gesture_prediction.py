import cv2
import time
from clean_image import CleanImage
import tensorflow as tf
import copy
import numpy as np
import keyboard


class GesturePrediction :
    def __init__(self):
        self.interpreter = tf.lite.Interpreter(model_path="tf_lite_model.tflite")
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        print("Loaded model from disk")
        self.gestures = {'high_five': 1, 'null': 0}
        self.inv_gestures = {v: k for k, v in self.gestures.items()}
        self.image_cleaner = CleanImage()

    def live_video(self):
        t1 = time.time()
        video_capture = cv2.VideoCapture(0)
        capture_background_flag = True
        count = 0
        while True:
            t2 = time.time()
            ret, self.frame = video_capture.read()
            if t2 - t1 > 5:
                capture_background_flag = False
            if cv2.waitKey(1) & 0xFF == ord('r'):
                t1 = time.time()
                capture_background_flag = True
            if capture_background_flag:
                self.image_cleaner.subtract_background = self.image_cleaner.refresh_background()
                continue
            self.image_cleaner.frame = self.frame
            self.image_cleaner.process()
            self.frame = self.image_cleaner.frame
            prediction = self.get_prediction()
            if prediction[0] == 'high_five':
                count+=1
                if count>3:
                    keyboard.press_and_release('cmd+shift+3')
                    time.sleep(1)
                    count=0
            else:
                count=0
            cv2.putText(self.frame, f"Press Q to quit | Press R to refresh", (0, 20),
                        self.image_cleaner.font, self.image_cleaner.fontScale, (255, 255, 255))
            cv2.putText(self.frame, f"Prediction: {prediction}", (0, 40),
                        self.image_cleaner.font, self.image_cleaner.fontScale, (255, 255, 255))
            cv2.imshow('frame', self.frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video_capture.release()
        cv2.destroyAllWindows()

    def get_prediction(self):
        roi = self.frame
        roi = cv2.resize(roi, (224, 224))
        roi = np.expand_dims(roi, axis=0)
        roi_copy = copy.deepcopy(roi)
        roi = np.stack((roi, roi_copy, roi_copy), axis=3).astype(np.float32)
        self.interpreter.set_tensor(self.input_details[0]['index'], roi)
        self.interpreter.invoke()
        prediction = self.interpreter.get_tensor(self.output_details[0]['index'])
        prediction_num = prediction[0][0]
        if prediction_num>0.7:
            prediction = self.inv_gestures[1]
        else:
            prediction = self.inv_gestures[0]
        return prediction, 100*prediction_num


if __name__ == '__main__':
    predict = GesturePrediction()
    predict.live_video()
