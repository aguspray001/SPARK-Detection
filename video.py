import numpy as np
import cv2

cap = cv2.VideoCapture("https://craggiest-guppy-2675.dataplicity.io/?action=stream?dummy=param.mjpg")
cap.set(3,640) #width=640
cap.set(4,480) #height=480
# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('hasil.avi',fourcc, 20.0, (640,480))

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame, flipCode = 1)

        # write the flipped frame
        out.write(frame)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()
