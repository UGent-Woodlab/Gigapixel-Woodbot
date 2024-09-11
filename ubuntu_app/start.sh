#!/bin/bash
export UID=1000
export GID=1000
export TZ="Europe/Brussels"

# Hardcoded values
# Define the ip and port of the cnc pc
linuxcnc_pc_ip="192.168.2.106"
linuxcnc_pc_port="8765"

# Define the username and password of the CNC PC
LINUXCNC_USER="linuxcnc"
LINUXCNC_PASSWORD="woodlab"

# Define the function for starting CNC
function startCNC() {
    # Replace this with the actual command to start CNC
    echo "Starting CNC..."
    sshpass -p $LINUXCNC_PASSWORD ssh -X $LINUXCNC_USER@$LINUXCNC_PC_IP "killall linuxcnc || echo 'linuxcnc not active'  && killall python2|| echo 'python not active' && ./Desktop/linuxcnc-container/start-container.sh" >/dev/null & 

    while true; do
        nc -zvw1 $LINUXCNC_PC_IP $LINUXCNC_PC_PORT >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "Websocket is active: hello there"
            break
        else
            echo "Websocket is not active, retrying ... turn on the pc please?"
            sleep 1
        fi
    done
}

# Define the function for starting Woodbot
function startWoodbot() {
    # Replace this with the actual command to start Woodbot
    echo "Starting Woodbot..."

    # go to correct directory
    cd ~/SimonVansuyt

    # start firefox when system is active
    ./ubuntu_app/start_web_app.sh &

    # start up system
    docker compose up

    docker compose down
}

function restartWoodbot() {
    # Replace this with the actual command to start Woodbot
    echo "Restarting Woodbot..."
    echo "Shtting Woodbot..."
    # shut down system
    docker compose down
    startWoodbot
}

# Check if CNC is active
nc -zvw1 $LINUXCNC_PC_IP $LINUXCNC_PC_PORT >/dev/null 2>&1
if [ $? -ne 0 ]; then
    # Create a Zenity dialog with two buttons
    if zenity --question --text="First start CNC then start Gigapixel Woodbot:" \
        --ok-label="Start CNC" --cancel-label="Do not start"; then
        # User clicked "Start CNC"
        startCNC
        echo  "CNC is active, you can start the woodbot wait until homed..."

        if zenity --question --text="Wait until the CNC is homed then start the Gigapixel Woodbot by clicking 'Start Gigapixel Woodbot':" \
            --ok-label="Start Gigapixel Woodbt" --cancel-label="Do not start"; then
            # User clicked "Start Gigapixel Woodbot"
            startWoodbot
       fi
    fi
else
    if zenity --question --text="The CNC is already active do you want to restart the Gigapixel Woodbot:" \
        --ok-label="Restart Gigapixel Woodbt" --cancel-label="Do not restart"; then
        # User clicked "Start Gigapixel Woodbot"
        restartWoodbot
    fi
fi

echo "Closing ..."