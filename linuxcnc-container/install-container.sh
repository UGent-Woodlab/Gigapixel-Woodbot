#!/bin/bash

# first clone container setup from git
git clone https://github.com/MachineKoderCompany/linuxcnc-mt-docker

# copy new files 
cp -af ./docker/. ./linuxcnc-mt-docker/docker/.

cd linuxcnc-mt-docker/docker
