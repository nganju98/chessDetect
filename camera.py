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
        self.focus = 165
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 2048) # 3264x2448 was better but hurt performance, this works fine
        self.cap.set(4, 1536) # 2448
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        cfps = self.cap.get(cv2.CAP_PROP_FPS)
        print (f'camera capture fps = {cfps}')
        _, img = self.cap.read() # warm up camera
        print(f'resolution={img.shape}')
        self.setFocus()
        time.sleep(.2)
        _, img = self.cap.read()
        self.setFocus() # call it twice to get this flaky camera to focus

        #self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        #auto = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        #print(f'camera autofocus={auto}')
        #result = self.cap.set(cv2.CAP_PROP_FOCUS, self.focus)
        #print(f'camera setting focus to {self.focus}, result={result}')
       


    def read(self):
        _, img = self.cap.read()
        frame = Frame(img, self.frameCtr, datetime.datetime.now())
        self.frameCtr+=1
        return frame

    def release(self):
        self.cap.release()

    def focusUp(self):
        self.focus += 5
        self.setFocus()

    
    def focusDown(self):
        self.focus -= 5
        self.setFocus()

    def setFocus(self):
        result = self.cap.set(cv2.CAP_PROP_FOCUS, self.focus)
        print(f'camera setting focus to {self.focus}, result={result}')

        
    def changeFocus(self):
        print('change focus')
        result = self.cap.set(cv2.CAP_PROP_FOCUS, 500)
        print(f'camera setting focus to 500, result={result}')
    
    def getFocusParams(self):
        auto = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        focus = self.cap.get(cv2.CAP_PROP_FOCUS) 
        return auto, focus