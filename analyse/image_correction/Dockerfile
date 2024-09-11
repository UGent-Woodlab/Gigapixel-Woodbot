# Use Ubuntu 22.04 as the base image
ARG CUDA_VERSION=11.7.0
ARG CUDNN_VERSION=8
ARG UBUNTU_VERSION=20.04

# FROM nvidia/cuda:${CUDA_VERSION}-cudnn${CUDNN_VERSION}-devel-ubuntu${UBUNTU_VERSION}
FROM ubuntu:${UBUNTU_VERSION}

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy any necessary files to the container (if applicable)
COPY . /app

# Install basicpy using pip
RUN pip3 install -r /app/requirements.txt

# Set the working directory to /app
WORKDIR /app

ENTRYPOINT ["/bin/bash"]

# CMD ["python3", "correction_rest.py"]