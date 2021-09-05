import cv2
import time
import datetime


class Frame:
    def __init__(self, img, frameNumber, frameTime):
        self.img = img
        self.frameNumber = frameNumber
        self.frameTime = frameTime

    

class Camera:
    def __init__(self):
        #self.zoom = False
        self.frameCtr = 0
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 3264)
        self.cap.set(4, 2448)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        cfps = self.cap.get(cv2.CAP_PROP_FPS)
        print (f'capture fps = {cfps}')
        self.cap.read() # warm up camera
        time.sleep(2)
    
    def read(self):
        _, img = self.cap.read()
        frame = Frame(img, self.frameCtr, datetime.datetime.now())
        return frame

    def release(self):
        self.cap.release()