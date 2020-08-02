# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QApplication, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal

import numpy as np
import sys
import threading

ratio = [640, 480]


class backupDisplay(QWidget):
    
    def __init__(self):
        super(backupDisplay, self).__init__()
        self.setGeometry(0, 0, ratio[0], ratio[1])
        # shutdown flag
        self.shutdown = False
        # Create the Layout
        layout = QHBoxLayout()
        # Create the Label
        self.pixmap_label = QLabel()
        self.pixmap_label.resize(ratio[0], ratio[1])
        # add the lable to the layout
        layout.addWidget(self.pixmap_label)
        self.setLayout(layout)
        # show the widget
        self.show()

    def stream_in(self, pix):
        #Assign the pixmap image to the label and update
        self.pixmap_label.setPixmap(pix)
        self.update()

    def closeEvent(self, event):
        self.shutdown = True
        event.accept()
        
class BackupCamera(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)

        # initialize the camera and grab a reference to the raw camera capture
        self.camera = PiCamera()
        self.camera.rotation = 180
        self.camera.resolution = (ratio[0], ratio[1])
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(ratio[0], ratio[1]))
        # allow the camera to warmup
        time.sleep(0.1)

        self.disp = backupDisplay()
    
    def update_image(self, pixmap):
        self.disp.pixmap_label.setPixmap(pixmap)

    def run(self):
        # capture frames from the camera
        for frame in self.camera.capture_continuous(self.rawCapture, format="rgb", use_video_port=True):
            # grab the raw NumPy array representing the image
            image = frame.array

            # Convert the image to a PyQt5 QPixmap
            qimage = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
            qimage = qimage.mirrored() #I want the image to act like an actual rear view mirror
            pixmap = QPixmap(qimage)
            pixmap = pixmap.scaled(ratio[0], ratio[1], Qt.KeepAspectRatio)
            self.update_image(pixmap)
            
            # clear the stream in preparation for the next frame
            self.rawCapture.truncate(0)
            # check for the shutdown flag
            if self.disp.shutdown:
                print('INFO: Shutting down . . .')
                time.sleep(2)
                break
		
		   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    bk_up_camera = BackupCamera()
    bk_up_camera.start()

    sys.exit(app.exec_())
