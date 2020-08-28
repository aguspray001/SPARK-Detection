import cv2 as open_cv
import numpy as np
import logging
from drawing_utils import draw_contours
from colors import COLOR_GREEN, COLOR_WHITE, COLOR_BLUE, COLOR_RED
import pyrebase
import threading

firebaseConfig = {
    "apiKey": "AIzaSyDgsmz-8E4VmH1WOlpypQOqTUmtH5nHcK8",
    "authDomain": "spark2020.firebaseapp.com",
    "databaseURL": "https://spark2020.firebaseio.com",
    "projectId": "spark2020",
    "storageBucket": "spark2020.appspot.com",
    "messagingSenderId": "34032245721",
    "appId": "1:34032245721:web:9f9d8c66eee0afb3ff17c8",
    "measurementId": "G-MKMMWSZC5E"
  }

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

# jumlah2 = 8
# hitung2 = 4

class MotionDetector:
    LAPLACIAN = 2
    DETECT_DELAY = 1

    def __init__(self,video, coordinates, start_frame):
        self.video = video
        self.coordinates_data = coordinates
        self.start_frame = start_frame
        self.contours = []
        self.bounds = []
        self.mask = []

    def detect_motion(self):
        capture = open_cv.VideoCapture(self.video)
        capture.set(3,400)
        capture.set(4,600)
        capture.set(open_cv.CAP_PROP_POS_FRAMES, self.start_frame)
        coordinates_data = self.coordinates_data
        logging.debug("coordinates data: %s", coordinates_data)

        for p in coordinates_data:
            coordinates = self._coordinates(p)
            logging.debug("coordinates: %s", coordinates)

            rect = open_cv.boundingRect(coordinates)
            logging.debug("rect: %s", rect)

            new_coordinates = coordinates.copy()
            new_coordinates[:, 0] = coordinates[:, 0] - rect[0]
            new_coordinates[:, 1] = coordinates[:, 1] - rect[1]
            logging.debug("new_coordinates: %s", new_coordinates)

            self.contours.append(coordinates)
            self.bounds.append(rect)

            mask = open_cv.drawContours(
                np.zeros((rect[3], rect[2]), dtype=np.uint8),
                [new_coordinates],
                contourIdx=-1,
                color=255,
                thickness=-1,
                lineType=open_cv.LINE_8)

            mask = mask == 255
            self.mask.append(mask)
            logging.debug("mask: %s", self.mask)

        statuses = [False] * len(coordinates_data)
        times = [None] * len(coordinates_data)

    
        while capture.isOpened():
            result, frame = capture.read()
            if frame is None:
                break

            if not result:
                raise CaptureReadError("Error reading video capture on frame %s" % str(frame))
            
            blurred = open_cv.GaussianBlur(frame.copy(), (5, 5), 3)
            grayed = open_cv.cvtColor(blurred, open_cv.COLOR_BGR2GRAY)
            new_frame = frame.copy()
            logging.debug("new_frame: %s", new_frame)
            # open_cv.imshow('gray',grayed)
            position_in_seconds = capture.get(open_cv.CAP_PROP_POS_MSEC) / 1000.0

            for index, c in enumerate(coordinates_data):
                status = self.__apply(grayed, index, c)

                if times[index] is not None and self.same_status(statuses, index, status):
                    times[index] = None
                    continue

                if times[index] is not None and self.status_changed(statuses, index, status):
                    if position_in_seconds - times[index] >= MotionDetector.DETECT_DELAY:
                        statuses[index] = status
                        times[index] = None
                    continue

                if times[index] is None and self.status_changed(statuses, index, status):
                    times[index] = position_in_seconds
            
            for index, p in enumerate(coordinates_data):
                coordinates = self._coordinates(p)
                # lastcolor = "True"
                color = COLOR_GREEN if statuses[index] else COLOR_BLUE
                draw_contours(new_frame, coordinates, str(p["id"] + 1), COLOR_WHITE, color)
                # with open('koordinat.txt', 'w') as f:
                #     f.write(str(coordinates_data))
                lasthitung = 0
                hitung = int(index)+1
                if statuses[index] != status:
                    if statuses[index] == False:
                        hitung = hitung-1
                    # else:
                    #     hitung = hitung+1
                    #open_cv.putText(new_frame,"          %d" %hitung, (30, 150),
                    #open_cv.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 255), 2)
                lasthitung = hitung
               
            # lastJumlah = 0
            jumlah = int(index)+1
            #open_cv.putText(new_frame,"jumlah: %d" %jumlah, (30, 95),
            #open_cv.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 255), 2)
            # hitung = 0


            #teks                
            #open_cv.putText(new_frame,"terpakai: ", (30, 150),
            #open_cv.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 255), 2)               
            empty = jumlah-lasthitung
            data = {"empty":0,"occupied":1}           
            db.child("Keputih").child("Parkir").child("1").update(data)
            # video_str = "https://craggiest-guppy-2675.dataplicity.io/?action=stream?dummy=param.mjpg"
            open_cv.imshow("video_parkir", new_frame)
                     
            k = open_cv.waitKey(1)
            
            if k == ord("q"):
                break
            
        capture.release()
        open_cv.destroyAllWindows()
    
    def __apply(self, grayed, index, p):
        coordinates = self._coordinates(p)
        logging.debug("points: %s", coordinates)
        rect = self.bounds[index]
        logging.debug("rect: %s", rect)

        roi_gray = grayed[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
        laplacian = open_cv.Laplacian(roi_gray, open_cv.CV_64F)
        logging.debug("laplacian: %s", laplacian)

        coordinates[:, 0] = coordinates[:, 0] - rect[0]
        coordinates[:, 1] = coordinates[:, 1] - rect[1]

        status = np.mean(np.abs(laplacian * self.mask[index])) < MotionDetector.LAPLACIAN
        logging.debug("status: %s", status)

        return status
    

    @staticmethod
    def _coordinates(p):
        return np.array(p["coordinates"])

    @staticmethod
    def same_status(coordinates_status, index, status):
        return status == coordinates_status[index]

    @staticmethod
    def status_changed(coordinates_status, index, status):
        return status != coordinates_status[index]

class CaptureReadError(Exception):
    pass
