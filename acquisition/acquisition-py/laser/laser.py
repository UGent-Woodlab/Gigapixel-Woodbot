import struct
import socket
import os
from collections import namedtuple
import time
import threading
import pandas as pd

# link to pdf -> https://www.baumer.com/medias/__secure__/en_BA_OM70_Eth_point_line.pdf?mediaPK=8988407726110

class Laser:
    '''
    A class setups and fetchs measurements from the laser sensor.

    Attributes:
        LASER_IP (str): IP address of the laser sensor.
        UDP_PORT (int): Port number of the laser sensor.
        s (socket): Socket object used for UDP communication.
        m (namedtuple): Latest measurement from the sensor.
        h_measure (DataFrame): DataFrame containing historical measurement data.
        thread (Thread): Thread object used for asynchronous data acquisition.
        stop_thread (bool): Boolean value used to stop the thread.

    Methods:
        __init__(self, LASER_IP, UDP_PORT): Initializes a Laser object.
        __del__(self): Destructor method that stops the thread.
        connect(self): Checks if the sensor is available and returns the status as a boolean.
        add_point_history(self, d, timestamp): Adds a measurement point to the historical data.
        get_measure(self): Updates the latest measurement attribute.
    '''

    # see pdf -> page 74
    Measure = namedtuple('Measure','BlockID FrameType Reserve NumFrame Quality SwOut AlarmOut Dist MeasRate ExpRes RDsec RDus TSsec TSus')

    def __init__(self, LASER_IP, UDP_PORT):
        '''
        Initializes a Laser object.

        Arguments:
            LASER_IP (str): IP address of the laser sensor.
            UDP_PORT (int): Port number of the laser sensor.

        '''
        #config
        self.LASER_IP = LASER_IP
        self.UDP_PORT = UDP_PORT

        # setup socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(0.0005)
        # self.s.setsockopt(socket.SOL_SOCKET, SO_TIMESTAMPS, 1)
        self.connect()
        self.m = None
        self.last_update = 0
        self.h_measure = pd.DataFrame(columns=['d', 'time'])
        self.h_measure = self.h_measure.astype(dtype={'d': 'float64', 'time': 'float64'})
        # create a thread that updates m when a new UDP package is read
        self.thread_measure = threading.Thread(target=self.get_measure)
        self.thread_measure.daemon = True
        self.thread_history = threading.Thread(target=self.add_latest_point)
        self.thread_history.daemon = True
        self.stop_thread = False
        self.thread_measure.start()
        self.thread_history.start()

    def __del__(self):
        '''
        Destructor method that stops the thread.
        '''
        self.stop_thread = True
        del self.h_measure

        self.s.close()
        del self.s

    def connect(self):
        '''
        This function checks if the sensor is available and returns the status as boolean

        Returns:
            boolean: true if sensor is available, else false
        '''
        # First check if LOCAL IP is available
        if(os.system("ping -c 1 " + self.LASER_IP) >= 0):
            # try connection
            return self.s.bind((self.LASER_IP, self.UDP_PORT))
        return False

    def add_point_history(self, d, timestamp):
        '''
        The function adds a history point to dataframe

        Arguments:
            d: a float measured distance of the sensor
            timestamp: the corresponding d measurement, also float

        Returns:
            None
        '''
        self.h_measure.loc[len(self.h_measure)] = [d, timestamp]

    def get_measure(self):
        '''
        The function updates the class measure attribute
        '''
        while not self.stop_thread:
            try:
                t1 = time.time()
                data = self.s.recv(40) # framelength is 40 bytes
                t2 = time.time()
                self.m = self.Measure._make(struct.unpack_from('<IBBHB??xfffIIII', data))
                self.last_update = (t1+t2)/2
            except socket.timeout:
                pass
                # self.connect()

    def add_latest_point(self):
        while not self.stop_thread:
            try:
                self.add_point_history(self.m.Dist, self.last_update)
            except:
                continue
    
    def reset_history(self):
        del self.h_measure
        self.h_measure = pd.DataFrame(columns=['d', 'time'])
        self.h_measure = self.h_measure.astype(dtype={'d': 'float64', 'time': 'float64'})

def main():
    # hardcoded variables
    LASER_IP = "192.168.1.104"
    UDP_PORT = 8888

    l = Laser(LASER_IP, UDP_PORT)

    time.sleep(2)

    while l.m is not None:
        print(f"Dist: {l.m.Dist:.2f}, Quality: {l.m.Quality}, Measurement rate: {l.m.MeasRate}")
        time.sleep(1)

if __name__ == "__main__":
    main()
