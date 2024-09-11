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
import os 
import threading

app = Flask('stitching')
threads = []  # list to store running threads and their statuses

@app.route("/stitching", methods=['POST'])
def stitch():
    output = request.form.get("output", "test.jpg")
    grid_height = int(request.form.get("grid_height", 0))
    grid_width = int(request.form.get("grid_width", 0))

    start_tile_col = int(request.form.get("start_tile_col", 0))
    start_tile_row = int(request.form.get("start_tile_row", 0))

    extent_height = int(request.form.get("extent_height", 0))
    extent_width = int(request.form.get("extent_width", 0))

    horizontal_overlap = float(request.form.get("horizontal_overlap", 0))
    vertical_overlap = float(request.form.get("vertical_overlap", 0))

    overlap_uncertainty = int(float(request.form.get("overlap_uncertainty", 5)))

    output_path = request.form.get("output_path")

    filename_pattern_type = request.form.get("filename_pattern_type", "ROWCOL")
    # filename_pattern = request.form.get("filename_pattern", "tile_{r}_{c}.tiff")
    filename_pattern = request.form.get("filename_pattern")

    grid_origin = request.form.get("grid_origin", "UL")

    image_dir = request.form.get("image_dir")

    output_full_image = "true"

    log_level = request.form.get("log_level", "INFO")

    program_type = request.form.get("program_type", "CUDA")

    name_prefix = request.form.get("out_file_prefix", "img-")

    blending_mode = request.form.get("blending_mode", "OVERLAY")
    blending_alpha = int(request.form.get("blending_alpha", 0))
    blending_alpha = "NaN" if blending_alpha == 0 else blending_alpha

    print(output, log_level)

    # Define a function that executes the focus-stack command
    cmd = (
        "/usr/bin/java -d64 -Xmx200g -jar /opt/MIST/target/MIST_-2.1-jar-with-dependencies.jar "
        "--gridHeight %s "
        "--gridWidth %s "
        "--extentHeight %s "
        "--extentWidth %s "
        "--horizontalOverlap %s "
        "--verticalOverlap %s "
        "--overlapUncertainty %s "
        "--outputPath %s "
        "--startTileCol %s "
        "--startTileRow %s "
        "--filenamePatternType \"%s\" "
        "--filenamePattern \"%s\" "
        "--gridOrigin \"%s\" "
        "--imageDir \"%s\" "
        "--outputFullImage %s "
        "--logLevel %s "
        "--programType %s "
        "--outFilePrefix %s "
        "--blendingMode %s "
        "--blendingAlpha %s "
        "--headless false "
        "--outputImgPyramid true"
    ) % (grid_height, grid_width, extent_height, extent_width, horizontal_overlap, vertical_overlap, overlap_uncertainty, output_path, start_tile_col, start_tile_row, filename_pattern_type, filename_pattern, grid_origin, image_dir, output_full_image, log_level, program_type, name_prefix, blending_mode, blending_alpha)

    
    os.system(cmd)
    return "Stitching in progress..."

@app.route("/threads", methods=['GET'])
def list_threads():
    results = []

    # Iterate over the list of threads and their statuses
    for thread in threads:
        # Check if the thread is still alive
        if threading.get_ident() == thread["id"]:
            thread["status"] = "running"
        else:
            thread["status"] = "finished"
        
        results.append(thread)

    return {"threads": results}

app.run(host="127.0.0.1", port=5006)