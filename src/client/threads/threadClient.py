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


class threadClient(ThreadWithStop):

    # ================================ INIT ===============================================
    def __init__(self, serverip, port, debugger):
        super(threadClient, self).__init__()
        self.serverip = serverip
        self.port = port
        try:
            os.mkdir(f"./captures{self.port}/")
        except:
            pass
        # Kết nối đến server
        self.server_address = (self.serverip, self.port)  # Địa chỉ và cổng của server
        self.client_socket = socket.socket()
        self.client_socket.connect(self.server_address)
        self.payload_size = struct.calcsize("Q")

        # Nhận dữ liệu từ server

        self.data = b""
        self.count = 0
        self.frame_count = 0
        self.img_array = list()
        self.debugger = debugger

    # =============================== STOP ================================================
    def stop(self):
        self.client_socket.close()
        # cv2.destroyAllWindows()
        super(threadClient, self).stop()


    # ================================ RUN ================================================
    def run(self):
        """This function will run while the running flag is True. It captures the image from camera and make the required modifies and then it send the data to process gateway."""
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
            image = cv2.resize(image,(image.shape[1]*2, image.shape[0]*2))
            cv2.imshow(f'{self.port}', image)

            if (self.count % 5 == 0):
                self.frame_count += 1
                cv2.imwrite(f"./captures{self.port}/frame{self.frame_count}.jpg", image)
            self.img_array.append(image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                out = cv2.VideoWriter(f'./captures{self.port}/capture.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 15, (320, 240))
                for i in self.img_array:
                    out.write(i)
                out.release()
                self.stop()
                break
            
            self.count += 1

    # =============================== START ===============================================
    def start(self):
        super(threadClient, self).start()

        
