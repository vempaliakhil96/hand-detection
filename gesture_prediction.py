import cv2
import time
from clean_image import CleanImage
from keras.models import model_from_json
import copy
import numpy as np


class GesturePrediction:
    def __init__(self):
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights("model_weights.h5")
        self.model = loaded_model
        print("Loaded model from disk")
        self.gestures = {'high_five': 1, 'victory_sign': 2, 'index_finger': 3, 'shaka_sign': 4, 'horns': 5, 'loser': 6,
                         'null': 0}
        self.inv_gestures = {v: k for k, v in self.gestures.items()}
        self.image_cleaner = CleanImage()

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
                self.image_cleaner.subtract_background = self.image_cleaner.refresh_background()
                continue
            self.image_cleaner.frame = self.frame
            self.image_cleaner.process()
            self.frame = self.image_cleaner.frame
            prediction = self.get_prediction()
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
        roi = np.stack((roi, roi_copy, roi_copy), axis=3)
        prediction = self.model.predict(roi)[0]
        if np.max(prediction) > 0.05:
            prediction = self.inv_gestures[int(np.argmax(prediction))]
        else:
            prediction = self.inv_gestures[0]
        return prediction


if __name__ == '__main__':
    predict = GesturePrediction()
    predict.live_video()
