import cv2
#from ..fps import *


cap = cv2.VideoCapture(0)
print(cap.getBackendName())
cap.set(3, 3264)
cap.set(4, 2448)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cfps = cap.get(cv2.CAP_PROP_FPS)
#fps = FPS(5).start()
while True:
    
    ret, img = cap.read()
    print(img.shape)
    cv2.imshow('img',img)
    k = cv2.waitKey(1) & 0xff
    
    if k == 27:
        break
    #fps.updateAndPrintAndReset()
cap.release()
cv2.destroyAllWindows()

