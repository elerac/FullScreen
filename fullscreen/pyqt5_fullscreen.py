"""
Caution! This fullscreen program using PyQt5 is really TRICKY.

This program consists of two modules, 
(1) fullscreen app (main funtion) and 
(2) launching and managing class for the fullscreen app (FullScreen class).
"""
import os
import sys
import argparse
import subprocess
import importlib

import numpy as np
from PyQt5 import QtWidgets, QtGui

is_pillow_available = importlib.util.find_spec("PIL") is not None
if is_pillow_available:
    from PIL import Image
else:
    import cv2

def imwrite(filename, image):
    if is_pillow_available:
        if image.ndim == 2:
            img_rgb = np.dstack([image]*3) # Gray -> RGB
        else:
            img_rgb = image[:, :, ::-1] # BGR -> RGB
        pil_img = Image.fromarray(img_rgb)
        pil_img.save(filename)
    else:
        cv2.imwrite(filename, image)

def resize(image, size):
    width, height = size
    if is_pillow_available:
        pil_img = Image.fromarray(image)
        pil_img = pil_img.resize((width, height), Image.NEAREST)
        return np.array(pil_img)
    else:
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_NEAREST)

class FullScreen:
    """Full-screen with PyQt5 backend
    """
    __tmp_filename = "__tmp_pyqt5_fullscreen.png"

    def __init__(self):
        app = QtWidgets.QApplication([])
        screen = app.primaryScreen()
        size = screen.size()
        self.width = size.width()
        self.height = size.height()
    
    @property
    def shape(self):
        return self.height, self.width, 3
    
    def imshow(self, image):
        self.destroyWindow()
        
        if image.shape[:2] != self.shape[:2]:
            image = resize(image, (self.width, self.height))
        
        imwrite(self.__tmp_filename, image)
        
        # Launch fullscreen app
        python_bin = sys.executable
        py_filename = __file__
        tmp_filename = self.__tmp_filename

        cmd = f"{python_bin} {py_filename} {tmp_filename}"
        self._p = subprocess.Popen(cmd, shell=True)
    
    def destroyWindow(self):
        if hasattr(self, "_p"):
            self._p.kill()

    def __del__(self):
        self.destroyWindow()
        os.remove(self.__tmp_filename)

def main():
    """Fullscreen app
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str)
    args = parser.parse_args()
    
    app = QtWidgets.QApplication([])
    
    widget = QtWidgets.QLabel()
    widget.showFullScreen()
    
    qt_img = QtGui.QImage(args.filename)
    widget.setPixmap(QtGui.QPixmap.fromImage(qt_img))

    widget.update()

    sys.exit(app.exec_())

if __name__=="__main__":
    main()
