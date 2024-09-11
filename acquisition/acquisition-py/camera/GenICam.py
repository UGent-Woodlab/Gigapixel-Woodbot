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

from harvesters.core import Harvester
from harvesters.util.pfnc import *
import cv2
from .Camera import Camera

class GenICam(Camera):
    def __init__(self, *args):
        self.config = args[0]

        self.h = Harvester()
        self.h.add_file(self.config["GENICAM_CTI_PATH"])
        self.h.update()

        print(len(self.h.device_info_list))
        print(self.h.device_info_list[0])

        self.ia = self.h.create(0)

    def __del__(self):
        self.ia.destroy()

        self.h.reset()

    # Override the take_picture function
    def take_picture(self, file_path):
        self.ia.start(run_as_thread=True)
        with self.ia.fetch() as buffer:
            component = buffer.payload.components[0]
            _2d = component.data.reshape(
                    component.height, component.width
            )

            cv2.imwrite(file_path, cv2.cvtColor(_2d, cv2.COLOR_BAYER_BG2BGR))
        self.ia.stop()
