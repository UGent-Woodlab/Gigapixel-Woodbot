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

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import threading
from analyse import Analyse
from db.store_to_image import images

# Define a static path for serving image files
static_path = "/image-document-store"

# Create a Flask app instance
app = Flask('analyse', static_folder="f{static_path}/db/.gui_config/")
CORS(app) # Enable Cross-Origin Resource Sharing (CORS) for the app
app.config['CORS_HEADERS'] = 'Content-Type'

analyse = Analyse("./config.json")

# start observation in thread
thread = threading.Thread(target=analyse.start_observation)
thread.daemon = True
thread.start()

# Define routes and their associated functions using decorators

# Route to start image analysis for a specific date
@app.route('/start_by_date', methods=['GET'])
def start_by_date():
    """
    Start analysis for a specified date.

    URL Parameters:
        date (str): The date for which analysis should be started.

    Returns:
        dict: A JSON response containing a message indicating the analysis start status.
    """
    date_str = request.args.get('date')
    analyse.start_by_date(date_str)
    return jsonify({'message': f'Analysis started for date {date_str}'})

@app.route('/images_meta', methods=['get'])
def fetch_images_metadata():
    """
    Fetch metadata of images stored in the database.

    Returns:
        dict: A JSON response containing image metadata.
    """
    images_meta = analyse.image_store.db.posts.find({})
    results = []
    for img in images_meta:
        image = images(img)

        results.append(
            {
                "name": image.name if hasattr(image, "name") else "Nameless job",
                "date": image.date,
                "camera": image.camera,
                "focus_stacked": image.focus_stacked if hasattr(image, "focus_stacked") else False,
                "correction": image.correction if hasattr(image, "correction") else False,
                "stitched": image.stitched if hasattr(image, "stitched") else False,
                "increment_x": image.increment_x,
                "increment_y": image.increment_y,
                "overlap": image.overlap if hasattr(image, "overlap") else "Undifined",
                "start_path": image.start_path,
                "start_x": image.start_x,
                "start_y": image.start_y,
                "blending": image.blending if hasattr(image, "blending") else "NONE",
            }
        )
    return jsonify(results)

@app.route('/images/heightmap.png', methods=['get'])
def fetch_height_map():
    """
    Fetch the heightmap image for a specified date.

    URL Parameters:
        date (str): The date for which the heightmap image should be retrieved.

    Returns:
        file: The heightmap image file.
    """
    date = request.args.get("date")
    new_images = analyse.image_store.find_images_by_date(date)
    filename = f"{new_images.start_path}/heightmap.png"
    if not os.path.exists(filename):
        filename = f"{analyse.dbpath}/.gui_config/heightmap/heightmap.png"
    return send_file(filename, mimetype='image/png')

@app.route("/restart_task", methods=["get"])
def restart_task_from():
    """
    Restart a specific analysis task for a given date.

    URL Parameters:
        task_type (str): The type of analysis task to restart ("stacking", "correction", "stitching", "all").
        date (str): The date for which the task should be restarted.

    Returns:
        dict: A JSON response indicating the status of the task restart.
    """
    task_type = request.args.get("task_type")
    date = request.args.get("date")

    # find images object by date
    new_images = analyse.image_store.find_images_by_date(date)

    if task_type == "stacking":
        new_images.focus_stacked = False
    elif task_type == "correction":
        new_images.correction = False
    elif task_type == "stitching":
        new_images.stitched = False
    elif task_type == "all":
        new_images.focus_stacked = False
        new_images.correction = False
        new_images.stitched = False

    analyse.analyse_pipeline(new_images)
    return jsonify({'message': f'Analysis started for date {date}'})

@app.route('/remove', methods=['get', 'delete'])
def remove_images_from_db():
    """
    Remove images from the database for a given date and name.

    URL Parameters:
        date (str): The date for which images should be removed from the database.
        name (str): The name of the images to remove.

    Returns:
        dict: A JSON response indicating the result of the image removal operation.
    """
    date = request.args.get("date")
    name = request.args.get("name")

    result = analyse.image_store.delete_image_from_db(date, name)
    return jsonify({'result': result})

@app.route("/update_setting", methods=['get'])
def update_setting():
    """
    Update a specific setting for a given date.

    URL Parameters:
        date (str): The date for which the setting should be updated.
        setting_name (str): The name of the setting to update.
        new_value (str): The new value for the setting.

    Returns:
        dict: A JSON response indicating the result of the setting update operation.
    """
    date = request.args.get("date")
    setting_name = request.args.get("setting_name")
    new_value = request.args.get("new_value")

    new_images = analyse.image_store.find_images_by_date(date)

    try:
        setattr(new_images, setting_name, type(new_images[setting_name])(new_value))
        print(getattr(new_images, setting_name))

        # ugly solution
        if setting_name == "overlap":
            new_images["overlap"] = float(new_value)

        analyse.image_store.update_images(new_images)
        return jsonify({'date': date, "setting_name": setting_name, "new_value": new_value})
    except Exception as e:
        return jsonify({"message": str(e)})

@app.route("/get_busy_tasks", methods=["get"])
def get_busy_tasks():
    """
    Get information about busy analysis tasks.

    Returns:
        dict: A JSON response containing information about busy tasks.
    """
    return jsonify({
        "efi_task": analyse.busy_efi,
        "correction_task": analyse.busy_correction,
        "stitching_task": analyse.busy_stitching,
    })

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5002)