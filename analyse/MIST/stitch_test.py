import requests
import json

url = "http://127.0.0.1:5005"
date = "15_03_2023_15_21_11"

x_max = 16
y_max = 27 

data = {
    "grid_width": y_max,
    "grid_height": x_max,
    "start_tile_col": 0,
    "start_tile_row": 0,
    "extent_width": y_max,
    "extent_height": x_max,
    "horizontal_overlap": 40,
    "vertical_overlap": 40,
    "overlap_uncertainty": 5,
    "image_dir": f"/image-document-store/db/{date}/corrected",
    "output_path": f"/image-document-store/db/{date}/stitched",
    "output": "result.tiff",
    "filename_pattern_type": "ROWCOL",
    "filename_pattern": "corrected_tile_{r}_{c}.tiff",
    "grid_origin": "UL",
    "log_level": "INFO",
    "program_type": "CUDA"
}

response = requests.post(f"{url}/stitching", data=data)
print(response.text)