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

from flask import Flask
from flask import request
from flask import send_file
from flask import Response
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image, ImageDraw

import sys
import threading
import queue
import json
from datetime import datetime

import signal

from acquisition import Acquisition
from calibration import Calibration

# move machine home
config_path = './config.json'
gui_config_path = "/image-document-store/db/.gui_config"
state = False

print("Start acquisition and REST server")
acq = Acquisition(config_path)
cali = Calibration(acq)

app = Flask('acquisition', static_folder="/image-document-store/db/.gui_config/")
CORS(app)

acq.cnc.move(0, 0, 0)

def handle_stop(signal, frame):
    acq.cnc.move(0,0,0)
    print("move cnc home")
    del acq

signal.signal(signal.SIGINT, handle_stop)
signal.signal(signal.SIGTERM, handle_stop)

export_jobs = []

# start app
def request_response():
    return app.response_class(
        response=json.dumps({
            "buzy": state,
            "x": acq.cnc.position[0], 
            "y": acq.cnc.position[1], 
            "z": acq.cnc.position[2], 
            "d": f"{acq.laser.m.Dist:.2f}", #  acq.laser.last_update,
            "speed": acq.cnc.F,
            "speed_p": acq.cnc.F/acq.cnc.max_F * 100,
            "camera_name": acq.camera_config["CAMERA_NAME"]
        }),
        status=200,
        mimetype='application/json'
    )

# rest calls
@app.route("/", methods=['get'])
def get_status():
    return request_response()

# MOVE CNC MACHINE
@app.route("/cnc/move", methods=['GET'])
def move_cnc():
    # fetch position parameters
    if acq.cnc.position is not None:
        x = request.args.get('x', acq.cnc.position[0])
        y = request.args.get('y', acq.cnc.position[1])
        z = request.args.get('z', acq.cnc.position[2])
    else:
        x = request.args.get('x', 0)
        y = request.args.get('y', 0)
        z = request.args.get('z', 0)
    
    print(x, y, z)

    # move the machine to the correct place
    # check if values do not exceed the maximum or minimum
    acq.cnc.move(float(x), float(y), float(z))

    # create a response
    return request_response()

@app.route("/cnc/move_relative", methods=['get'])
def move_relative_cnc():
    # fetch position parameters
    x = request.args.get('x', 0)
    y = request.args.get('y', 0)
    z = request.args.get('z', 0)

    # move the machine to the correct place
    # check if values do not exceed the maximum or minimum
    acq.cnc.move(
        acq.cnc.position[0] + float(x),
        acq.cnc.position[1] + float(y),
        acq.cnc.position[2] + float(z)
    )

    return request_response()

# SET CNC SPEED
@app.route("/cnc/set_speed", methods=['get'])
def set_speed():
    # fetch position parameters
    p = int(request.args.get('p', 0))
    acq.cnc.set_speed(p)
    return request_response()

# CNC SEND GCODE
@app.route("/cnc/gcode", methods=['get'])
def send_gcode_cnc():
    gcode = request.args.get('gcode', '')
    acq.cnc.run_gcode(gcode)
    return request_response()

# Camera 

# a function to change camera
@app.route("/camera/update_current", methods=['get'])
def take_current_view():
    file_name_tiff = f"{gui_config_path}/latest.tiff"
    file_name_jpg = f"{gui_config_path}/latest_1024.jpg"
    acq.camera.take_picture(file_name_tiff)

    img = cv2.imread(file_name_tiff)
    res = cv2.resize(img, dsize=(1024, int(img.shape[0]/img.shape[1]*1024)), interpolation=cv2.INTER_CUBIC)
    img = cv2.imwrite(file_name_jpg, res)

    # return send_file(file_name, mimetype='image/jpg')
    return request_response()

@app.route("/camera/current_view.jpg")
def get_current_view():
    file_name = f"{gui_config_path}/latest_1024.jpg"
    return send_file(file_name, mimetype='image/jpg')

@app.route("/camera/view.tiff")
def download_view():
    file_name = f"{gui_config_path}/latest.tiff"
    return send_file(file_name, mimetype='image/tiff')

@app.route("/laser/camera_to_laser")
def camera_to_laser():
    acq.cnc.move(
        acq.cnc.position[0] - acq.camera_config["SPACES"]["LASER_TO_CAMERA_X"],
        acq.cnc.position[1] - acq.camera_config["SPACES"]["LASER_TO_CAMERA_Y"],
        acq.cnc.position[2] + (acq.laser.m.Dist if isinstance(acq.laser.m.Dist, type(0.1)) else acq.camera_config["CAMERA_FOCUS"]) - acq.camera_config["CAMERA_FOCUS"]
    )
    return request_response()

# acquisition
@app.route("/acquisition/base_scan", methods=["get"])
def generate_base_scan():
    p = float(request.args.get("percentage", 100))/100
    z = float(request.args.get("z_height", 40))
    step = float(request.args.get("step_size", 50))

    acq.scan_height_lineair((0,0), (acq.cnc.x_max * p, acq.cnc.y_max), step=step, z=z)
    acq.hmap.plot_base_scan(f"{gui_config_path}/base_scan/")
    return request_response()

@app.route("/acquisition/base_scan.png", methods=["get"])
def get_base_scan():
    file_name = f"{gui_config_path}/base_scan/base_scan.png"
    return send_file(file_name, mimetype='image/png')

#### Acquistion jobs

# Create a queue to hold incoming tasks
task_queue = queue.Queue()
current_task = {}

# maximum threshold to prevent hitting the sample
max_threshold = acq.camera_config["CAMERA_FOCUS"] * 0.9

def start_job(task):
    if task['type'] == 'drill_sample':
        acq.scan_drill_sample(
            (task["x_cord1"], task["y_cord1"]),
            (task["x_cord2"], task["y_cord2"]),
            names=task["names"],
            date=task["date"],
            step_cord_x = acq.camera_config["CAMERA_WIDTH_CORRECTION"]*(1-task["picture_overlap"]/100),
            step_cord_y = acq.camera_config["CAMERA_HEIGHT_CORRECTION"]*(1-task["picture_overlap"]/100),
            z=task["height_z"],
            amount=task["amount"],
        )
    elif task['type'] == 'object_fixed':
        acq.scan_surface_fixed(
            (task["x_cord1"], task["y_cord1"]),
            (task["x_cord2"], task["y_cord2"]),
            name=task["name"],
            date=task["date"],
            step_cord_x = acq.camera_config["CAMERA_WIDTH_CORRECTION"]*(1-task["picture_overlap"]/100),
            step_cord_y = acq.camera_config["CAMERA_HEIGHT_CORRECTION"]*(1-task["picture_overlap"]/100),
            z=task["z_start"],
            amount=task["z_amount"],
            step=task["z_step"],
        )
    else:
        acq.scan_surface(
            (task["x_cord1"], task["y_cord1"]),
            (task["x_cord2"], task["y_cord2"]),
            name=task["name"],
            date=task["date"],
            step_cord_x = acq.camera_config["CAMERA_WIDTH_CORRECTION"]*(1-task["picture_overlap"]/100),
            step_cord_y = acq.camera_config["CAMERA_HEIGHT_CORRECTION"]*(1-task["picture_overlap"]/100),
            step_height = task["height_step"],
            z = task["height_z"],
            margin = task["margin"],
            threshold = task["height_threshold"] if task["height_threshold"] < max_threshold else max_threshold  # safety for head not bumb into object
        )

def acquistion_worker():
    global state
    global current_task
    # run jobs until there not empty
    state = True

    while not task_queue.empty():
        task = task_queue.get()
        print("starting", task)
        date = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        task["date"] = date
        current_task = task
        start_job(task)

        task_queue.task_done()
    
    current_task = {}
    state = False

# have a working thread to handle the acquisition tasks
worker_thread = threading.Thread(target=acquistion_worker)
worker_thread.daemon = True

@app.route("/acquisition/object", methods=["get"])
def add_job_object():
    global worker_thread

    x_cord1 = float(request.args.get("x_cord1", 0))
    y_cord1 = float(request.args.get("y_cord1", 0))
    x_cord2 = float(request.args.get("x_cord2", 0))
    y_cord2 = float(request.args.get("y_cord2", 0))

    name = request.args.get("name", "test123")
    height_z = request.args.get("height_z", 50, type=float)
    height_step = request.args.get("height_step", 2, type=float)
    height_threshold = request.args.get("height_</br>threshold", 5, type=float)
    picture_overlap = request.args.get("picture_overlap", 10, type=float)
    margin = request.args.get("margin", 2, type=float)
    
    to_export = request.args.get("to_export", default=False, type=lambda b: b.lower() == 'true')

    print(to_export)

    acquisition_task = {
        "type": "object",
        "x_cord1": x_cord1,
        "y_cord1": y_cord1,
        "x_cord2": x_cord2,
        "y_cord2": y_cord2,
        "name": name,
        "date": "wait to start",
        "height_z": height_z,
        "height_step": height_step,
        "height_threshold": height_threshold,
        "picture_overlap": picture_overlap,
        "margin": margin,
    }

    # send to export object or to queue
    if to_export:
        # append to job to export object
        export_jobs.append(acquisition_task)
    else:
        # add job to queue
        task_queue.put(acquisition_task)

    # check if worker thread is already running
    if not worker_thread.is_alive():
        # reset the thread
        worker_thread = threading.Thread(target=acquistion_worker)
        worker_thread.daemon = True
        worker_thread.start()

    return request_response()

@app.route("/acquisition/drill_sample", methods=["get"])
def add_job_drill():
    global worker_thread

    x_cord1 = float(request.args.get("x_cord1", 0))
    y_cord1 = float(request.args.get("y_cord1", 0))
    x_cord2 = float(request.args.get("x_cord2", 0))
    y_cord2 = float(request.args.get("y_cord2", 0))

    amount = int(request.args.get("amount", 5))
    name = request.args.get("name", "Namless", str)
    height_z = float(request.args.get("height_z", 50))
    picture_overlap = float(request.args.get("picture_overlap", 10))

    to_export = request.args.get("to_export", default=False, type=lambda b: b.lower() == 'true')

    acquisition_task = {
        "type": "drill_sample",
        "x_cord1": x_cord1,
        "y_cord1": y_cord1,
        "x_cord2": x_cord2,
        "y_cord2": y_cord2,
        "names": list(name.split(",")),
        "height_z": height_z,
        "amount": amount,
        "picture_overlap": picture_overlap,
        "date": "wait to start",
        "name": name,
    }

    # send to export object or to queue
    if to_export:
        # append to job to export object
        export_jobs.append(acquisition_task)
    else:
        # add job to queue
        task_queue.put(acquisition_task)

    # check if worker thread is already running
    if not worker_thread.is_alive():
        # reset the thread
        worker_thread = threading.Thread(target=acquistion_worker)
        worker_thread.daemon = True
        worker_thread.start()

    return request_response()

@app.route("/acquisition/object_fixed", methods=["get"])
def add_job_object_fixed():
    global worker_thread

    x_cord1 = float(request.args.get("x_cord1", 0))
    y_cord1 = float(request.args.get("y_cord1", 0))
    x_cord2 = float(request.args.get("x_cord2", 0))
    y_cord2 = float(request.args.get("y_cord2", 0))

    name = request.args.get("name", "test123", type=str)
    z_start = request.args.get("z_start", 0, type=float)
    z_amount = request.args.get("z_amount", 1, type=int)
    z_step = request.args.get("z_step", acq.camera_config["CAMERA_DOF"], type=float)
    picture_overlap = request.args.get("picture_overlap", 10, type=float)

    to_export = request.args.get("to_export", default=False, type=lambda b: b.lower() == 'true')

    acquisition_task = {
        "type": "object_fixed",
        "x_cord1": x_cord1,
        "y_cord1": y_cord1,
        "x_cord2": x_cord2,
        "y_cord2": y_cord2,
        "name": name,
        "date": "wait to start",
        "z_start": z_start,
        "z_amount": z_amount,
        "z_step": z_step,
        "picture_overlap": picture_overlap,
    }

    # send to export object or to queue
    if to_export:
        # append to job to export object
        export_jobs.append(acquisition_task)
    else:
        # add job to queue
        task_queue.put(acquisition_task)

    # check if worker thread is already running
    if not worker_thread.is_alive():
        # reset the thread
        worker_thread = threading.Thread(target=acquistion_worker)
        worker_thread.daemon = True
        worker_thread.start()

    return request_response()

@app.route("/acquisition/acquisition_queue", methods=["get"])
def show_queue():
    return {
        "current_task": current_task,
        "queue": list(task_queue.queue),
        "thread_is_active": worker_thread.is_alive()
    }

@app.route('/acquisition/import_from_file', methods=["get"])
def import_from_file():
    global worker_thread

    body = json.loads(request.args.get("body", "[]"))
    print(body)

    for acquisition_task in body:
        # add current date to the system
        acquisition_task["date"] = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

        # put task to the queue
        task_queue.put(acquisition_task)

    # check if worker thread is already running
    if not worker_thread.is_alive():
        # reset the thread
        worker_thread = threading.Thread(target=acquistion_worker)
        worker_thread.daemon = True
        worker_thread.start()

    return request_response()

@app.route('/acquisition/remove_item_from_export', methods=['get'])
def remove_item_from_export():
    name = request.args.get("name", "test123", type=str)

    for i in range(len(export_jobs)):
        if export_jobs[i]['name'] == name:
            del export_jobs[i]
            break
    
    return request_response()

@app.route('/acquisition/export_job_file', methods=["get"])
def export_job_file():
    return export_jobs

# Calibration
@app.route("/calibration/get_current_setting", methods=["get"])
def current_setting():
    print(acq.config)
    return app.response_class(
        response=json.dumps({
            "x": acq.camera_config["SPACES"]["LASER_TO_CAMERA_X"], 
            "y": acq.camera_config["SPACES"]["LASER_TO_CAMERA_Y"], 
            "z": acq.camera_config["CAMERA_FOCUS"], 
            "camera_name": acq.camera_config["CAMERA_NAME"],
        }),
        status=200,
        mimetype='application/json'
    )

@app.route("/calibration/update_settings", methods=["get"])
def update_settings():
    global acq

    x = request.args.get("laser_to_camera_x", None)
    print(x, x is not None)
    if x is not None:
        acq.camera_config["SPACES"]["LASER_TO_CAMERA_X"] = round(float(x), 3)

    y = request.args.get("laser_to_camera_y", None)
    if y is not None:
        acq.camera_config["SPACES"]["LASER_TO_CAMERA_Y"] = round(float(y), 3)

    z = request.args.get("laser_to_camera_z", None)
    if z is not None:
        acq.camera_config["CAMERA_FOCUS"] = round(float(z), 3)

    # Overwrite the JSON file with the Python object
    acq.update_config(config_path)

    return request_response()

@app.route("/calibration/manual_xy", methods=["get"])
def manual_xy():
    global state
    x = float(request.args.get("x", 0))
    y = float(request.args.get("y", 0))
    z = float(acq.laser.m.Dist if isinstance(acq.laser.m.Dist, type(0.1)) else acq.camera_config["CAMERA_FOCUS"]) - acq.camera_config["CAMERA_FOCUS"]

    result = cali.manual_xy(x, y, z, gui_config_path)

    state = False
    return app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )

@app.route("/calibration/manual_xy_picture.png", methods=["get"])
def manul_xy_picture():
    file_name_png = f"{gui_config_path}/calibration/manual_xy.png"
    return send_file(file_name_png, mimetype='image/png')

@app.route("/calibration/take_z_stack", methods=["get"])
def take_z_stack():
    global state
    state = True

    z_start = float(request.args.get("z_start", 0))
    step = float(request.args.get("step", 0))
    amount = int(request.args.get("amount", 0))

    path = gui_config_path + "/z_stack/"

    result = cali.take_z_stack(z_start, step, amount, path)

    state = False
    print("result array is:", result, file=sys.stdout)
    return Response(json.dumps(result),  mimetype='application/json')

@app.route('/calibration/get_stack_by_index', methods=["get"])
def get_index_stack():
    file_name = str(request.args.get("file_name"))
    file_name = f"{gui_config_path}/z_stack/{file_name}"
    return send_file(file_name, mimetype='image/png')