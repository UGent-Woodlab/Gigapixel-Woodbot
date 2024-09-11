FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y upgrade \
  && apt-get install -y \
    apt-utils \
    unzip \
    tar \
    curl \
    xz-utils \
    ocl-icd-libopencl1 \
    opencl-headers \
    clinfo

# install python
RUN apt-get -y update && \ 
    apt-get -y install software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get -y install python3.10 python3-pip

RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

ENV TZ=Europe/Brussels
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y \
    tzdata \
    git \
    build-essential \
    libopencv-dev \
    ocl-icd-opencl-dev \
    # nvidia-opencl-icd \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth=1 https://github.com/PetteriAimonen/focus-stack.git

RUN make -C focus-stack

RUN make install -C focus-stack

RUN pip install --upgrade pip

RUN pip install flask
RUN pip install flask-cors

CMD ["focus-stack"]
# CMD ["python3", "focus_stack_rest.py"]