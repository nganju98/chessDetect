import cv2
#from ..fps import *

#v4l2-ctl -d 0 -c focus_absolute=0
#v4l2-ctl -d 0 -c focus_absolute=500
#v4l2-ctl -d 0 -C focus_absolute
#v4l2-ctl -d 0 -c focus_auto=0
#v4l2-ctl -d 0 -C focus_auto


def list_ports():
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
            camera.set(3, 2048) 
            camera.set(4, 1536) 
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                notWorking = 0
                print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                available_ports.append(dev_port)
        dev_port +=1
    return available_ports,working_ports


available, working = list_ports()
print(available)
print(working)
# cap = cv2.VideoCapture(0)
# print(cap.getBackendName())
# cap.set(3, 3264)
# cap.set(4, 2448)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# cfps = cap.get(cv2.CAP_PROP_FPS)
# auto = cap.get(cv2.CAP_PROP_AUTOFOCUS)
# print(f'auto={auto}')
# result = cap.set(cv2.CAP_PROP_FOCUS, 0)
# print(f'result={result}')
# #fps = FPS(5).start()
# while True:
    
#     ret, img = cap.read()
#     #print(img.shape)
#     cv2.imshow('img',img)
#     k = cv2.waitKey(1) & 0xff
    
#     if k == 27:
#         result = cap.set(cv2.CAP_PROP_FOCUS, 500)
#         print(result)
#     #fps.updateAndPrintAndReset()
# cap.release()
# cv2.destroyAllWindows()

