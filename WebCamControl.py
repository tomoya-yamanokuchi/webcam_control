import os
import time
from multiprocessing import Process, Queue
import cv2


class WebCamControl:
    def __init__(self, cam_id=1):
        self.cam_id = cam_id
        capture_size   = (1920, 1080)
        self.img_size  = (1000, 1000)
        self.w, self.h = capture_size[0], capture_size[1]
        self.fps       = 30  # default
        self.video_len = 1  # [s]
        # ----
        self.fname_queue, self.stop_queue = Queue(), Queue()
        self.p = Process(target=self.record_process, args=(self.fname_queue, self.stop_queue))
        self.p.start()


    def record_process(self, fname_queue, stop_queue):
            w, h = self.w, self.h

            cam = cv2.VideoCapture(self.cam_id, cv2.CAP_V4L2)
            cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            cam.set(3, w)
            cam.set(4, h)

            if not cam.isOpened():
                print("Failed to open webcam in child process.")
                return

            while True:
                fname = fname_queue.get()
                if fname == 'FIN':
                    print('camera_process has been finished.')
                    break

                out = cv2.VideoWriter(fname, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), self.fps, (w, h))
                imgs = []
                while True:
                    ret, frame = cam.read()
                    if not ret:
                        print("Failed to read from camera.")
                        continue
                    imgs.append(frame.copy())
                    try:
                        fl = stop_queue.get_nowait()
                    except:
                        continue
                    if fl:
                        break
                [out.write(e) for e in imgs]
                out.release()
                print('created')

            cam.release()
            print('camera object is released!')


    def rec_start(self, fname: str):
        """
        Record start
        :param fname_queue: dir_name + fname (e.g. /hoge/fuga/piyo.mp4)
        """
        self.fname_queue.put(fname)

    def rec_stop(self):
        """
        Record stop
        """
        self.stop_queue.put(True)

    def release(self):
        """
        Cam object relase
        """
        self.fname_queue.put('FIN')


if __name__ == '__main__':
    # test usecase
    webcam = WebCamControl(cam_id=1)
    webcam.rec_start('./test_video_front.mp4')
    # -------
    for i in range(30):
        # Do somthing...
        time.sleep(0.1)
        # Do somthing...
    # -------
    webcam.rec_stop()
    webcam.release()
