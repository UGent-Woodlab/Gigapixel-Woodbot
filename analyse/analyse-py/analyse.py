#
# Created on Tue Sep 05 2023
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

import json
import os
import re
import numpy as np
import time
import logging
import requests
import threading
from datetime import datetime
import queue

from db.store_to_image import image_store, images

class Analyse():
    def __init__(self, path_to_config):
        """
        Initialize the Analyse class.

        Args:
            path_to_config (str): The path to the configuration file.

        """

        # read in the config
        config_file = open(path_to_config)
        self.config = json.load(config_file)
        self.dbpath = self.config["DB"]["IMAGE_DB_PATH"]
        self.extension = self.config["IMAGE"]["EXTENSION"]
        self.focus_stack_url = self.config["FOCUS_STACK_URL"]
        self.correction_url = self.config["CORRECTION_URL"]
        self.stitching_url = self.config["STITCHING_URL"]
        config_file.close()

        print(self.config)
        self.image_store = image_store(self.config["DB"]["CONN_STR"])

        self.busy_efi = None
        self.busy_correction = None
        self.busy_stitching = None

    def __del__(self):
        """
        Start observing for changes in the image store and trigger analysis for new images.

        """

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    def start_observation(self):
        """
        Start observing for changes in the image store and trigger analysis for new images.

        """

        with self.image_store.change_stream as stream:
            for change in stream:
                print(change)

                lock = threading.Lock()
                lock.acquire()

                new_images = images(change['fullDocument'])
                print("update noticed in ", new_images.date, new_images.name)

                self.analyse_pipeline(new_images)

                lock.release()

    def start_by_date(self, date_str):
        """
        Start image analysis for images on a specific date.

        Args:
            date_str (str): The date in string format (e.g., "25_04_2023_15_04_37").

        """

        new_images = self.image_store.find_images_by_date(date_str)
        print(new_images.sources)
        print("stacked", new_images.stacked_sources)

        new_images.focus_stacked = False
        new_images.correction = False
        new_images.stitched = False

        self.analyse_pipeline(new_images)

    def copy_to_fiji_file_format(self, sources, images_path):
        """
        Copy images to Fiji file format.

        Args:
            sources (list): List of image sources.
            images_path (str): Path to the images.

        """

        print(sources, images_path)
        os.makedirs(f"{images_path}/final_tiles", exist_ok=True)

        for x, row in enumerate(sources):
            for y, file_name in enumerate(row):
                if file_name is not None:
                    print(x, y, file_name, f"{images_path}/stacked/{file_name} {images_path}/fiji/tile_{x}_{y}.{self.extension}")
                    os.system(f"cp -n {images_path}/stacked/{file_name} {images_path}/fiji/tile_{x}_{y}.{self.extension}")
                else:
                    # save black image
                    os.system(f"cp -n {self.dbpath}/black.tiff {images_path}/final_tile/tile_{x}_{y}.{self.extension}")
    
    def write_logging(self, file_name, line):
        """
        Write a log line to a specified file.

        Args:
            file_name (str): The name of the log file.
            line (str): The log line to write.

        """
        
        with open(file_name, 'a+') as f:
            f.write(line + "\n")
            f.close()

    def analyse_pipeline(self, new_images):
        """
        Analyze a set of images in a pipeline fashion.

        Args:
            new_images (images): An instance of the `images` class containing image data.

        """

        if new_images.sources is not None:
            images_path = new_images.start_path 
            if not new_images.focus_stacked:
                os.makedirs(f"{images_path}/stacked", exist_ok=True)
                # start EFI
                self.write_logging(f"{images_path}/logging.csv", f"stitching_start;{datetime.now().strftime('%H:%M:%S')}")
                self.start_EFI(new_images)
                print("ANALYSE EFI STARTED")
            elif not new_images.correction:
                os.makedirs(f"{images_path}/corrected", exist_ok=True)
                # start Correction
                self.write_logging(f"{images_path}/logging.csv", f"correction_start;{datetime.now().strftime('%H:%M:%S')}")
                self.start_correction(new_images)
                print("ANALYSE CORRECTION STARTED")
            elif not new_images.stitched:
                os.makedirs(f"{images_path}/stitched", exist_ok=True)
                # start stitching
                self.write_logging(f"{images_path}/logging.csv", f"stitching_start;{datetime.now().strftime('%H:%M:%S')}")
                self.start_stitching(new_images)

            print("ANALYSE DONE")

    def start_EFI(self, new_images):
        """
        Start Extended Focus Imaging (EFI) for a set of images.

        Args:
            new_images (images): An instance of the `images` class containing image data.

        Returns:
            images: An updated instance of the `images` class after EFI.

        """

        print("START EXTENDED FOCUS IMAGING (EFI)")

        images_path = new_images.start_path

        stacked_sources = np.empty(new_images.sources.shape, object)
        # fetch every position
        uids = set()
        for x, _ in enumerate(new_images.sources):
            for y, entry in enumerate(new_images.sources[x]):
                # generate output file
                if entry is not None:
                    output_rel = re.sub("(_\d+)*\.", f"_{x}_{y}.", entry["images_sourcs"][0])
                    output = f"{images_path}/stacked/" + output_rel
                    print(output)
                    if len(entry["images_sourcs"]) > 1:
                        # stacking is needed -> there are more than 1 pictures taken
                        z_start = entry["z_start"]
                        images = ' '.join([f"{images_path}/{file}" for file in entry["images_sourcs"]])

                        # EFI the images
                        uid = int(id(entry))
                        respons = requests.post(f"{self.focus_stack_url}/focus_stack", data={
                            "id": uid,
                            "output": output,
                            "images": images
                        })
                        print(uid, ": respons", respons.content)
                        uids.add(str(uid))
                        # os.system(f"focus-stack --nocrop --align-keep-size --no-contrast --no-whitebalance --output={output} {images}")
                        # cv2.imwrite(output, focus_stack([f"{images_path}/{file}" for file in entry["images_sourcs"]]))
                    else:
                        # if there is only 1 ->  image copy this image
                        os.system(f"cp {images_path}/{entry['images_sourcs'][0]} {output}")

                    stacked_sources[x, y] = output_rel
        
        def check_efi_is_done():
            print(uids)
            respons = requests.get(f"{self.focus_stack_url}/threads")
            respons_json = respons.json()
            finished_set = set(respons_json["finished_jobs"])

            while not uids.issubset(finished_set):
                # fetch alle the finished jobs from efi container
                respons = requests.get(f"{self.focus_stack_url}/threads")
                respons_json = respons.json()
                finished_set = set(respons_json["finished_jobs"])

                # calculate the intersection of the finished jobs and the jobs that need to be done
                inter = uids.intersection(finished_set)

                # update the progress
                print(f"Stacking for {new_images.date} : ({len(inter)}/{len(uids)}) {len(inter)/len(uids)*100} %")

                # change busy_efi  when this task is started
                if len(inter) != 0:
                    self.busy_efi = {
                        "date": new_images.date,
                        "name": new_images.name,
                        "finished_jobs": len(inter),
                        "total_jobs": len(uids)
                    }

                time.sleep(5)
            # update variables
            new_images.focus_stacked = True
            new_images.stacked_sources = stacked_sources

            self.image_store.update_images(new_images)
            self.busy_efi = None
            print("ANALYSE EFI DONE")
            self.write_logging(f"{images_path}/logging.csv", f"stacking_end;{datetime.now().strftime('%H:%M:%S')}")
        
        t = threading.Thread(target=check_efi_is_done)
        t.daemon = True
        t.start()

        return new_images
    
    def start_correction(self, new_images):
        """
        Calculate the longest sequence of non-None elements in a list.

        Args:
            images_list (list): List of image sources.

        Returns:
            list: The longest sequence of non-None elements.

        """

        images_path = new_images.start_path

        respons = requests.post(f"{self.correction_url}/correction",
            data={
                "camera": new_images.camera,
                "path_input": f"{images_path}/stacked",
                "path_output": f"{images_path}/corrected",
            }
        )

        respons_json = json.loads(respons.content)
        ids = set(respons_json["results"])

        print("Result respons:", respons.content, respons_json, ids)
        def check_correction_is_done():
            print("ANALYSE CORRECTION STARTED")
            respons = requests.get(f"{self.correction_url}/threads")
            respons_json = respons.json()
            finished_set = set(respons_json["finished_jobs"])
            while not ids.issubset(finished_set):
                # fetch alle the finished jobs from correction container
                respons = requests.get(f"{self.correction_url}/threads")
                respons_json = respons.json()
                finished_set = set(respons_json["finished_jobs"])

                inter = ids.intersection(finished_set)
                print(f"Correction for {new_images.date}: ({len(inter)}/{len(ids)}) {len(inter)/len(ids)*100} %")

                # change busy_efi  when this task is started
                if len(inter) != 0:
                    self.busy_correction = {
                        "date": new_images.date,
                        "name": new_images.name,
                        "finished_jobs": len(inter),
                        "total_jobs": len(ids),
                    }
                time.sleep(5)

            new_images.correction = True
            self.image_store.update_images(new_images)
            self.busy_correction = None
            print("ANALYSE CORRECTION DONE")
            self.write_logging(f"{images_path}/logging.csv", f"correction_end;{datetime.now().strftime('%H:%M:%S')}")

        t = threading.Thread(target=check_correction_is_done)
        t.daemon = True
        t.start()
        return new_images

    def calc_longest_seq(self, images_list):
        images_list = np.array(images_list)
        none_idxs, = np.where(np.equal(images_list, None))
        if none_idxs.size == 0:
            return images_list.tolist()
        else:
            diff = none_idxs[1:] - none_idxs[:-1]
            print(diff, diff.shape)
            if diff.shape[0] == 0:
                pos = none_idxs[0]
                return np.delete(images_list, pos).tolist()

            # if multiple take subset
            pos1 = none_idxs[diff.argmax()]+1
            pos2 = pos1+diff.max()-1
            print(images_list[pos1:pos2])
            return images_list[pos1:pos2].tolist()

    def start_stitching(self, new_images):
        """
        Start stitching a grid of images.

        Args:
            new_images (images): An instance of the `images` class containing image data.

        """

        print("START STITCHING THE IMAGES")
        images_path = new_images.start_path
        stacked_images_path = f"{images_path}/stacked"
        os.makedirs(f"{images_path}/stitched", exist_ok=True)
        
        x_max, y_max = new_images.sources.shape
        overlap = int(round(new_images.overlap) // 2)
        overlap = overlap if overlap <= 10 else 10
        print("x_max:", x_max, "y_max:", y_max, "overlap:", overlap)

        # print(new_images.overlap)
        data = {
            "grid_width": y_max,
            "grid_height": x_max,
            "start_tile_col": 0,
            "start_tile_row": 0,
            "extent_width": y_max,
            "extent_height": x_max,
            "horizontal_overlap": round(new_images.overlap),
            "vertical_overlap": round(new_images.overlap), # new_images.overlap,  
            "overlap_uncertainty": overlap,
            "image_dir": f"{images_path}/corrected",
            "output_path": f"{images_path}/stitched",
            "output": "result.tiff",
            "out_file_prefix": new_images.name if new_images.name is not None else "img",
            "filename_pattern_type": "ROWCOL",
            "filename_pattern": "corrected_tile_{r}_{c}.tiff",
            "grid_origin": "UL",
            "log_level": "INFO",
            "program_type": "CUDA",
            "blending_mode": new_images.blending if hasattr(new_images, "blending") and new_images.blending in ["OVERLAY", "LINEAR", "AVERAGE"] else "OVERLAY",
            "blending_alpha": new_images.blending_alpha if hasattr(new_images, "blending_alpha") else 4,
        }

        def send_stitching_request():
            self.busy_stitching = {
                "date": new_images.date,
                "name": new_images.name
            }
            response = requests.post(f"{self.stitching_url}/stitching", data=data)
            print(response.content)

            new_images.stitched = True
            self.busy_stitching = None
            self.image_store.update_images(new_images)

            self.write_logging(f"{images_path}/logging.csv", f"stitching_end;{datetime.now().strftime('%H:%M:%S')}")

        t = threading.Thread(target=send_stitching_request)
        t.daemon = True
        t.start()


def main():
    a = Analyse("./config.json")
    test_date = "25_04_2023_15_04_37"
    a.start_by_date(test_date)

    a.start_observation()

if __name__ == "__main__":
    main()
