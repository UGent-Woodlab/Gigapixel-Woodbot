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

import pymongo
from bson.json_util import dumps
import json
from datetime import datetime
import bson
import pickle
import numpy as np

class image_store:
    def __init__(self, conn_str):
        # connect to database
        self.dbclient = pymongo.MongoClient(conn_str)
        self.db = self.dbclient["images"]

    def post_images(self, image_post):
        print(image_post.sources)
        image_post.sources = bson.Binary(pickle.dumps(image_post.sources, protocol=2))
        image_post.stacked_sources = bson.Binary(pickle.dumps(image_post.stacked_sources, protocol=2))
        print(image_post.__dict__)
        id = self.db.posts.insert_one(image_post.__dict__).inserted_id
        print("posted with id", id)
        return id

    def find_images_by_date(self, date_str):
        images_dict = self.db.posts.find_one({'date': date_str})
        return images(images_dict)

    def export_to_json(self, date_str):
        '''
        Export the last stored image to json file
        '''
        cursor = self.db.posts.find({'date': date_str})
        with open(f'./{date_str}.json', 'w') as file:
            json.dump(json.loads(dumps(cursor)), file)

    def import_from_json(self, json_path):
        '''
        open json file and return images object and store to db
        '''
        with open(json_path, 'r') as file:
            json_dict = bson.json_util.loads(file.read())
        json_dict = json_dict[0]
        return images(json_dict)

    def drop_db(self):
        '''
        function clears the database
        only for development reasons
        '''
        self.db.dropDatabase()

class images:
    def __init__(self, dict_img={}):
        if dict_img == {}:
            self.name = ""
            self.date = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
            self.start_x = 0.0
            self.start_y = 0.0
            self.increment_x = 0.0
            self.increment_y = 0.0
            self.overlap = 0.0
            self.focus_stacked = False
            self.correction = False
            self.stitched = False
            self.start_path = ""
            self.camera = "Dummy Camera"
            self.sources = None
            self.stacked_sources = None
            self.corrected_sources = None
            self.blending = "LINEAR"
        else:
            for key in dict_img:
                setattr(self, key, dict_img[key])
            if hasattr(self, "sources"):
                self.sources = pickle.loads(self.sources)
            if hasattr(self, "stacked_sources"):
                self.stacked_sources = pickle.loads(self.stacked_sources)
            if hasattr(self, "stitched_sources"):
                self.stitched_sources = pickle.loads(self.stitched_sources)
