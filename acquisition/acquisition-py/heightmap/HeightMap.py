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

import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
import pandas as pd
import scipy

class HeightMap():
    '''
    A class to represent a height map.

    Attributes:
        heights (pandas.DataFrame): A pandas DataFrame to store the heights of the points.
        x_diff (float): The x difference between the real world coordinates and the coordinates in the image.
        y_diff (float): The y difference between the real world coordinates and the coordinates in the image.
        camera_dim (float): Half of the camera width because later x+camera_dim/2 and x-camera_dim/2.
        camera_dof (float): The depth of field of the camera.  camera_focus (float): The focal point of the camera.  reference (int): A reference value.
    Methods:
        add_point(point): Adds a point to the heights DataFrame.
        add_line(pos_df, height_df): Merges the position and height DataFrames.
        plot_points(): Creates a 3D plot of the points.
        get_picture_positions(cord1, cord2, step_x, step_y): Gets the positions and depths of the picture.
    '''

    def __init__(self, camera_conf):
        '''
        Initializes a HeightMap object.

        Arguments:
            diff (tuple, optional): The x and y differences between the real world coordinates and the coordinates in the image. Defaults to (0, 0).
            camera_conf (dict, optional): The camera parameters. Defaults to {"CAMERA_WIDTH": 1, "CAMERA_DOF": 1, "CAMERA_FOCUS": 0}.
        '''
        plt.rcParams["figure.figsize"] = (15,15)
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['ps.fonttype'] = 42
        plt.rcParams['font.family'] = 'Arial'

        # Initialize a pandas DataFrame to store the heights of the points
        self.heights = pd.DataFrame(columns=["x", "y", "d"])
        # Store the x and y differences between the real world coordinates and the coordinates in the image
        self.x_diff = camera_conf["SPACES"]["LASER_TO_CAMERA_X"]
        self.y_diff = camera_conf["SPACES"]["LASER_TO_CAMERA_Y"]
        # Store the camera parameters
        self.camera_dim_x = camera_conf["CAMERA_WIDTH"]/2 # half because later x+camera_dim_x/2 and x-camera_dim_x/2
        self.camera_dim_y = camera_conf["CAMERA_HEIGHT"]/2 # half because later y+camera_dim_y/2 and y-camera_dim_y/2
        self.camera_dof = camera_conf["CAMERA_DOF"]
        self.camera_focus = camera_conf["CAMERA_FOCUS"]
        # Store a reference value (not sure what this is for)
        self.reference = 0
        self.upper_distance = 150

    def __del__(self):
        del self.heights

    def add_point(self, point):
        '''
        Adds a point to the heights DataFrame.

        Arguments:
            point (tuple): The (x, y, d) coordinates of the point.
        '''
        # Add a point to the DataFrame
        x, y, d = point
        self.heights.loc[len(self.heights)] = [x, y, d]

    def add_line(self, pos_df, height_df):
        '''
        Merges the position and height DataFrames.
        Then add the points to the height map

        Arguments:
            pos_df (pandas.DataFrame): The position DataFrame.
            height_df (pandas.DataFrame): The height DataFrame.
        '''

        # Merge the position and height DataFrames (not sure what this is for)
        # pos_df.time = pos_df.time.round(decimals=2)
        # height_df.time = height_df.time.round(decimals=2)
        pos_df = pos_df.round({'time': 2})
        height_df = height_df.round({'time': 2})

        pos_df = pos_df.merge(height_df, left_on="time", right_on="time", how="left").dropna()

        pos_df["d"] = pos_df["z"] + pos_df["d"]

        # add your heights to the result dataframe
        points_df = pos_df.groupby(["x", "y"], as_index=False)["d"].mean().drop_duplicates()
        print(points_df)
        self.heights = pd.concat([self.heights, points_df], ignore_index=True)
        return points_df

    def plot_points(self, path=None):
        """Creates a 3D plot of the points."""
        # Create a 3D plot of the points
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        X = self.heights["x"].to_numpy()
        Y = self.heights["y"].to_numpy()
        D = self.heights["d"].to_numpy()
        D = self.upper_distance - D # to get normal plot

        try:
            triang = mtri.Triangulation(X, Y)

            # Plot the surface of the points
            ax.plot_trisurf(triang, D, cmap="jet")
        except:
            pass

        # Plot the points as a scatter plot
        ax.scatter(X, Y, D, marker=".", c="black", alpha=0.5)
        # Set the labels for the axes
        ax.set_xlabel("X axis (mm)")
        ax.set_ylabel("Y axis (mm)")
        ax.set_zlabel("Distance (mm)")

        xlim = ax.get_xlim3d()
        ylim = ax.get_ylim3d()
        zlim = ax.get_zlim3d()

        ax.set_box_aspect((xlim[1]-xlim[0],ylim[1]-ylim[0],10*(zlim[1]-zlim[0])))

        # Show the plot``
        if path is not None:
            plt.savefig(f"{path}/heightmap.png")
            self.heights.to_csv(f"{path}/heightmap_data.csv", index=False)
        else:
            plt.show()

        # delete object
        del self.heights
        self.heights = pd.DataFrame(columns=["x", "y", "d"])
    
    def plot_base_scan(self, path=None):
        """Creates a 2D height plot from base scan"""
        # clear matplotlib
        plt.cla()
        plt.clf()
        # Generate data:
        # x, y, z = 10 * np.random.random((3,10))
        df = self.heights[::20].dropna()
        df.to_csv(f"{path}/base_scan_data.csv", index=False)
        x, y, z = df["x"].to_numpy(), df["y"].to_numpy(), (self.upper_distance - df["d"].to_numpy())

        # Set up a regular grid of interpolation points
        xi, yi = np.linspace(y.min(), y.max(), 100), np.linspace(x.min(), x.max(), 100)
        xi, yi = np.meshgrid(xi, yi)

        # Interpolate
        rbf = scipy.interpolate.Rbf(y, x, z, function='linear')
        zi = rbf(xi, yi)

        plt.imshow(
            zi, 
            vmin=z.min(),
            vmax=z.max(),
            origin='lower',
            extent=[y.min(), y.max(), x.min(), x.max()]
        )

        # plt.scatter(y, x, c=z)
        
        # Show the plot
        if path is not None:
            plt.rcParams["figure.figsize"] = (10,6)

            plt.tight_layout()
            plt.margins(0)
            plt.xlim(0, 600)
            plt.ylim(1000, 0)
            plt.tick_params(
                left = False,
                right = False,
                bottom = False,
                top = False,
                labelleft = False,
                labelbottom = False,
            )

            plt.savefig(f"{path}/base_scan.png", bbox_inches="tight", pad_inches=0)
            # reset the fig size
            plt.rcParams["figure.figsize"] = (15,15)
        else:
            plt.colorbar()
            plt.show()

        # delete object
        del self.heights
        self.heights = pd.DataFrame(columns=["x", "y", "d"])

    def get_picture_positions(self, cord1, cord2, step_x, step_y, margin=0, threshold=5):
        '''
        Generate a DataFrame containing the positions and depths of a picture.

        Arguments:
            cord1 (tuple): A tuple of length 2 representing the (x, y) coordinates of the top-left corner of the image.
            cord2 (tuple): A tuple of length 2 representing the (x, y) coordinates of the bottom-right corner of the image.
            step_x (float): The step size between each point in the image along x-axis.
            step_y (float): The step size between each point in the image along y-axis.
            margin (float): Default 0, take all height points that lay outside the image by margin into acount
            threshold (float): Default 5, make dicision boundry of all removed data poinst based on this threshold.
        Returns:
            DataFrame: A DataFrame with columns "x", "y", "z_start", and "z_amount", where "x" and "y" are the coordinates of
            the points in the image, "z_start" is the starting depth for the image, and "z_amount" is the number of depths for
            the image.
        '''
        # Make a copy of the heights DataFrame
        corr_heights = self.heights.copy(deep=True)
        print("Threshold", threshold, "Min", corr_heights["d"].min(), "SUM", corr_heights["d"].min() + threshold)
        corr_heights = corr_heights[corr_heights["d"] <= (corr_heights["d"].min() + threshold)]
        # Correct the x and y coordinates to align with the image
        corr_heights["x"] = corr_heights["x"] - self.x_diff
        corr_heights["y"] = corr_heights["y"] - self.y_diff

        # Initialize a new DataFrame to store the positions and depths of the picture
        picture_df = pd.DataFrame(columns=["x", "y", "z_start", "z_amount"])

        x_loop = np.arange(cord1[0], cord2[0], step_x)
        x_loop = (x_loop if not x_loop.size == 0 else [cord1[0]]) # correct for only 1 col

        y_loop = np.arange(cord1[1], cord2[1], step_y)
        y_loop = (y_loop if not y_loop.size == 0 else [cord1[1]]) # correct for only 1 row

        for x in x_loop:
            for y in y_loop:
                # Select only the heights that are within the image
                img_heights = corr_heights.loc[
                        (corr_heights["x"] >= x-self.camera_dim_x-margin) &
                        (corr_heights["x"] <= x+self.camera_dim_x+margin) &
                        (corr_heights["y"] >= y-self.camera_dim_y-margin) &
                        (corr_heights["y"] <= y+self.camera_dim_y+margin)
                ]

                # if img_heights is empty go to next
                # make sure that at least 2 datapoints are used to create image
                if len(img_heights) > 2:
                    # Calculate the starting depth and the number of depths for the image
                    # # Is (img_heights["d"].min() - self.camera_focus) is normaly the calculated z_start
                    # # but we add self.camera.dof as extra safety
                    # z_start = img_heights["d"].min() - self.camera_focus - self.camera_dof
                    # # z_amount is calulated by: difference in height divided by DOF.
                    # # The +2 to z_amount is added as extra safety measure, strictly speaking it doesn't needed to be added
                    # z_amount = int(np.ceil((img_heights["d"].max() - img_heights["d"].min())/(self.camera_dof))) + 2

                    ## Alternative without safety:
                    z_start = img_heights["d"].min() - self.camera_focus + self.camera_dof/2
                    z_amount = int(np.ceil((img_heights["d"].max() - img_heights["d"].min())/(self.camera_dof)))

                    picture_df.loc[len(picture_df)] = [round(x, 2), round(y, 2), z_start, z_amount]

        # Convert the data types of the columns in the picture DataFrame
        picture_df = picture_df.astype({"x":"float64", "y":"float64", "z_start":"float64", "z_amount":"int64"})
        print(picture_df)
        return picture_df

def main():
    hmap = HeightMap()
    hmap.add_point((0, 0, 0))
    hmap.add_point((1, 0, 1))
    hmap.add_point((0, 1, 1))
    hmap.add_point((1, 1, 2))
    hmap.plot_points()

if __name__ == '__main__':
    main()
