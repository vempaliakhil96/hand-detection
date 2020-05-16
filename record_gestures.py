import cv2
import os.path
from clean_image import CleanImage
import time

image_cleaner = CleanImage()


def live_video(gesture_name):
    t1 = time.time()
    video_capture = cv2.VideoCapture(0)
    capture_background_flag = True
    capture_flag = False
    while True:
        t2 = time.time()
        ret, frame = video_capture.read()
        if t2 - t1 > 5:
            capture_background_flag = False
        if cv2.waitKey(1) & 0xFF == ord('r'):
            t1 = time.time()
            capture_background_flag = True
        if capture_background_flag:
            image_cleaner.subtract_background = image_cleaner.refresh_background()
            continue
        image_cleaner.frame = frame
        image_cleaner.process()
        frame = image_cleaner.frame
        if not os.path.isdir("images/" + gesture_name):
            os.mkdir("images/" + gesture_name)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            capture_flag = not capture_flag
        if capture_flag:
            cv2.imwrite("images/" + gesture_name + "/" + gesture_name + "_" + str(int(t2)) + ".jpg", frame)
            cv2.putText(frame, f"Gesture Captured !", (0, 60),
                        image_cleaner.font, image_cleaner.fontScale, (255, 255, 255))
            pass
        cv2.putText(frame, f"Press Q to quit | Press R to refresh", (0, 20),
                    image_cleaner.font, image_cleaner.fontScale, (255, 255, 255))
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    live_video("null")
