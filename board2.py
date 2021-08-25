import cv2
import imutils
import go
import numpy as np


def findCorners(img):
    print(img.shape)
    bbox, ids = go.findArucoMarkers(img)
    ids = ids.flatten()
    # print(bbox)
    # print(ids)
    # print (np.where(ids == 0)[0][0])
    # print(bbox[1])
    #bbox = bbox.astype(int)
    tl = bbox[np.where(ids == 0)[0][0]][0][0].astype(int)
    tr = bbox[np.where(ids == 1)[0][0]][0][0].astype(int)
    br = bbox[np.where(ids == 2)[0][0]][0][0].astype(int)
    bl = bbox[np.where(ids == 3)[0][0]][0][0].astype(int)
    return np.array([tl, tr, br, bl], np.float32)

def between(p1, p2, distance):
    x = (p2[0] - p1[0]) * distance + p1[0]
    y = (p2[1] - p1[1]) * distance + p1[1]
    return [int(x), int(y)]

img = cv2.imread('./images/corners.jpg')
rect = findCorners(img)
tl, tr, br, bl = rect
print(rect)
widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
# ...and now for the height of our new image
heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
# take the maximum of the width and height values to reach
# our final dimensions
maxWidth = max(int(widthA), int(widthB))
maxHeight = max(int(heightA), int(heightB))
# construct our destination points which will be used to
# map the screen to a top-down, "birds eye" view
dst = np.array([
	[0, 0],
	[maxWidth - 1, 0],
	[maxWidth - 1, maxHeight - 1],
	[0, maxHeight - 1]], dtype = "float32")
# calculate the perspective transform matrix and warp
# the perspective to grab the screen
print(rect)
print(dst)
M = cv2.getPerspectiveTransform(rect, dst)
warp = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
print(warp.shape)
# print("************")
# print(tl)
# print(tr)
for j in range(0,9):
    yl = between([0,0], [0,maxHeight-1], j/8)

    for i in range(0,9):
        bt = between(yl, [maxWidth-1,yl[1]], i/8)
        print(bt)
        cv2.circle(warp, bt, 10, (255,0,0), 3)

# print(bt)
# cv2.circle(img, tl, 10, (255,0,0), 3)
# cv2.circle(img, tr, 10, (255,0,0), 3)
# cv2.circle(img, bl, 10, (255,0,0), 3)
# cv2.circle(img, br, 10, (255,0,0), 3)

# cv2.line(img, tl, tr, (255,0,0), 3)

resized = imutils.resize(warp, 800)
cv2.imshow('img',resized)
cv2.waitKey(0)
cv2.destroyAllWindows()