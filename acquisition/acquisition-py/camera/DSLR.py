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

from .Camera import Camera
import gphoto2 as gp

class DSLR(Camera):
    def __init__(self, *args):
        # self.config = args[0] # currently not used
        self.reset()

    def __del__(self):
        self.camera.exit()
        del self.camera
    
    def reset(self):
        self.camera = gp.Camera()
        self.camera.init()

        print('Summary')
        print('=======')
        print(str(self.camera.get_summary()))

    # Overwrite the take_picture function
    def take_picture(self, file_path):
        try:
            # try capturing the image
            image_capture = self.camera.capture(gp.GP_CAPTURE_IMAGE)

            image_file = self.camera.file_get(image_capture.folder, image_capture.name, gp.GP_FILE_TYPE_NORMAL)
            image_file.save(file_path)

            print(f"Took image and saved it on {file_path}, image detail {image_capture.folder}")

        except gp.GPhoto2Error as ex:
            print(f"An erorr occurred: {str(ex)}")
            # exit the camera and reset
            self.camera.exit()
            self.reset()
            # try taking the picture again
            self.take_picture(file_path)

if __name__ == '__main__':
    camera = DSLR()
    camera.take_picture("./test.png")