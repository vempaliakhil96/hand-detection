import cv2
import time


class DetectSkinColor:
    def __init__(self, username, camera_port=0, record=False):
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

    def record_skin_color(self):

        skin_frames = []
        while True:
            _time = time.time()
            # Capture frame-by-frame
            ret, frame = self.video_capture.read()
            frame = cv2.flip(frame, 1)
            roi1 = self.get_region_of_interest(frame, self.frame_width*0.7, self.frame_height/2, 50, 50)
            roi2 = self.get_region_of_interest(frame, self.frame_width*0.7, self.frame_height/3, 50, 50)
            if cv2.waitKey(1) & 0xFF == ord('r'):
                self.record = True
            if self.record:
                name = "images/skin_color/" + "roi_1_" + self.username + "_" + str(int(_time)) + ".jpg"
                cv2.imwrite(name, roi1)
                skin_frames.append(roi1)
                name = "images/skin_color/" + "roi_2_" + self.username + "_" + str(int(_time)) + ".jpg"
                cv2.imwrite(name, roi2)
                skin_frames.append(roi2)
            # Display the resulting frame
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.record = False
                break
        # When everything is done, release the capture
        self.video_capture.release()
        cv2.destroyAllWindows()
        return skin_frames

    def get_region_of_interest(self, frame, _x, _y, height, width):
        end_point, start_point = self.create_rectangle(_x, _y, height, width)
        color = (255, 0, 0)
        thickness = 1
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
        return frame[start_point[1] + thickness: end_point[1] - thickness,
                     end_point[0] + thickness: start_point[0] - thickness]


if __name__ == '__main__':
    my_skin = DetectSkinColor("akhil")
    x = my_skin.record_skin_color()
