import cv2
import threading
import socket
import base64
import time
import numpy as np
import os

from multiprocessing import Pipe
from src.templates.threadwithstop import ThreadWithStop
import struct
import pickle
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsColorizeEffect
from PyQt5.QtGui import QFontDatabase, QPixmap, QImage
from PyQt5.QtCore import QThread, QEvent, pyqtSignal

import folium
from ui_interface import *


class threadClient(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, host, port):
        super().__init__()
        self.ThreadActive = True
        self.host = host
        self.port = port
        print(self.host, self.port)
        self.connect_flag = False 
        

    def run(self):
        self.ThreadActive = True

        # host = socket.gethostname()  # as both code is running on same pc
        # host = "192.168.2.193"
        # port = 12345  # socket server port number

        client_socket = socket.socket()  # instantiate
        print('Socket created')
        while not self.connect_flag:
            try:
                client_socket.connect((self.host, self.port))  # connect to the server
                self.connect_flag = True
            except:
                print('Connecting Failed!!! Retrying....')
                pass

        data = b""
        payload_size = struct.calcsize("Q")       

        while self.ThreadActive:
            while len(data) < payload_size:
                packet = client_socket.recv(4*1024)
                if not packet: break
                data+=packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q",packed_msg_size)[0]
            
            while len(data) < msg_size:
                data += client_socket.recv(4*1024)
            frame_data = data[:msg_size]
            data  = data[msg_size:]
            frame = pickle.loads(frame_data)
            # cv2.imshow("RECEIVING VIDEO",frame)
            image_data = base64.b64decode(frame)
            img = np.frombuffer(image_data, dtype=np.uint8)
            frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
            key = cv2.waitKey(1) & 0xFF
            if key  == 27:
                break

            # Get the frame height, width and channels.
            height, width, channels = frame.shape
            # Calculate the number of bytes per line.
            bytes_per_line = width * channels
            Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FlippedImage = cv2.flip(Image, 1)
            # Convert the image to Qt format.
            qt_rgb_image = QImage(FlippedImage.data, width, height, bytes_per_line, QImage.Format_RGB888)
            # Scale the image.
            # NOTE: consider removing the flag Qt.KeepAspectRatio as it will crash Python on older Windows machines
            # If this is the case, call instead: qt_rgb_image.scaled(1280, 720) 
            qt_rgb_image_scaled = qt_rgb_image.scaled(320, 240, Qt.KeepAspectRatio)  # 720p
            # qt_rgb_image_scaled = qt_rgb_image.scaled(1920, 1080, Qt.KeepAspectRatio)
            # Emit this signal to notify that a new image or frame is available.
            self.ImageUpdate.emit(qt_rgb_image_scaled)
        # When everything done, release the socket
        client_socket.close()
        # Tells the thread's event loop to exit with return code 0 (success).
        self.terminate()

    def stop(self):
        self.ThreadActive = False
        self.terminate()

        
