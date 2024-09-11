import requests
import json

url = "http://127.0.0.1:5004"
date = "15_03_2023_15_21_11"
path_in = f"/image-document-store/db/{date}/fiji"
path_out = f"/image-document-store/db/{date}/corrected"

data = {
    "path_input": path_in,
    "path_output": path_out,
}

# get current threads:
def fetch_threads():
    print ("==================[ THREAD OVERVIEW ]===================")
    response = requests.get(f"{url}/threads")
    threads = response.json()
    print(threads)

    # print("Active threads:")
    # for thread in threads:
    #     if thread["status"] == "running":
    #         print(f"Thread {thread['id']} is running.")

    print ("========================================================")

# first check if there are any active threads
fetch_threads()

# start a correction job in thread
response = requests.post(f"{url}/correction", data=data)
print(response.text)

# check if there are any active threads
fetch_threads()