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

import numpy as np
import os
from PIL import Image
from basicpy import BaSiC
from matplotlib import pyplot as plt

class FlatFieldCorrection():
    def __init__(self, settings):
        """
        Initialize the FlatFieldCorrection class with the given settings.

        Args:
            settings (dict): A dictionary containing configuration settings.
        """
        self.reset(settings)
    
    def reset(self, settings):
        """
        Reset the FlatFieldCorrection object with new settings.

        Args:
            settings (dict): A dictionary containing configuration settings.
        """
        self.crop = settings["crop_enable"]

        if self.crop:
            self.left = int((settings["original_dim_y"] - settings["crop_dim_y"]) / 2)
            self.right = settings["original_dim_x"] - self.left
            self.top = int((settings["original_dim_x"] - settings["crop_dim_x"]) / 2)
            self.bottom = settings["original_dim_x"] - self.top
            self.black_image = Image.new("RGB", (settings["crop_dim_x"], settings["crop_dim_y"]), (0, 0, 0))
        else:
            self.black_image = Image.new("RGB", (settings["original_dim_x"], settings["original_dim_y"]), (0, 0, 0))

        # Check if the specified path exists, create it if not
        self.path = settings["flat_field_path"]
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        
        self.files = os.listdir(self.path)

        image_array_r = np.empty(len(self.files), dtype=object)
        image_array_g = np.empty(len(self.files), dtype=object)
        image_array_b = np.empty(len(self.files), dtype=object)
        image_original = np.empty(len(self.files), dtype=object)

        # Loop over the files in the directory
        for i, file_name in enumerate(self.files):
            # Load the image using PIL
            image = Image.open(os.path.join(self.path, file_name))
            # if corp function is enabled crop the image
            if self.crop:
                image = image.crop((self.left, self.top, self.right, self.bottom))
            # Add the image to the appropriate location in the image array
            image_original[i] = image
            image_array = np.array(image, dtype=np.uint8)
            image_array_r[i] = image_array[:,:,0]
            image_array_g[i] = image_array[:,:,1]
            image_array_b[i] = image_array[:,:,2]


        images_r = np.stack(image_array_r.flatten(), axis=0)
        images_g = np.stack(image_array_g.flatten(), axis=0)
        images_b = np.stack(image_array_b.flatten(), axis=0)

        self.basic_r = self.create_basic(images_r)
        self.basic_g = self.create_basic(images_g)
        self.basic_b = self.create_basic(images_b)
    
    def create_basic(self, images):
        """
        Create and fit a BaSiC object to the input images.

        Args:
            images (numpy.ndarray): Input images for BaSiC correction.

        Returns:
            BaSiC: BaSiC object fitted to the input images.
        """
        basic = BaSiC()
        basic.fit(images)
        return basic
    
    def show_the_fit(self, basic):
        """
        Visualize BaSiC correction results using Matplotlib.

        Args:
            basic (BaSiC): BaSiC object containing correction results.
        """
        fig, axes = plt.subplots(1, 3, figsize=(9, 3))
        im = axes[0].imshow(basic.flatfield)
        fig.colorbar(im, ax=axes[0])
        axes[0].set_title("Flatfield")
        im = axes[1].imshow(basic.darkfield)
        fig.colorbar(im, ax=axes[1])
        axes[1].set_title("Darkfield")
        axes[2].plot(basic.baseline)
        axes[2].set_xlabel("Frame")
        axes[2].set_ylabel("Baseline")
        fig.tight_layout()
    
    def correct_images(self, path_tiles, path_output):
        """
        Correct a single input image and save the corrected image.

        Args:
            image_path (str): Path to the input image.
            output_path (str): Path where the corrected image will be saved.
        """
        # Define the size of the 2D grid
        grid_size = (0, 0)  # Change this to match the actual size of your grid

        # fetch grid size
        print(path_tiles)
        for file_name in os.listdir(path_tiles):
            extension = file_name.split('.')[1]

            print(file_name, extension)
            if extension == 'tiff':
                x, y = map(int, file_name.split('.')[0].split('_')[1:])
                print(x, y)
                if x+1 > grid_size[0]:
                    grid_size = (x+1, grid_size[1])
                if y+1 > grid_size[1]:
                    grid_size = (grid_size[0], y+1)

        # Initialize an empty 2D NumPy array to hold the images
        image_array_r = np.empty(grid_size, dtype=object)
        image_array_g = np.empty(grid_size, dtype=object)
        image_array_b = np.empty(grid_size, dtype=object)
        image_original = np.empty(grid_size, dtype=object)

        # Loop over the files in the directory
        for x in range(grid_size[0]):
            for y in range(grid_size[1]):
                # Load the image using PIL
                image = Image.open(os.path.join(path_tiles, f"stack_{x}_{y}.tiff"))
                # if corp boolean is enabled crop the image
                if self.crop:
                    image = image.crop((self.left, self.top, self.right, self.bottom))
                # Add the image to the appropriate location in the image array

                image_original[x, y] = image
                image_array = np.array(image, dtype=np.uint8)
                print(x, y) 
                image_array_r[x, y] = image_array[:,:,0]
                image_array_g[x, y] = image_array[:,:,1]
                image_array_b[x, y] = image_array[:,:,2]
        
        # apply correction
        images_r_trans = self.basic_r.transform(np.stack(image_array_r.flatten(), axis=0))
        images_g_trans = self.basic_g.transform(np.stack(image_array_g.flatten(), axis=0))
        images_b_trans = self.basic_b.transform(np.stack(image_array_b.flatten(), axis=0))

        # write the images 
        i = 0
        for x in range(grid_size[0]):
            for y in range(grid_size[1]):
                corrected_image = Image.fromarray(
                    np.clip(
                        np.dstack((
                            images_r_trans[i],
                            images_g_trans[i],
                            images_b_trans[i],
                        ),
                        0,
                        255
                    )).astype(np.uint8))

                print("saving tile", x, y)
                corrected_image.save(f"{path_output}/corrected_tile_{x}_{y}.tiff")
                i += 1
        print("DONE CORRECTION")

    def correct_one_image(self, image_path, output_path):
        """
        Correct a single input image and save the corrected image.

        Args:
            image_path (str): Path to the input image.
            output_path (str): Path where the corrected image will be saved.
        """

        # Load the image using PIL
        image = Image.open(image_path)
        # If crop boolean is enabled crop the image
        if self.crop:
            image = image.crop((self.left, self.top, self.right, self.bottom))

        # Apply correction
        image_array = np.array(image, dtype=np.uint8)
        image_r = image_array[:, :, 0]
        image_g = image_array[:, :, 1]
        image_b = image_array[:, :, 2]
        image_r_trans = np.squeeze(np.clip(self.basic_r.transform(image_r), 0, 255)).astype(np.uint8)
        image_g_trans = np.squeeze(np.clip(self.basic_g.transform(image_g), 0, 255)).astype(np.uint8)
        image_b_trans = np.squeeze(np.clip(self.basic_b.transform(image_b), 0, 255)).astype(np.uint8)

        print(image_r_trans.shape, image_g_trans.shape, image_b_trans.shape)

        # Merge the corrected channels into an RGB image
        corrected_image = Image.fromarray(
            np.stack([image_r_trans, image_g_trans, image_b_trans], axis=2)
        )

        # Save the corrected image
        corrected_image.save(output_path)
    
    def correct_one_folder(self, path_tiles, path_output):
        """
        Correct a set of images in a folder and save the corrected images.

        Args:
            path_tiles (str): Path to the directory containing input images.
            path_output (str): Path to the directory where corrected images will be saved.
        """

        # Define the size of the 2D grid
        grid_size = (0, 0)  # Change this to match the actual size of your grid

        # fetch grid size
        print(path_tiles)
        for file_name in os.listdir(path_tiles):
            extension = file_name.split('.')[1]

            print(file_name, extension)
            if extension == 'tiff':
                x, y = map(int, file_name.split('.')[0].split('_')[1:])
                print(x, y)
                if x+1 > grid_size[0]:
                    grid_size = (x+1, grid_size[1])
                if y+1 > grid_size[1]:
                    grid_size = (grid_size[0], y+1)

        for x in range(grid_size[0]):
            for y in range(grid_size[1]):
                input_image_path = os.path.join(path_tiles, f"stack_{x}_{y}.tiff")
                output_image_path = os.path.join(path_output, f"corrected_tile_{x}_{y}.tiff")

                if os.path.exists(input_image_path):
                    self.correct_one_image(input_image_path, output_image_path)
                else: 
                    self.black_image.save(output_image_path)
