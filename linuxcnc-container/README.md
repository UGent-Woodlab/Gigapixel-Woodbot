# How to start the linuxcnc container?

first the the PCI-e ports need to be enabled
``` shell
sudo echo 1 > /sys/bus/pci/devices/0000:82:00.2/enable
```
Second start the dockercontainer
