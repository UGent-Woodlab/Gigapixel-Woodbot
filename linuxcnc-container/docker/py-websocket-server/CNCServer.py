from simple_websocket_server import WebSocketServer, WebSocket
import sys
import linuxcnc
import time
from datetime import datetime
import threading
import os
import json
import re
import signal

class CNCServer(WebSocket):

    def handle(self):
        '''
        This function handles a incoming message
        -> Try to execute the message as gcode
        -> sends back the coordinates of the cnc
        '''
        self.thread = threading.Thread(target=self.handle_in_thread, args=(self.data, ))
        self.thread.start()

    def handle_in_thread(self, data):
        print(data)
        json_data = json.loads(data)
        print(json_data)
        if json_data["status"] == "connect":
            self.start_connection_with_cnc()
        elif json_data["status"] == "gcode":
            self.execute_g_code(json_data["gcode"])
        else:
            # json_data["status"] == "pos":
            self.send_cords_with_timestamp()

    def connected(self):
        # check if machine is already started
        print(self.address, 'connected')
        self.send_message("OK")

    def start_connection_with_cnc(self):
        # print out the current status of machine
        self.show_cnc_status()
        s.poll()
        if self.ok_for_mdi():
            c.mode(linuxcnc.MODE_MDI)
            c.wait_complete() # wait until mode switch executed
            self.send_message("CNC OK")

    def handle_close(self):
        c.mdi("G0 X0 Y0 Z0")
        print("connection closed with: " + self.address[0])
        self.send_message(self.address[0] + u' - disconnected')

    def set_home(self):
        '''
        Set current position as home position
        '''
        for i in range(3):
            c.home(i)
            self.wait_complete()
            print("homed axis %d" % i)
        if s.homed[0:3] == (1, 1, 1):
            print("Axis are homed")
        else:
            print("Something went wrong machine didn't home")

    def ok_for_mdi(self):
        '''
        Returns:
            Boolean that is true if cnc is ready for mdi else false
        '''
        s.poll()
        return not s.estop and s.enabled and (s.homed.count(1) == s.joints) and (s.interp_state == linuxcnc.INTERP_IDLE)

    def get_position(self):
        '''
        Returns:
            tuple of floats containing the coordinates of the current position of the machine
        '''
        s.poll()
        return s.actual_position

    def show_cnc_status(self):
        '''
        function prints out status information of the machine
        '''
        print(s.poll())
        print("")
        print("etsop:			", not s.estop)
        print("connection:		", s.enabled)
        print("s.homed.count(1):	", s.homed.count(1))
        print("s.joints:		", s.joints)
        print("s.interp_state		", s.interp_state)
        print("linuxcnc.INTERP_IDLE	", linuxcnc.INTERP_IDLE)
        print(self.get_position())

    def execute_g_code(self, gcode):
        '''
        This function takes a string and tries to execute it as gcode
        '''
        if self.ok_for_mdi():
            a = c.mdi(gcode)

            print("[ EXEC ] " + gcode + ", " + str(a))
            print(re.findall(r'[-]?[\d]+(\.\d+)?', gcode))
            re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", gcode)
            gcode_numbers = [float(x) for x in re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", gcode)]

            print(gcode_numbers)
            if gcode_numbers[0] == 0 or gcode_numbers[0] == 1:
                # gcode G0 or G1 -> send cords

                self.wait_complete([round(gcode_numbers[1], 2), round(gcode_numbers[2], 2), round(gcode_numbers[3], 2)]) # problem what if only 1 or 2 axis are passed through
            else:
                print("NOT A G0 COMMAND stall")
                c.wait_complete()

    def send_cords_with_timestamp(self, cords):
        s.poll()
        timestamp1 = time.time()
        pos = self.get_position()[0:3]
        timestamp2 = time.time()

        last_state = 1 if (self.ok_for_mdi() and
                      round(pos[0], 2) == cords[0] and
                      round(pos[1], 2) == cords[1] and
                      round(pos[2], 2) == cords[2]) else 2

        json_data = '{' + \
                ('"cords": "%.2f %.2f %.2f", ' % pos) + \
                ('"timestamp": %.4f, ' % ((timestamp1 + timestamp2)/2)) + \
                ('"state": %d' % last_state) + \
            '}'

        self.send_message(json_data)
        print("SENDING >>> " + json_data)
        return last_state

    def wait_complete(self, cords, delay=0.005):
        # state = 1 -> cnc running done MDI is ready
        #       = 2 -> cnc is running
        last_state = 2 # send with state 1 so client knows operation is finished
        while last_state == 2:
            c.wait_complete(delay)
            last_state = self.send_cords_with_timestamp(cords)

    def handler_stop_signal(self, signum, frame):
        c.mdi("G0 X0 Y0 Z0")
        c.wait_complete()
        print(signum, frame, "Exiting")
        # request.environ.get('werkzeug.server.shutdown')
    
    def serve_forever(self):
        signal.signal(signal.SIGINT, self.handler_stop_signal)
        signal.signal(signal.SIGTERM, self.handler_stop_signal)

        WebSocket.serve_forever()

def connect_to_cnc():
    print("try connectiong to cnc")
    try:
        s = linuxcnc.stat() # create a connection to the status channel
        s.poll() # get current values
        c = linuxcnc.command()
        c.state(linuxcnc.STATE_ESTOP_RESET)
        c.state(linuxcnc.STATE_ON)
        # auto home machine
        c.home(-1)
        c.wait_complete()
        return s, c

    except linuxcnc.error, detail:
        print("error", detail)
        sys.exit(1)


if __name__ == '__main__':
    s, c = connect_to_cnc()

    server = WebSocketServer('127.0.0.1', 8765, CNCServer)
    server.serve_forever()
