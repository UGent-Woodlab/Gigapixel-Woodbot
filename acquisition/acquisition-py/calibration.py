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

from acquisition import Acquisition
import time
import sys
import os
import re
import cv2
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import numpy as np

class Calibration():
    def __init__(self, acquisition):
        self.acq = acquisition

    def manual_xy(self, x, y, z, gui_config_path):
        # move to new cordinates
        self.acq.cnc.move(
            self.acq.cnc.position[0] - float(x),
            self.acq.cnc.position[1] - float(y),
            self.acq.cnc.position[2] + float(z)
        )

        # take picture
        print("take picture")
        file_name_tiff = f"{gui_config_path}/calibration/manual_xy.tiff"
        self.acq.camera.take_picture(file_name_tiff)

        # move back to original position
        self.acq.cnc.move(
            self.acq.cnc.position[0] + float(x),
            self.acq.cnc.position[1] + float(y),
            self.acq.cnc.position[2] - float(z)
        )

        # draw cross
        image = Image.open(file_name_tiff)
        width, height = image.size

        draw = ImageDraw.Draw(image)

        color_cross = (255, 0, 0) # red
        draw.line((0, 0, width, height), fill=color_cross, width=5)
        draw.line((0, height, width, 0), fill=color_cross, width=5)

        # downsize for gui
        factor =  2
        image = image.resize((width//factor, height//factor))
        file_name_png = f"{gui_config_path}/calibration/manual_xy.png"
        image.save(file_name_png)

        return {
            "x": x, 
            "y": y, 
            "tiff": file_name_tiff, 
            "png": file_name_png, 
        }
    
    def calc_variance_of_lapacian(self, img):
        grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(grey_img, cv2.CV_64F).var()
        return fm

    def take_z_stack(self, z_start, step , amount, path):

        x_laser = self.acq.cnc.position[0]
        y_laser = self.acq.cnc.position[1]

        x_camera = self.acq.cnc.position[0] - self.acq.camera_config["SPACES"]["LASER_TO_CAMERA_X"]
        y_camera = self.acq.cnc.position[1] - self.acq.camera_config["SPACES"]["LASER_TO_CAMERA_Y"]

        z = self.acq.cnc.position[2]

        # clear folder
        for file_name in os.listdir(path):
            print(file_name)
            os.unlink(os.path.join(path, file_name))

        ## find correct start position
        z_cord = 0 
        print("print bizar abs value", abs((self.acq.laser.m.Dist if isinstance(self.acq.laser.m.Dist, type(0.1)) else 0) - z_start), file=sys.stdout)
        h = self.acq.laser.m.Dist
        print("last h", h)
        h = h if h > 0 else 0 
        while abs(h - z_start) > 0.1:
            print("diff laser and z_start", h, z_start, abs(h - z_start), file=sys.stdout)
            self.acq.cnc.move(x_laser, y_laser, z_cord)
            h = float(self.acq.laser.m.Dist)
            print("last h", h)
            h = h if h > 0 else 0

            if h > 0 and abs(h - z_start) > 3:
                z_cord = self.acq.cnc.position[2] + abs(h - z_start) - 2
            else:
                z_cord += 0.05

        ## take stack
        result = []
        plot_result = [[], []]
        resize_factor = 4

        for i in range(amount):
            self.acq.cnc.move(x_laser, y_laser, z_cord + i*step)
            time.sleep(1)
            h = float(self.acq.laser.m.Dist)
            result.append({
                'h': round(h, 2) if h > 0 else 'nan',
                'file_name_tiff': f"/stack_{int(round(x_laser))}_{int(round(y_laser))}_{int(i)}.tiff",
                'file_name_png': f"stack_{int(round(x_laser))}_{int(round(y_laser))}_{int(i)}.png"
            })
            self.acq.cnc.move(x_camera, y_camera, z_cord + i*step)
            self.acq.camera.take_picture(f'{path}{result[-1]["file_name_tiff"]}')

            img = cv2.imread(f'{path}{result[-1]["file_name_tiff"]}')

            width, height = img.shape[1], img.shape[0]
            ## Calculate variance of laplacian
            result[-1]["variance_of_laplacian"] = self.calc_variance_of_lapacian(img)

            # save result to plot later
            plot_result[0].append(result[-1]['h'])
            plot_result[1].append(result[-1]["variance_of_laplacian"])

            ## Save scaled file
            img = cv2.resize(img, (width//resize_factor, height//resize_factor))

            # Get the dimensions of the image
            height, width, _ = img.shape

            # Define the dimensions for the center crop
            crop_width = 1000  # Adjust this value as needed
            crop_height = 1000  # Adjust this value as needed

            # Calculate the starting coordinates for the crop to be centered
            start_x = (width - crop_width) // 2
            start_y = (height - crop_height) // 2

            img = img[start_y:start_y + crop_height, start_x:start_x + crop_width]

            file_name_png = re.sub(r"\.\w+$", ".png", result[-1]["file_name_tiff"])
            cv2.imwrite(f"{path}/{file_name_png}", img)

        self.acq.cnc.move(x_laser, y_laser, z)

        # # remove the tiff
        # for file_name in os.listdir(path):
        #     # remove old file
        #     os.unlink(os.path.join(path, file_name))

        plt.figure().set_figheight(5)
        plt.figure().set_figwidth(25)
        plt.tight_layout()
        plt.margins(0)
        fig, ax = plt.subplots()
        ax.set_xlabel("Heigth of measered by laser (mm)")
        ax.set_ylabel("Variance of laplacian")
        ax.set_xticks(np.arange(min(plot_result[0])-0.5, max(plot_result[0])+0.5, step))
        ax.grid()
        ax.plot(plot_result[0], plot_result[1], '-o') 
        plt.savefig(f"{path}/var_of_laplacian.png")
        plt.cla()
        plt.rcParams["figure.figsize"] = (15,15)

        return {
            "result": result,
            "best_index": plot_result[1].index(max(plot_result[1])),
            "var_of_laplacian_path": "var_of_laplacian.png",
        }