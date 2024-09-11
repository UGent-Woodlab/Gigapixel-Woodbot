FROM ubuntu:20.04
FROM python:3.10

# Setup user
ARG USER=docker
ARG UID=1000
ARG GID=1000
ARG PW=docker

# add user and set password
RUN useradd -m ${USER} --uid=${UID} && echo "${USER}:${PW}" | chpasswd && adduser ${USER} sudo

# update the packages
RUN apt update -y
# install dependencies for GigE framework and install ping, sudo and other essenstials
RUN apt install -y \
        sudo \
        apt-utils \
        gcc \
        g++ \
        git \
        gphoto2 \
        make \
        build-essential \
        libx11-dev \
        libxext-dev \
        libgtk-3-dev \
        libglade2-0 \
        libglade2-dev \
        libpcap0.8 \
        libcap2 \
        ethtool \
        iputils-ping \
        coreutils \
        unzip \
        libusb-1.0-0 \
        libxcb-* \
        libxkbcommon-x11-0 \
        net-tools \
        wget \
        unzip \
        usbutils \
        libexif12 \
        libgphoto2-6 \
        libgphoto2-dev \
        libltdl7 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        lsb-release \
        libfreetype6 \
        libfontconfig1 \
        ttf-bitstream-vera

RUN wget http://archive.ubuntu.com/ubuntu/pool/main/g/glibc/multiarch-support_2.27-3ubuntu1_amd64.deb
RUN apt-get install -y ./multiarch-support_2.27-3ubuntu1_amd64.deb

COPY ./.container_build/. /tmp/.

# change to user
# disable sudo password
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# UNZIP cvb software
RUN printf '#!/bin/sh\nexit 0' > /usr/sbin/policy-rc.d
# WORKDIR /home/${USER}/
RUN mkdir /tmp/cvb/
RUN mv /tmp/cvb-14.00.002-ubu2004-x86_64.zip /tmp/cvb/cvb-14.00.002-ubu2004-x86_64.zip
RUN mv /tmp/codemeter_7.60.5598.500_amd64.deb /tmp/cvb/codemeter_7.60.5598.500_amd64.deb
RUN cd /tmp/cvb \
  && unzip cvb-14.00.002-ubu2004-x86_64.zip \
  && dpkg --unpack codemeter_7.60.5598.500_amd64.deb \
  && rm /var/lib/dpkg/info/codemeter.postinst \
  && dpkg --configure codemeter \
  && dpkg --unpack cvb-camerasuite-14.00.002-ubu2004-x86_64.deb \
  && rm /var/lib/dpkg/info/cvb-camerasuite.postinst \
  && dpkg --configure cvb-camerasuite \
  && dpkg --unpack cvb-camerasuite-dev-14.00.002-ubu2004-x86_64.deb \
  && dpkg --configure cvb-camerasuite-dev \
  && ldconfig \
  && ln -s /opt/cvb-14.00.002/ /opt/cvb  \
  && dpkg -I cvb-foundation-14.00.002-ubu2004-x86_64.deb \
  && dpkg -I cvb-foundation-dev-14.00.002-ubu2004-x86_64.deb \
  && dpkg -I cvb-tools-14.00.002-ubu2004-x86_64.deb \
  && dpkg -I cvb-tools-dev-14.00.002-ubu2004-x86_64.deb

USER ${USER}
# set python environemnt en upgrade pip
ENV PATH "$PATH:$HOME/.local/bin"
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --upgrade pip
# get requirements file and isntall dependencies

# ignore pygigev -> gives error because gigev framework isn't installed
RUN grep -vE "(pygigev)" /tmp/requirements.txt | xargs pip install

# USER root
# ENV HOME_D /home/${USER}
# unpack gigev tar
# RUN mkdir $HOME/gigev/
# RUN tar -zxf $HOME_D/GigE-V-Framework_x86_2.20.0.0182.tar.gz -C $HOME_D

# install gigev framework
# ENV TDY_INSTALL_MODE "Silent"
# RUN cd $HOME_D/DALSA/ && sudo -E ./corinstall
# RUN cd $HOME_D && rm -rf $HOME_D/gigev

# USER ${USER}
# ENV GENICAM_ROOT /opt/genicam_v3_0
# ENV GENICAM_ROOT_V3_0 /opt/genicam_v3_0
# ENV GENICAM_CACHE /var/opt/genicam/xml/cache
# ENV GENICAM_CACHE_V3_0 /var/opt/genicam/xml/cache
# ENV GENICAM_LOG_CONFIG /opt/genicam_v3_0/log/config-unix
# ENV GENICAM_LOG_CONFIG_V3_0 /opt/genicam_v3_0/log/config-unix
# ENV GIGEV_DIR /usr/dalsa/GigeV
# ENV GIGEV_XML_DOWNLOAD /usr/dalsa/GigeV

# ENV GigE variables
# RUN . $HOME/gigev-exports
# RUN cat $HOME/gigev-ENVs >> home/$USER/.bashrc
# RUN . $HOME/.bashrc

# install python GigE (pygigev)
# RUN grep -E "(pygigev)" $HOME/requirements.txt | xargs pip install



# set workspace
RUN  mkdir $HOME/aqcuisition
WORKDIR $HOME/acquisition

# copy local folder to workspace
COPY acquisition-py/. .

EXPOSE 8080

CMD /opt/cvb-14.00.002/bin/siLogSvc -s && \
    /opt/cvb-14.00.002/bin/cvmgmtd && \
    /opt/cvb-14.00.002/bin/siGevSvc -s && \
    . /etc/profile.d/cvb_environment.sh
# run main program
# CMD [ "python", "acquisition.py" ]
