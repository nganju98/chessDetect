import cv2
#from ..fps import *

#v4l2-ctl -d 0 -c focus_absolute=0
#v4l2-ctl -d 0 -c focus_absolute=500
#v4l2-ctl -d 0 -C focus_absolute
#v4l2-ctl -d 0 -c focus_auto=0
#v4l2-ctl -d 0 -C focus_auto

cap = cv2.VideoCapture(0)
print(cap.getBackendName())
cap.set(3, 3264)
cap.set(4, 2448)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cfps = cap.get(cv2.CAP_PROP_FPS)
auto = cap.get(cv2.CAP_PROP_AUTOFOCUS)
print(f'auto={auto}')
result = cap.set(cv2.CAP_PROP_FOCUS, 0)
print(f'result={result}')
#fps = FPS(5).start()
while True:
    
    ret, img = cap.read()
    #print(img.shape)
    cv2.imshow('img',img)
    k = cv2.waitKey(1) & 0xff
    
    if k == 27:
        result = cap.set(cv2.CAP_PROP_FOCUS, 500)
        print(result)
    #fps.updateAndPrintAndReset()
cap.release()
cv2.destroyAllWindows()

