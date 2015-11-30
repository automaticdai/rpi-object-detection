"""

<Description>
This is a blob detection program which intend to find the biggest blob
in a given picture taken by a camera and return its central positon.

Key Steps:
[1] Image Filtering
[2] Image Segmentation
[3] Detect Blobs
[4] Filter Blobs using a criteria
[5] Track Blobs
</Description>

<Author>
Xiaotian Dai
YunFei Robotics Labrotary
htttp://www.yfworld.com
</Author>

"""

import cv2
import numpy as np

def isset(v): 
    try: 
        type (eval(v)) 
    except: 
        return 0 
    else: 
        return 1

# create video capture
cap = cv2.VideoCapture(0)

while(1):
    
    # Read the frames frome a camera
    _,frame = cap.read()
    frame = cv2.blur(frame,(3,3))

    # Or get it from a JPEG
    #frame = cv2.imread('frame0010.jpg', 1)
    
    # Convert the image to hsv space and find range of colors
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # This is for RED tag
    #thresh = cv2.inRange(hsv,np.array((120, 80, 80)), np.array((180, 255, 255)))

    # This is for GREEN tag
    thresh = cv2.inRange(hsv,np.array((50, 80, 80)), np.array((120, 255, 255)))

    thresh2 = thresh.copy()

    # find contours in the threshold image
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # finding contour with maximum area and store it as best_cnt
    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt = cnt

    # finding centroids of best_cnt and draw a circle there     
    if isset('best_cnt'):
        M = cv2.moments(best_cnt)
        cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
        cv2.circle(frame,(cx,cy),5,255,-1)
        print "Central pos: (%d, %d)" % (cx,cy)
    else:
        print "[Warning]Tag lost..."
        
    # Show the original and processed image
    cv2.imshow('frame', frame)
    cv2.imshow('thresh', thresh2)
    
    # if key pressed is 'Esc' then exit the loop
    if cv2.waitKey(33)== 27:
        break
    
# Clean up and exit the program
cv2.destroyAllWindows()
cap.release()
