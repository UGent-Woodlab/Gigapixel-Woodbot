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

from flask import Flask, request, send_file
import os 
import threading
import queue

app = Flask('focus-stack')
thread_count = 4 # set the number of workers to use

# Create a queue to hold incoming tasks
task_queue = queue.Queue()

# Create a list to hold running threads and their statuses
threads = {}
finished_jobs = []

# Define a function that executes the focus-stack command
def execute_focus_stack():
    threads[threading.current_thread().ident] = []
    while True:
        if not task_queue.empty():
            # Get the next task from the queue
            task = task_queue.get()
            threads[threading.current_thread().ident].append({"status": "running", "task": task})

            print(threads[threading.current_thread().ident])

            # Extract the output and image values from the task
            output = task["output"]
            images = task["images"]

            # Execute the focus-stack command
            i = os.system(
                f"focus-stack \
                    --verbose \
                    --align-keep-size \
                    --full-resolution-align \
                    --no-contrast \
                    --no-whitebalance \
                    --output={output} \
                    {' '.join(images)}"
            )

            # other settings that can be used
            # --depthmap={output.rstrip('.tiff')}_depthmap.png \
            # --3dview={output.rstrip('.tiff')}_3dview.png \

            # Mark the task as complete
            task_queue.task_done()
            finished_jobs.append(task["id"])
            threads[threading.current_thread().ident][-1]["status"] = ("finnished" if i == 0 else "failed")

@app.route("/focus_stack", methods=['POST'])
def focus_stack():
    """
    Start Extended Focus Imaging (EFI) for a set of images.
    return: string with the id of the task
    """

    uid = request.form.get('id', int(id(request.form)))
    output = request.form.get("output")
    images = request.form.getlist("images")

    # Create a new task and add it to the queue
    task = {"id": uid, "output": output, "images": images}
    task_queue.put(task)

    return str(uid)

@app.route("/threads", methods=['GET'])
def list_threads():
    """
    Give a list of alle the threads and their status
    """
    return {"threads": threads, "finished_jobs": finished_jobs}

# Start the worker threads
for i in range(thread_count):
    thread = threading.Thread(target=execute_focus_stack)
    thread.daemon = True
    thread.start()

app.run(host="127.0.0.1", port=5003)
