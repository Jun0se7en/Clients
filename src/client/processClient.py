from src.templates.workerprocess import WorkerProcess
from multiprocessing import Pipe
import socket
import pickle
import cv2
import base64
import numpy as np
import struct
import os

from src.client.threads.threadClient import threadClient


class processClient(WorkerProcess):
    """This process handle camera.\n
    Args:
            queueList (dictionar of multiprocessing.queues.Queue): Dictionar of queues where the ID is the type of messages.
            logging (logging object): Made for debugging.
            debugging (bool, optional): A flag for debugging. Defaults to False.
    """

    # ====================================== INIT ==========================================
    def __init__(self, serverip, port, debugging=False):
        self.serverip = serverip
        self.port = port
        
        self.debugging = debugging
        
        super(processClient, self).__init__()

    # ===================================== STOP ==========================================
    def stop(self):
        """Function for stopping threads and the process."""
        for thread in self.threads:
            thread.stop()
            thread.join()
        super(processClient, self).stop()

    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads."""
        super(processClient, self).run()

    # ===================================== INIT TH ======================================
    def _init_threads(self):
        """Create the Camera Publisher thread and add to the list of threads."""
        print(f'Initializing {self.port} Thread!!!')
        ClientTh = threadClient(
            self.serverip, self.port, self.debugging
        )
        self.threads.append(ClientTh)

