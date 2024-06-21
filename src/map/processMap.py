from src.templates.workerprocess import WorkerProcess
from multiprocessing import Pipe
import socket
import pickle
import cv2
import base64
import numpy as np
import struct
import os

from src.map.threads.threadMap import threadMap


class processMap(WorkerProcess):
    """This process handle camera.\n
    Args:
            queueList (dictionar of multiprocessing.queues.Queue): Dictionar of queues where the ID is the type of messages.
            logging (logging object): Made for debugging.
            debugging (bool, optional): A flag for debugging. Defaults to False.
    """

    # ====================================== INIT ==========================================
    def __init__(self, serverip, port, WebviewUpdateSlot, debugging=False):
        self.serverip = serverip
        self.port = port
        self.WebviewUpdateSlot = WebviewUpdateSlot
        self.debugging = debugging
        super(processMap, self).__init__()

    # ===================================== STOP ==========================================
    def stop(self):
        """Function for stopping threads and the process."""
        for thread in self.threads:
            thread.stop()
            thread.join()
        super(processMap, self).stop()

    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads."""
        super(processMap, self).run()

    # ===================================== INIT TH ======================================
    def _init_threads(self):
        """Create the Camera Publisher thread and add to the list of threads."""
        MapTh = threadMap(
            self.serverip, self.port, self.WebviewUpdateSlot, self.debugging
        )
        self.threads.append(MapTh)

