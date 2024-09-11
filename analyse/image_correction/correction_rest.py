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

from flask import Flask, request, send_file, jsonify
import queue
import os 
import uuid
import threading
import json
from correction import FlatFieldCorrection 

app = Flask('correction')
thread_count = 4 # set the number of workers to use

# Create a queue to hold incoming tasks
task_queue = queue.Queue()

# Create a list to hold running threads and their statuses
threads = {}  # dict to store running threads and their statuses
finished_jobs = []

# check if the folder /db/flatfields/ exists and contains image files with extension .tiff
# if not, create the folder and download the flatfield images from the server

# Settings for ...
settings = {
    "Teledyne DALSA Nano XL": {
        "flat_field_path": "/image-document-store/flatfields/Teledyne",
        "crop_enable": True,
        "original_dim_x": 4096,
        "original_dim_y": 4096,
        "crop_dim_x": 3380,
        "crop_dim_y": 3380,
    },
    "Canon EOS 6D": {
        "flat_field_path": "/image-document-store/flatfields/Canon",
        "crop_enable": False,
        "original_dim_x": 5472,
        "original_dim_y": 3648,
        "crop_dim_x": 5472,
        "crop_dim_y": 3648,
    }
}

correction = {}
for camera, setting in settings.items():
    correction[camera] = FlatFieldCorrection(setting)

lock = threading.Lock()

def execute_image_correction():
    """
    Execute image correction tasks in a thread.

    This function continuously checks the task_queue for image correction tasks and processes them.
    """
    global lock
    threads[threading.current_thread().ident] = []
    while True:
        if not task_queue.empty():
            # Get the next task from the queue
            task = task_queue.get()
            threads[threading.current_thread().ident].append({"status": "running", "task": task})

            print(threads[threading.current_thread().ident])

            # Extract the output and image values from the task
            camera = task["camera"]
            path_input = task["path_input"]
            path_output = task["path_output"]

            # Execute the focus-stack command
            # print(task)
            lock.acquire()
            correction[camera].correct_one_image(path_input, path_output)

            # Mark the task as complete
            task_queue.task_done()
            finished_jobs.append(task["id"])
            threads[threading.current_thread().ident][-1]["status"] = "finnished"
            lock.release()

@app.route("/correction", methods=['POST'])
def image_correction():
    """
    Start image correction tasks for a specified set of images.

    This function receives a set of images and schedules them for correction using a thread pool.

    Returns:
        dict: A JSON response containing the unique IDs of the scheduled correction tasks.
    """

    uid = request.form.get('id', int(id(request.form)))
    uids = []
    camera = request.form.get("camera")
    path_input = request.form.get("path_input")
    path_output = request.form.get("path_output")

    # Define the size of the 2D grid
    grid_size = (0, 0)  # Change this to match the actual size of your grid

    # fetch grid size
    for file_name in os.listdir(path_input):
        extension = file_name.split('.')[1]

        if extension == 'tiff':
            x, y = map(int, file_name.split('.')[0].split('_')[1:])
            if x+1 > grid_size[0]:
                grid_size = (x+1, grid_size[1])
            if y+1 > grid_size[1]:
                grid_size = (grid_size[0], y+1)


    for x in range(grid_size[0]):
        for y in range(grid_size[1]):
            input_image_path = os.path.join(path_input, f"stack_{x}_{y}.tiff")
            output_image_path = os.path.join(path_output, f"corrected_tile_{x}_{y}.tiff")

            if os.path.exists(input_image_path):
                # Create a new task and add it to the queue
                task_uid = str(uuid.uuid4())
                uids.append(task_uid)
                task = {"id": task_uid, "path_input": input_image_path, "path_output": output_image_path, "camera": camera}
                task_queue.put(task)
                print(f"INFO: Save corrected image {x} {y}, with uid={task_uid}")
            else: 
                print(f"INFO: Save black image {x} {y}")
                correction[camera].black_image.save(output_image_path)

    return jsonify(results = uids)

@app.route("/set_crop_settings", methods=['GET'])
def set_crop_settings():
    """
    Update crop settings for a specified camera.

    This function updates the crop settings for a camera based on the provided parameters.

    Returns:
        None
    """

    camera = request.form.get("camera", '', str)
    settings = {
        "flat_field_path": request.form.get('flat_field_path', '', str),
        "crop_enable": request.form.get('crop', False, bool),
        "original_dim_x": request.form.get('original_dim_x', 0, int),
        "original_dim_y": request.form.get('original_dim_y', 0, int),
        "crop_dim_x": request.form.get('crop_dim_x', 0, int),
        "crop_dim_y": request.form.get('crop_dim_y', 0, int),
    }

    correction[camera].reset(settings)


@app.route("/threads", methods=['GET'])
def list_threads():
    """
    Get a list of running threads and their statuses.

    Returns:
        dict: A JSON response containing information about running threads and finished jobs.
    """

    return {"threads": threads, "finished_jobs": finished_jobs}

# Start the worker threads
for i in range(thread_count):
    thread = threading.Thread(target=execute_image_correction)
    thread.daemon = True
    thread.start()

app.run(host="127.0.0.1", port=5004)
