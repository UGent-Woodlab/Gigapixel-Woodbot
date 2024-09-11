#
# Created on Tue Sep 15 2023
#
# The MIT License (MIT)
# Copyright (c) 2023 Simon Vansuyt UGent-Woodlab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import asyncio
import websockets
import time
import json
from pygcode import *
import pandas as pd

class CNC():
    '''
    A class to interact with a CNC machine using websockets.

    Attributes:
        CNC_URI (str): the URI of the CNC machine
        ws (websockets.client.WebSocketClientProtocol): the websocket connection to the CNC machine
        loop (asyncio.AbstractEventLoop): the event loop used for asynchronous operations
        position (list): the current position of the CNC machine
        h_pos (pandas.DataFrame): a dataframe to keep a history of positions
    
    Methods:
        __init__(self, CNC_URI): initializes a new instance of the CNC class
        __del__(self): deconstructs the websocket connection
        __async__disconnect(self): closes the websocket connection
        __async__connect(self): connects to the CNC machine using a websocket
        add_position_to_history(self, pos, timestamp): adds a position and timestamp to the position history dataframe
        __async__run_gcode(self, gcode): sends GCode to the CNC machine and waits for a response
        __async__fetch_position(self): fetches the current position of the CNC machine
        run_gcode(self, gcode): runs GCode on the CNC machine
        move(self, X=0, Y=0, Z=0): moves the CNC machine to a specified location
        fetch_position(self): fetches the current position of the CNC machine and adds it to the position history dataframe
    '''
    def __init__(self, CNC_URI, CNC_MAX_DIM, CNC_MAX_F):
        '''
        Initializes a new instance of the CNC class.

        Arguments:
             CNC_URI (str): the URI of the CNC machine
        '''
        self.CNC_URI = CNC_URI

        self.ws = None
        self.loop = asyncio.get_event_loop()
        # perform a synchronous connect
        self.loop.run_until_complete(self.__async__connect())
        self.position = None

        # keep a history of positions
        self.h_pos = pd.DataFrame(columns=["x", "y", "z", "time"])
        self.h_pos = self.h_pos.astype(dtype={
            'x': 'float64',
            'y': 'float64',
            'z': 'float64',
            'time': 'float64'
        })
        
        self.max_F = CNC_MAX_F
        self.F = CNC_MAX_F

        self.x_max = CNC_MAX_DIM[0]
        self.y_max = CNC_MAX_DIM[1]
        self.z_max = CNC_MAX_DIM[2]

    def __del__(self):
        """
        Deconstructor -> Closes the websocket connection.
        """
        del self.h_pos
        return self.loop.run_until_complete(self.__async__disconnect())

    def reset_history(self):
        del self.h_pos
        self.h_pos = pd.DataFrame(columns=["x", "y", "z", "time"])
        self.h_pos = self.h_pos.astype(dtype={
            'x': 'float64',
            'y': 'float64',
            'z': 'float64',
            'time': 'float64'
        })

    async def __async__disconnect(self):
        """
        Closes the websocket connection.
        """
        return await self.ws.close()

    async def __async__connect(self):
        """
        Connects to the CNC machine using a websocket.
        """

        print(f"Attempting connection to {self.CNC_URI} ...")
        self.ws = await websockets.connect(self.CNC_URI, ping_timeout=None)
        status = await self.ws.recv()
        print("status: ", status, "-> connection established")

        cnc_connect_data = {'status': 'connect'}
        await self.ws.send(json.dumps(cnc_connect_data))
        status = await self.ws.recv()
        print("status CNC: ", status, "-> connection established")

    def add_position_to_history(self, pos, timestamp):
        """
        Adds a position and timestamp to the position history dataframe.

        Arguments:
            pos (list): the position to add
            timestamp (float): the timestamp to add
        """
        self.h_pos.loc[len(self.h_pos)] = [pos[0], pos[1], pos[2], timestamp]

    async def __async__run_gcode(self, gcode):
        '''
        Sends G-code to the CNC and waits for the CNC to finish executing it.
        Records the CNC's position after every movement and stores it in the position history.

        Args:
            gcode (str): G-code command to send to the CNC.

        Returns:
            str: The current position of the CNC as a string, formatted as "X Y Z".
        '''
        data = {'status': 'gcode', 'gcode': gcode}
        await self.ws.send(json.dumps(data))
        print(f">>> {gcode}")

        current_data = json.loads((await self.ws.recv()).decode("utf-8"))
        t1 = current_data["timestamp"]

        # Wait for the CNC to finish executing the G-code
        while current_data["state"] != 1:
            current_data = json.loads((await self.ws.recv()).decode("utf-8"))
            self.position = [float(pos) for pos in current_data["cords"].split(" ")]
            self.add_position_to_history(self.position, current_data["timestamp"])
        print(f"<<< {current_data}")

        t2 = current_data["timestamp"]

        # Record the final position of the CNC after executing the G-code
        self.position = [float(pos) for pos in current_data["cords"].split(" ")]
        self.add_position_to_history(self.position, current_data["timestamp"])
        return current_data["cords"], t1, t2

    async def __async__fetch_position(self):
        '''
        Sends a request to the CNC machine to return its current position.

        Returns:
            str: The current position of the machine in string format.
        '''
        await self.ws.send("{'status': 'pos'}")
        current_data = json.loads((await self.ws.recv()).decode("utf-8"))
        self.position = [float(pos) for pos in current_data["cords"].split(" ")]
        self.add_position_to_history(self.position, current_data["timestamp"])
        return current_data["cords"]

    def run_gcode(self, gcode):
        '''
        same as __async__run_gcode but then sync
        '''
        return self.loop.run_until_complete(self.__async__run_gcode(gcode))

    def fetch_position(self):
        '''
        same as __async__fetch_position but then sync
        '''
        return self.loop.run_until_complete(self.__async__fetch_position())

    def move(self, X=0, Y=0, Z=0):
        '''
        Send a gcode command to cnc to move the machine to (X, Y, Z)

        Arguments:
            X (float) : x-coordinate
            Y (float) : y-coordinate
            Z (float) : z-coordinate

        Returns:
            str: Returns current position of the macine in string format.
        '''
        # don't send coords that are out of bound
        if X < 0: 
            X = 0
        elif X > self.x_max:
            X = self.x_max

        if Y < 0:
            Y = 0
        elif Y > self.y_max:
            Y = self.y_max
        
        if Z < 0:
            Z = 0
        elif Z > self.z_max:
            Z = self.z_max

        return self.run_gcode("G1 X%.2f Y%.2f Z%.2f F%.2f" % (X, Y, Z, self.F))
    
    def set_speed(self, p):
        self.F = self.max_F * p / 100

def main():
    CNC_URI = "ws://127.0.0.1:8765"
    cnc = CNC(CNC_URI)

    time.sleep(10)
    cnc.run_gcode("G0 X100 Y100 Z10")
    print("Wait 3 seconds and then move cnc back home ...")
    time.sleep(3)
    cnc.run_gcode("G0 X0 Y0 Z0")

if __name__ == "__main__":
    main()
