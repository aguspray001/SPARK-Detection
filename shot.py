import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0) # video capture source camera (Here webcam of laptop)
cap.set(3,640) #width=640
cap.set(4,480) #height=480
cap.set(cv2.CAP_PROP_EXPOSURE, 0.9) 


i = 0
while(cap.isOpened()):
    #cv2.imshow('img1',frame) #display the captured image
    #if cv2.waitKey(1) & 0xFF == ord('y'): #save on pressing 'y' 
    #    cv2.imwrite('images/c12.png',frame)
    #    cv2.destroyAllWindows()
    #    break
    ret, frame = cap.read()
    if ret==True:
       cv2.imshow("camera", frame)
       cv2.imwrite('shutter/pic{:>05}.jpg'.format(i), frame)
       if cv2.waitKey(10) & 0xFF == ord('y'):
          break
    else:    
        break
    i += 1
#cap.release()
