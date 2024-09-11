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

import json
import numpy as np
import pandas as pd
import os
import time
import pickle
import gc
import threading

import matplotlib.pyplot as plt

from heightmap.HeightMap import HeightMap
from laser.laser import Laser
from camera.GenICam import GenICam
from camera.DSLR import DSLR
from cnc.CNCClient import CNC
from db.ImageToStore import image_store, images

camera = {
    "DSLR": DSLR,
    "GenICam": GenICam,
}

class Acquisition():
    # make Acquisition a singleton

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
          cls.instance = super(Acquisition, cls).__new__(cls)
        return cls.instance

    def __init__(self, path_to_config):
        # read in the config
        config_file = open(path_to_config)
        self.config = json.load(config_file)
        config_file.close()

        # select settings of selected device
        i=0
        self.camera_config = self.config["CAMERA"]["CAMERA_LIST"][i]
        while i < len(self.config["CAMERA"]["CAMERA_LIST"]) and self.camera_config["CAMERA_NAME"] != self.config["CAMERA"]["CAMERA_ACTIVE"]:
            i += 1
            self.camera_config = self.config["CAMERA"]["CAMERA_LIST"][i]

        print(json.dumps(self.camera_config, indent=2))
        print(json.dumps(self.config, indent=2))

        # define objects
        self.hmap = HeightMap(self.camera_config)

        self.extension = self.config["IMAGE"]["EXTENSION"]
        
        print("Try connecting to camera ...")
        self.camera = camera[self.camera_config["CAMERA_TYPE"]](self.config[self.camera_config["CAMERA_TYPE"]])

        print("Try connection to the laser ...")
        self.laser = Laser(
            self.config["LASER"]["LASER_IP"],
            self.config["LASER"]["UDP_PORT"]
        )

        self.image_store= image_store(self.config["DB"]["CONN_STR"])

        print(self.config["CNC"]["CNC_URI"])
        self.cnc = CNC(
            self.config["CNC"]["CNC_URI"],
            (
                self.config["CNC"]["MAX_DIM_X"],
                self.config["CNC"]["MAX_DIM_Y"],
                self.config["CNC"]["MAX_DIM_Z"],
            ),
            self.config["CNC"]["MAX_F_SPEED"],
        )

        self.cnc.set_speed(self.config["CNC"]["START_SPEED"])
        print("Done setting up the acquisition")

    def __del__(self):
        self.cnc.move(0, 0, 0)
        del self.cnc
        time.sleep(10)
        del self.hmap
        del self.camera
        del self.laser

    def scan_height(self, cord1, cord2, step=1, z=0):
        '''
        The function scans the the grid starting with cord1 and moves with steps to cord2

        Arguments:
            cord1: a tuple of two floats x, y: starting coordinate
            cord2: a tuple of two floats x, y: finishing coordinate
            step: a float, the incrementing step in x and y direction
            z: a float the cordinate along the z axis

        Returns:
            None
        '''
        # move cnc to cord2
        self.cnc.move(cord1[0], cord1[1], z)
        for x in np.arange(cord1[0], cord2[0]+step, step):
            y_range = np.arange(cord1[1], cord2[1]+step, step) if (x-cord1[0])/step % 2 == 0 else np.arange(cord2[1]-step, cord1[1]-step, -step)
            for y in y_range:
                if self.laser.m != None:
                    print(f"X{x} Y{y}: Dist={self.laser.m.Dist}")
                    self.hmap.add_point((x, y, self.laser.m.Dist+z))
                    self.cnc.move(x, y, z)

    def scan_line_height(self, cord, z=0):
        '''
        Scans a single line of height data using the CNC and laser sensor.

        Arguments:
            cord: tuple of two floats (x, y) that represent the position of the line.
            z: float, the coordinate along the z axis.

        Returns:
            None
        '''
        pd.set_option('float_format', '{:f}'.format)
        x, y = cord

        # start timer()
        _, t1, t2 = self.cnc.move(x, y, z)

        # end timer
        print("times: ", t1, t2)

        pos_df = self.cnc.h_pos.loc[(self.cnc.h_pos["time"] > t1) & (self.cnc.h_pos["time"] < t2)]

        # take time to update laser status
        while self.laser.last_update < t2:
            pass
        h_measure = self.laser.h_measure.copy()
        h_measure.dropna(inplace=True)
        print(h_measure)
        height_df = h_measure.loc[(h_measure["time"] > t1) & (h_measure["time"] < t2)]

        points_df = self.hmap.add_line(pos_df, height_df)
        del height_df
        return points_df

    def scan_height_lineair(self, cord1, cord2, step=1, z=0):
        '''
        '''
        self.cnc.move(cord1[0], cord1[1], z)

        self.cnc.reset_history()
        self.laser.reset_history()

        y = cord2[1]

        for x in np.arange(cord1[0], cord2[0]+step, step):
            print(x, y)
            self.scan_line_height((x, y), z)
            y = cord2[1] if y == cord1[1] else cord1[1]
            self.scan_line_height((x, y), z)

    def scan_drill_sample(self, cord1, cord2, names=[], date="dateless", name="drill_sample", z=0, step_cord_x=7, step_cord_y=7, amount=5, percentil=75):
        '''
        Perform a scan of a drill sample bord.

        Args:
            cord1 (tuple): The coordinates (x, y) of the first line.
            cord2 (tuple): The coordinates (x, y) of the second line.
            names (list, optional): A list of names for the generated pictures. Defaults to [].
            date (str, optional): The date associated with the pictures. Defaults to "".
            z (float, optional): The z-coordinate of the movement. Defaults to 0.
            step_cord_x (int, optional): The step size between picture positions. Defaults to 7.
            step_cord_y (int, optional): The step size between picture positions. Defaults to 7.
            amount (int, optional): The number of pictures to take. Defaults to 5.
            percentil (int, optional): The percentile threshold for selecting points. Defaults to 85.

        Returns:
            None
        '''
        def plot_scatter(points_df_old, points_df, centers, file_name=None):
            '''
            Plot scatter points and vertical lines at cluster centers.

            Args:
                points_df_old (DataFrame): DataFrame containing the original points.
                points_df (DataFrame): DataFrame containing the selected points.
                centers (Series): Series containing the cluster centers.

            Returns:
                None
            '''
            plt.cla()
            plt.clf()
            plt.scatter(points_df_old["x"], points_df_old["d"], color="blue", alpha=0.4)
            plt.scatter(points_df["x"], points_df["d"], color="red", alpha=0.4)
            for x in centers:
                plt.axvline(x, color="black")
            plt.xticks(list(centers))
            plt.ylabel("distance (mm)")
            plt.xlabel("x (mm)")
            if file_name is not None:
                plt.savefig(file_name)
            else:
                plt.show()

        def scan_line(cord):
            '''
            Scan a line and select points based on a percentile threshold.

            Args:
                cord (tuple): The coordinates (x, y) of the line to scan.

            Returns:
                tuple: A tuple containing the original points DataFrame, the selected points DataFrame, and the cluster centers.
            '''
            points_df = self.scan_line_height(cord, z)
            points_df_old = points_df.copy()
            points_df = points_df.loc[points_df["d"] > points_df["d"].quantile(percentil/100)]
            # take distance of 10
            points_df["cluster"] = points_df["x"].diff().gt(10).cumsum()
            centers = points_df.groupby("cluster")["x"].mean()
            return points_df_old, points_df, centers

        start_path = f"{self.config['DB']['IMAGE_DB_PATH']}/{date}_{name}/"
        os.mkdir(start_path)

        # Go to the first line
        self.cnc.move(cord1[0], cord1[1], z)
        # first scan x-line of plate
        points_df1_old, points_df1, centers1 = scan_line((cord2[0], cord1[1]))
        plot_scatter(points_df1_old, points_df1, centers1, f"{start_path}/centers1.png")

        self.cnc.move(cord1[0], cord2[1], z)
        points_df2_old, points_df2, centers2 = scan_line((cord2[0], cord2[1]))
        plot_scatter(points_df2_old, points_df2, centers2, f"{start_path}/centers2.png")

        print("centers 1:", centers1)
        print("centers 2:", centers2)
        # 2. calculate different Z cords
        picture_dfs = []
        for i in range(amount):
            line_cord1 = (centers1[i], cord1[1])
            line_cord2 = (centers2[i], cord2[1])

            cord1_camera = (line_cord1[0] - self.camera_config["SPACES"]["LASER_TO_CAMERA_X"], line_cord1[1] - self.camera_config["SPACES"]["LASER_TO_CAMERA_Y"])
            cord2_camera = (line_cord2[0] - self.camera_config["SPACES"]["LASER_TO_CAMERA_X"], line_cord2[1] - self.camera_config["SPACES"]["LASER_TO_CAMERA_Y"])
            print(cord1_camera, cord2_camera)
            self.cnc.move(line_cord1[0], line_cord1[1], z)
            points_df1 = self.scan_line_height((line_cord2[0], line_cord2[1]), z)
            picture_df = self.hmap.get_picture_positions(cord1_camera, cord2_camera, step_cord_x, step_cord_y, threshold=5) # threshold kan nog worden toegevoegd
            print("picture df {i}", picture_df, points_df1)
            picture_dfs.append(picture_df)

        # 3. take pictures
        for i, picture_df in enumerate(picture_dfs):
            new_images = images()
            new_images.name = names[i]
            new_images.date = date
            new_images.camera = self.camera_config["CAMERA_NAME"]
            new_images.index = i

            new_images.start_path = f"{start_path}drill_{names[i]}"
            os.mkdir(new_images.start_path)

            print("new dir created:", new_images.start_path)
            self.hmap.plot_points(new_images.start_path)
            picture_df.to_csv(f"{new_images.start_path}/picture_data.csv")

            new_images.start_x = picture_df.iloc[0]["x"]
            new_images.start_y = picture_df.iloc[0]["y"]
            new_images.increment_x = step_cord_x
            new_images.increment_y = step_cord_y
            new_images.overlap = (1 - (step_cord_x/self.camera_config["CAMERA_WIDTH_CORRECTION"])) * 100

            size_sources = (1, np.arange(cord1_camera[1], cord2_camera[1], step_cord_y).size)
            sources = np.empty(size_sources, object)

            for row in picture_df.iterrows():
                pos = row[1]
                sources_index = 0, int(round((pos["y"] - cord1_camera[1])/step_cord_y))
                if sources_index[0] < size_sources[0] and sources_index[1] < size_sources[1]:
                    images_list = self.take_stacked_pictures((pos["x"], pos["y"]), pos["z_start"], int(pos["z_amount"]), path=new_images.start_path, index=sources_index)
                    print("x:", pos["x"], "y:", pos["y"], "index:", sources_index)
                    sources[sources_index[0], sources_index[1]] = {'z_start': pos["z_start"], 'images_sourcs': images_list}
                else:
                    print("Somthing wrong with dimensions. Move along")

            print("size sources", sources.shape)

            # Remove leading and tailing full None rows
            mask_row = np.any(sources != None, axis=1)
            start_idx_row = np.where(mask_row)[0][0]
            end_idx_row = np.where(mask_row)[0][-1]

            # Remove full None columns
            mask_col = np.any(sources != None, axis=0)
            start_idx_col = np.where(mask_col)[0][0]
            end_idx_col = np.where(mask_col)[0][-1]

            sources = sources[start_idx_row:end_idx_row+1, start_idx_col:end_idx_col+1]
            print("size sources", sources.shape)
            new_images.sources = sources

            # send new images to mongodb
            # 4. send pictures metadata to database
            self.image_store.post_images(new_images)

    def take_stacked_pictures(self, cord, z_start, n, step_z=0.3, path="/home/woodlab/Pictures/Z_stack_test/", index=None):
        '''
        First moves the cnc to (x, y, z_start) where (x, y) = cord
        Than the function takes n pictures along the z axis starting at z_start and moves down with the given stepsize

        Arguments
            cord: a tuple of two floats representing x and y on the CNC
            z_start: a float that represents z coordinate where CNC starts taking pictures
            n: an integers, the amount of pictures along along the z
            step: a float, the stepsize along the z axis
            path: a string, the path where the pictures are stored

        Returns:
            list of paths where the images are stored
        '''
        # first move cnc to x, y, z_start
        x, y= cord
        self.cnc.move(x, y, z_start)
        images_list = []

        # take n pictures along the z axis
        for i in range(n):
            z = z_start + (i * step_z)
            self.cnc.move(x, y, z)
            print(f"Take picture number {i+1}")
            print(f"==========================")
            # self.camera.take_picture(f"~/Pictures/Z_stack_test/stack_{x}_{y}_{int(z*1000)}_d_{self.laser.m.Dist:.2f}.jpg") # the way pictures are saved need to be changed
            if index is not None:
                # Fiji image_path
                image_path = f"stack_{index[0]}_{index[1]}_{i}.{self.extension}"
            else:
                image_path = f"stack_{int(x)}_{int(y)}_{int(z_start*1000000)}_{i}.{self.extension}"
            self.camera.take_picture(f"{path}/{image_path}")
            images_list.append(image_path)

        return images_list

    def scan_surface(self, cord1, cord2, name="nameless", date="dateless", step_height=3, step_cord_x=7, step_cord_y=7, z=0, margin=0, threshold=5, blending_type="LINEAR"):
        '''
        The scan_surface function takes in several parameters and performs a series of steps to scan a surface and store the resulting images in the document store.

        Arguments:
            cord1 and cord2: tuples containing the (x, y) coordinates of two points that define the rectangular area to scan.
            name: the name of the scan, as string.
            date: the date of the scan, as string.
            step_height: the height increment between pictures, as float.
            step_cord_x: the distance between pictures along x-axis, as float.
            step_cord_y: the distance between pictures along y-axis, as float.
            z: the starting z-coordinate, as float.
            margin: margin to take height points outside image into account
            threshold: threshold to take height points outside image into account
            blending_type: the type of blending to use, as string, there are 3 options OVERLAY, LINEAIR (default) and AVERAGE.
        Returns:
            None
        '''
        # 1. take heightmap
        cord1_laser = cord1
        cord2_laser = cord2

        cord1 = (cord1[0] - self.camera_config["SPACES"]["LASER_TO_CAMERA_X"], cord1[1] - self.camera_config["SPACES"]["LASER_TO_CAMERA_Y"])
        cord2 = (cord2[0] - self.camera_config["SPACES"]["LASER_TO_CAMERA_X"], cord2[1] - self.camera_config["SPACES"]["LASER_TO_CAMERA_Y"])

        lock = threading.Lock()
        lock.acquire()
        self.scan_height_lineair(cord1_laser, cord2_laser, step_height, z)

        # 2. calculate different Z cords
        picture_df = self.hmap.get_picture_positions(cord1, cord2, step_cord_x, step_cord_y, margin, threshold)
        gc.collect()
        lock.release()

        if picture_df.empty:
            print("Something went wrong")
            return None

        # 3. take pictures
        new_images = images()
        new_images.name = name
        new_images.date = date
        new_images.camera = self.camera_config["CAMERA_NAME"]
        new_images.start_path = f"{self.config['DB']['IMAGE_DB_PATH']}/{new_images.date}_{new_images.name}"
        os.mkdir(new_images.start_path)
        print("new dir created:", new_images.start_path)
        self.hmap.plot_points(new_images.start_path)
        picture_df.to_csv(f"{new_images.start_path}/picture_data.csv")

        new_images.start_x = picture_df.iloc[0]["x"]
        new_images.start_y = picture_df.iloc[0]["y"]
        new_images.increment_x = step_cord_x
        new_images.increment_y = step_cord_y
        new_images.overlap = (1 - (step_cord_x/self.camera_config["CAMERA_WIDTH_CORRECTION"])) * 100
        new_images.blending = blending_type

        size_sources = int(np.ceil((cord2[0] - cord1[0])/step_cord_x)), int(np.ceil((cord2[1] - cord1[1])/step_cord_y))
        print(((cord2[0]-cord1[0])/step_cord_x , (cord2[1]-cord1[1])/step_cord_y), int(np.ceil((cord2[0]-cord1[0])/step_cord_x)) , int(np.ceil((cord2[1]-cord1[1])/step_cord_y)), size_sources)
        print(size_sources)
        sources = np.empty(size_sources, object)

        for row in picture_df.iterrows():
            pos = row[1]
            sources_index = int(round((pos["x"] - cord1[0])/step_cord_x)), int(round((pos["y"] - cord1[1])/step_cord_y))
            if sources_index[0] < size_sources[0] and sources_index[1] < size_sources[1]:
                images_list = self.take_stacked_pictures((pos["x"], pos["y"]), pos["z_start"], int(pos["z_amount"]), path=new_images.start_path, index=sources_index)
                print("x:", pos["x"], "y:", pos["y"], "index:", sources_index)
                sources[sources_index[0], sources_index[1]] = {'z_start': pos["z_start"], 'images_sourcs': images_list}
            else:
                print("Somthing wrong with dimensions. Move along")

        print("size sources", sources.shape)
        # Remove leading and tailing full None rows
        mask_row = np.any(sources != None, axis=1)
        start_idx_row = np.where(mask_row)[0][0]
        end_idx_row = np.where(mask_row)[0][-1]

        # sources = sources[~np.all(sources == None, axis=1)]

        # Remove full None columns
        mask_col = np.any(sources != None, axis=0)
        start_idx_col = np.where(mask_col)[0][0]
        end_idx_col = np.where(mask_col)[0][-1]

        # sources = sources[:, ~np.all(sources == None, axis=0)]
        sources = sources[start_idx_row:end_idx_row+1, start_idx_col:end_idx_col+1]
        print("size sources", sources.shape)
        new_images.sources = sources

        ##########################################################
        # Disable automatic stitching                            #
        ##########################################################
        # new_images.stitched = True # enable this line to disable the automatic stitching


        # new_images.stitched = True, 

        # 4. send pictures metadata to database
        self.image_store.post_images(new_images)
    
    def scan_surface_fixed(self, cord1, cord2, name="nameless", date="dateless", step_cord_x=7, step_cord_y=7, z=0, amount=1, step=None, blending_type="LINEAR"):
        '''
        like a normal scan surface but doesn't generate a height map an

        Arguments:
            cord1 and cord2: tuples containing the (x, y) coordinates of two points that define the rectangular area to scan.
            name: the name of the scan, as string.
            date: the date of the scan, as string.
            step_cord_x: the distance between pictures along x-axis, as float.
            step_cord_y: the distance between pictures along y-axis, as float.
            z: the starting z-coordinate, as float.
            amount: the amout of pictures along z-axis, as float
            step: step size in mm between two pictures, default is DOF of camera.
            blending_type: the type of blending to use, as string, there are 3 options OVERLAY, LINEAIR (default) and AVERAGE.
        Returns:
            None
        '''
        # 1. covert to camera cordinates
        cord1 = (cord1[0] - self.camera_config["SPACES"]["LASER_TO_CAMERA_X"], cord1[1] - self.camera_config["SPACES"]["LASER_TO_CAMERA_Y"])
        cord2 = (cord2[0] - self.camera_config["SPACES"]["LASER_TO_CAMERA_X"], cord2[1] - self.camera_config["SPACES"]["LASER_TO_CAMERA_Y"])

        step = step if step is not None else self.camera_config["CAMERA_DOF"]

        # 2. calcuate positions
        size_sources = int(np.ceil((cord2[0] - cord1[0])/step_cord_x)), int(np.ceil((cord2[1] - cord1[1])/step_cord_y))
        row_indices = np.arange(cord1[0], cord1[0] + (size_sources[0] * step_cord_x), step_cord_x)
        column_indices = np.arange(cord1[1], cord1[1] + (size_sources[1] * step_cord_y), step_cord_y)
        sources = np.empty(size_sources, object)

        # define images object
        new_images = images()
        new_images.name = name
        new_images.date = date
        new_images.camera = self.camera_config["CAMERA_NAME"]
        new_images.start_path = f"{self.config['DB']['IMAGE_DB_PATH']}/{new_images.date}_{new_images.name}"
        os.mkdir(new_images.start_path)
        print("new dir created:", new_images.start_path)

        new_images.start_x = cord1[0]
        new_images.start_y = cord1[1]
        new_images.increment_x = step_cord_x
        new_images.increment_y = step_cord_y
        new_images.overlap = (1 - (step_cord_x/self.camera_config["CAMERA_WIDTH_CORRECTION"])) * 100
        new_images.blending = blending_type

        # 3. take pictures
        for i, x in enumerate(row_indices):
            for j, y in enumerate(column_indices):
                images_list = self.take_stacked_pictures((x, y), z, amount, step_z=step, path=new_images.start_path, index=(i, j))
                sources[i, j] = {'z_start': z, 'images_sourcs': images_list}

        new_images.sources = sources

        ##########################################################
        # Disable automatic stitching                            #
        ##########################################################
        # new_images.stitched = True # enable this line to disable the automatic stitching

        # 4. send pictures metadata to database
        self.image_store.post_images(new_images)
    
    def update_config(self, config_path):
        # update the camera config in settings
        i=0
        while i < len(self.config["CAMERA"]["CAMERA_LIST"]) and self.config["CAMERA"]["CAMERA_LIST"][i]["CAMERA_NAME"] != self.config["CAMERA"]["CAMERA_ACTIVE"]:
            i += 1

        self.config["CAMERA"]["CAMERA_LIST"][i] = self.camera_config
        print(json.dumps(self.config, indent=2))

        # Overwrite the JSON file with the Python object
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)