import cv2
import time
from .clean_image import CleanImage
from keras.models import model_from_json
import copy
import numpy as np
import keyboard
import os

class GesturePrediction :

    def file_path(self, relative_path):
        dir = os.path.dirname(os.path.abspath(__file__))
        split_path = relative_path.split("/")
        new_path = os.path.join(dir, *split_path)
        return new_path
        
    def __init__(self):
        json_file = open(self.file_path('config/model_v1-0.json'), 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights(self.file_path('config/model_weights_v1-0.h5'))
        self.model = loaded_model
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
                if count>2:
                    keyboard.press_and_release('cmd+shift+3')
                    time.sleep(1)
                    count=0
            else:
                count=0
            print(count)
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
        prediction_num = self.model.predict(roi)[0][0]
        if prediction_num>0.7:
            prediction = self.inv_gestures[1]
        else:
            prediction = self.inv_gestures[0]
        return prediction, 100*prediction_num


# if __name__ == '__main__':
#     predict = GesturePrediction()
#     predict.live_video()
