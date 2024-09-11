ARG CUDA_VERSION=11.7.0
ARG CUDNN_VERSION=8
ARG UBUNTU_VERSION=20.04

# FROM nvidia/cuda:${CUDA_VERSION}-cudnn${CUDNN_VERSION}-devel-ubuntu${UBUNTU_VERSION}

FROM ubuntu:20.04

ARG PYTHON_VERSION=3.9
ARG OPENCV_VERSION=4.6.0

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && \
    apt-get -qq install  \
#   python :
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        libpython${PYTHON_VERSION} \
        libpython${PYTHON_VERSION}-dev \
        python-dev \
        python3-setuptools \
#   developement tools, opencv image/video/GUI dependencies, optimiztion packages , etc ...  :
        apt-utils \
        autoconf \
        automake \
        checkinstall \
        cmake \
        gfortran \
        git \
        libatlas-base-dev \
        libavcodec-dev \
        libavformat-dev \
        libavresample-dev \
        libeigen3-dev \
        libexpat1-dev \
        libglew-dev \
        libgoogle-glog-dev \
        libgtk-3-dev \
        libjpeg-dev \
        libopenexr-dev \
        libpng-dev \
        libpostproc-dev \
        libpq-dev \
        libqt5opengl5-dev \
        libsm6 \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libtiff-dev \
        libtool \
        libv4l-dev \
        libwebp-dev \
        libxext6 \
        libxrender1 \
        libxvidcore-dev \
        ocl-icd-opencl-dev \
        pkg-config \
        protobuf-compiler \
        qt5-default \
        tzdata \
        unzip \
        wget \
        yasm \
        zlib1g-dev \
#   GStreamer :
        libgstreamer1.0-0 \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-libav \
        gstreamer1.0-doc \
        gstreamer1.0-tools \
        gstreamer1.0-x \
        gstreamer1.0-alsa \
        gstreamer1.0-gl \
        gstreamer1.0-gtk3 \
        gstreamer1.0-qt5 \
        gstreamer1.0-pulseaudio \
        libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get purge   --auto-remove && \
    apt-get clean


# install new pyhton system wide :
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 2 && \
    update-alternatives --config python3

# numpy for the newly installed python :
RUN wget https://bootstrap.pypa.io/get-pip.py  && \
    python${PYTHON_VERSION} get-pip.py --no-setuptools --no-wheel && \
    rm get-pip.py && \
    pip install numpy

RUN mkdir /opt/build
COPY ./.container_build/. /opt/build/.

# uncomment following line /opt/opencv-${OPENCV_VERSION}/modules/imgproc/src/imgwarp.cpp
# opencv and opencv-contrib :
# RUN cd /opt/ &&\
#     wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip -O opencv.zip &&\
#     unzip -qq opencv.zip &&\
#     rm opencv.zip &&\
#     wget https://github.com/opencv/opencv_contrib/archive/${OPENCV_VERSION}.zip -O opencv-co.zip &&\
#     unzip -qq opencv-co.zip &&\
#     rm opencv-co.zip &&\
#     mv -f /opt/build/imgwarp.cpp /opt/opencv-${OPENCV_VERSION}/modules/imgproc/src/imgwarp.cpp &&\
#     mkdir /opt/opencv-${OPENCV_VERSION}/build && cd /opt/opencv-${OPENCV_VERSION}/build &&\
#     cmake \
#       -D BUILD_opencv_java=OFF \
#       -D WITH_CUDA=ON \
#       -D BUILD_opencv_dnn=ON \
#       -D CUDA_ARCH_BIN=8.6 \
#       -D CUDA_ARCH_PTX=8.6 \
#       -D WITH_CUBLAS=ON \
#       -D WITH_CUDNN=ON \
#       -D OPENCV_DNN_CUDA=ON \
#       -D ENABLE_FAST_MATH=1\
#       -D CUDA_FAST_MATH=1\
#       -D WITH_NVCUVID=ON \
#       -D WITH_CUFFT=ON \
#       -D WITH_OPENGL=ON \
#       -D WITH_QT=ON \
#       -D WITH_IPP=ON \
#       -D WITH_TBB=ON \
#       -D WITH_EIGEN=ON \
#       -D CUDA_NVCC_FLAGS=-Wno-deprecated-gpu-targets \
#       -D CMAKE_BUILD_TYPE=RELEASE \
#       -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib-${OPENCV_VERSION}/modules \
#       -D PYTHON2_EXECUTABLE=$(python${PYTHON_VERSION} -c "import sys; print(sys.prefix)") \
#       -D CMAKE_INSTALL_PREFIX=$(python${PYTHON_VERSION} -c "import sys; print(sys.prefix)") \
#       -D PYTHON_EXECUTABLE=$(which python${PYTHON_VERSION}) \
#       -D PYTHON_INCLUDE_DIR=$(python${PYTHON_VERSION} -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
#       -D PYTHON3_PACKAGES_PATH=/usr/lib/python${PYTHON_VERSION}/dist-packages \
#       -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda-11.7 \
#       -D CMAKE_LIBRARY_PATH=/usr/local/cuda/lib64/stubs \
#       -D OPENCV_GENERATE_PKGCONFIG=YES \
#         .. &&\
#     make -j$(nproc) && \
#     make install && \
#     ldconfig
# # &&\
# #     rm -rf /opt/opencv-${OPENCV_VERSION} && rm -rf /opt/opencv_contrib-${OPENCV_VERSION}

# ENV NVIDIA_DRIVER_CAPABILITIES all
# ENV XDG_RUNTIME_DIR "/tmp"

# # FROM thecanadianroot/opencv-cuda:ubuntu20.04-cuda11.3.1-opencv4.5.2
# # FROM nvidia12.0.1-devel-ubuntu22.04
# # FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}
# # FROM thecanadianroot/opencv-cuda:pr-8-${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}

# RUN pkg-config --libs opencv4

# SET TIMEZONE
ENV TZ=Europe/Brussels
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# STITCHING
# 4.5.4.60
# copy container build files

# PYTHON APPLICATION
# setup python environmt en upgrade pip
ENV PATH "$PATH:$HOME/.local/bin"

# RUN wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -
# RUN apt update
# RUN apt install -y libllvm-12-ocaml-dev libllvm12 llvm-12 llvm-12-dev llvm-12-doc llvm-12-examples llvm-12-runtime
# ARG LLVM_VERSION=12
# RUN wget --no-check-certificate -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -
# RUN add-apt-repository 'deb http://apt.llvm.org/focal/   llvm-toolchain-focal-10  main'
# RUN add-apt-repository 'deb http://apt.llvm.org/jammy/   llvm-toolchain-jammy  main'
# RUN apt-get update && apt-get install -y \
    # libedit-dev  \
    # llvm-${LLVM_VERSION} \
    # llvm-${LLVM_VERSION}-dev
# ARG LLVM_CONFIG=/usr/bin/llvm-config-${LLVM_VERSION}
RUN python3 -m pip install --upgrade pip

# install all python requirements
RUN pip install -r /opt/build/requirements.txt

# FOCALS IMAGE STACKING
# libopencv-dev ocl-icd-opencl-dev
# RUN add-apt-repository ppa:graphics-drivers/ppa
# RUN apt update && \
    # rm -rf /var/lib/apt/lists/*

# RUN git clone --depth=1 https://github.com/PetteriAimonen/focus-stack.git

# RUN apt-get update -y
# RUN apt-get install -y clinfo vim

# RUN make -C focus-stack
# RUN make install -C focus-stack

# setup workspace
RUN echo $HOME
RUN mkdir $HOME/analyse
WORKDIR $HOME/analyse

COPY analyse-py/. .

# start script
# ENTRYPOINT ["echo", "start container"]