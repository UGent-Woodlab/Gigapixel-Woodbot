#!/bin/bash
# enable the pcie bus
echo 1 | sudo tee -a /sys/bus/pci/devices/0000:82:00.2/enable
# start linuxcnc
linuxcnc /mill-configs/my-mill.ini &
sleep 5 # change to idle loop that check's if machine is ready
# start WebSocket server
echo "START WEBSOCKET SERVER"
python2 /server/CNCServer.py 2>&1