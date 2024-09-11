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

import pymongo
from bson.json_util import dumps
import json
from datetime import datetime
import bson
import pickle
import numpy as np
import copy

# connection string is hard coded need to to change
class image_store:
    def __init__(self, conn_str):
        # connect to database
        self.dbclient = pymongo.MongoClient(conn_str)
        self.db = self.dbclient["images"]
        # self.change_stream = self.db.watch([{'$match': {'operationType': 'insert'}}])
        self.change_stream = self.db.watch(full_document='updateLookup') # receive the full document on change

    def find_images_by_date(self, date_str):
        images_dict = self.db.posts.find_one({'date': date_str})
        print(images_dict)
        return images(images_dict)

    def export_to_json(self, date_str):
        '''
        Export the last stored image to json file
        '''
        cursor = self.db.posts.find({'date': date_str})
        with open(f'./{date_str}.json', 'w') as file:
            json.dump(json.loads(dumps(cursor)), file)

    def update_images(self, new_images):
        new_images = copy.deepcopy(new_images)
        delattr(new_images, "_id")
        if hasattr(new_images, "sources"):
            new_images.sources = bson.Binary(pickle.dumps(new_images.sources, protocol=2))
        if hasattr(new_images, "stacked_sources"):
            new_images.stacked_sources = bson.Binary(pickle.dumps(new_images.stacked_sources, protocol=2))
        if hasattr(new_images, "stitched_sources"):
            new_images.stitched_sources = bson.Binary(pickle.dumps(new_images.stitched_sources, protocol=2))

        self.db.posts.find_one_and_update(
                {
                    'date': new_images.date,
                    'name': new_images.name
                },
                {
                    '$set': new_images.__dict__
                },
        )

    def drop_db(self):
        '''
        function clears the database
        only for development reasons
        '''
        self.db.dropDatabase()
    
    def delete_image_from_db(self, date, name):
        try:
            result = self.db.posts.delete_one({"date": date, "name": name})

            if result.deleted_count == 1:
                print(f"Document with {date} and name {name} is removed")
                return f"{date}, {name} was removed."
            else:
                print("Nothing is deleted check if date an name exits.")
                return "Nothing was removed!"
        
        except Exception as e:
            print("An error occurred:", str(e))

            return "An error occured: " + str(e)

class images:
    def __init__(self, dict_img={}):
        self.name = "Nameless"
        self.date = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        self.camera = "Dummy Camera"
        self.start_x = 0.0
        self.start_y = 0.0
        self.increment_x = 0.0
        self.increment_y = 0.0
        self.overlap = 0.0
        self.focus_stacked = False
        self.correction = False
        self.stitched = False
        self.start_path = ""
        self.sources = None
        self.stacked_sources = None
        self.stitched_sources = None
        self.blending = "OVERLAY"

        for key in dict_img:
            setattr(self, key, dict_img[key])
        if hasattr(self, "sources") and self.sources != None:
            self.sources = pickle.loads(self.sources)
        if hasattr(self, "stacked_sources") and self.stacked_sources != None:
            self.stacked_sources = pickle.loads(self.stacked_sources)
        if hasattr(self, "stitched_sources") and self.stitched_sources != None:
            self.stitched_sources = pickle.loads(self.stitched_sources)

if __name__ == '__main__':
    store = image_store("mongodb://localhost:27017/")
    print("done")
    # test_date_str = "15_02_2023_14:40:42"
    # test_date_str = "21_02_2023_16:41:49"
    # test_date_str = "21_02_2023_16:46:20"

    # test_date_str = "21_02_2023_17:16:09"
    # test_date_str = "22_02_2023_17:40:04"
    # test = store.find_images_by_date(test_date_str)

    # print(test.sources[0][0])

    # store.export_to_json(test_date_str)