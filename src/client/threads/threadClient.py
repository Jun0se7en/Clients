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

import qdarktheme

import folium
from ui_interface import *


class threadClient(QThread):

    # ================================ INIT ===============================================
    def __init__(self, ip_address, port, ImageUpdateSlot, debugger):
        super(threadClient, self).__init__()
        try:
            os.mkdir(f"./captures{self.port}/")
        except:
            pass
        # Kết nối đến server
        self.ip_address = ip_address
        self.port = port
        self.payload_size = struct.calcsize("Q")

        # Nhận dữ liệu từ server

        self.data = b""
        self.count = 0
        self.frame_count = 0
        self.img_array = list()
        self.ImageUpdate = pyqtSignal(QImage)
        self.ImageUpdate.connect(ImageUpdateSlot)
        self.debugger = debugger

    # =============================== STOP ==============================        print('Socket Close')
    def stop(self):
        self.client_socket.close()
        self._running = False
        self.terminate()


    # ================================ RUN ================================================
    def run(self):
        """This function will run while the running flag is True. It captures the image from camera and make the required modifies and then it send the data to process gateway."""
        self.client_socket = socket.socket()
        print(f'Socket Created!!!')
        self.client_socket.connect((self.ip_address, self.port))
        while self._running:
            chunk = self.client_socket.recv(4*1024)
            if not chunk:
                break
            self.data+=chunk
            packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            
            while len(self.data)<msg_size:
                self.data+=self.client_socket.recv(4*1024)
            image = self.data[:msg_size]
            self.data = self.data[msg_size:]
            
            image = pickle.loads(image)
            image_data = base64.b64decode(image)
            img = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(img, cv2.IMREAD_COLOR)
            # print(image)
            image = cv2.resize(image,(320, 240))
            
            ## Show Image
            # Get the frame height, width and channels.
            height, width, channels = image.shape
            # Calculate the number of bytes per line.
            bytes_per_line = width * channels
            FlippedImage = cv2.flip(image, 1)
            qt_rgb_image = QImage(FlippedImage.data, width, height, bytes_per_line, QImage.Format_RGB888)
            qt_rgb_image_scaled = qt_rgb_image.scaled(320, 240, Qt.KeepAspectRatio)
            self.ImageUpdate.emit(qt_rgb_image_scaled)

            if (self.count % 5 == 0):
                self.frame_count += 1
                cv2.imwrite(f"./captures{self.port}/frame{self.frame_count}.jpg", image)
            self.img_array.append(image)
            
            key = ''
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                out = cv2.VideoWriter(f'./captures{self.port}/capture.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 15, (320, 240))
                for i in self.img_array:
                    out.write(i)
                out.release()
                self.stop()
                break
            abc_bytes = pickle.dumps(chr(key))
            message = struct.pack("Q", len(abc_bytes))+abc_bytes
            self.client_socket.sendall(message)
            self.count += 1

    # =============================== START ===============================================
    def start(self):
        self._running = True
        

        
