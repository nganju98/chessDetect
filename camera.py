import cv2
import time
import datetime


class Frame:
    def __init__(self, img, frameNumber, frameTime):
        self.img = img
        self.frameNumber = frameNumber
        self.frameTime = frameTime


class CameraDevice:
    def __init__(self, port, width, height):
        self.port = port
        self.width = width
        self.height = height
    
    def description(self):
        return f'Camera {self.port} ({self.width}x{self.height})'

class Camera:
    HEIGHT = 1536 # 3264x2448 was better but hurt performance, this works fine
    WIDTH = 2048

    def __init__(self, cameraPort = 0):
        #self.zoom = False
        self.frameCtr = 0
        self.focus = 165
        self.cap = cv2.VideoCapture(cameraPort)
        self.cap.set(3, Camera.WIDTH) 
        self.cap.set(4, Camera.HEIGHT) 
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
       

    def listPorts():
        notWorking = 0
        dev_port = 0
        working_ports = []
        available_ports = []
        while notWorking < 2:
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                notWorking += 1
                print("Port %s is not working." %dev_port)
            else:
                camera.set(3, Camera.WIDTH) 
                camera.set(4, Camera.HEIGHT) 
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    notWorking = 0
                    print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                    working_ports.append(CameraDevice(dev_port, int(w), int(h)))
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                    available_ports.append(dev_port)
                camera.release()
            dev_port +=1
        return working_ports


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



if __name__ == "__main__":
    _, working = Camera.listPorts()
    for cam in working:
        print(cam.description())