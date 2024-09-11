#!/bin/bash

# install pip
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
python get-pip.py

# install server
pip install simple-websocket-server