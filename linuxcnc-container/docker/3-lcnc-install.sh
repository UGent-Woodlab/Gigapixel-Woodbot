# Add the LinuxCNC Archive Signing Key to your apt keyring by running 
apt-key adv --keyserver hkp://keyserver.ubuntu.com --recv-key 3cb9fd148f374fef

# Add the apt repository
echo deb http://linuxcnc.org/ buster base 2.8-rtpreempt | sudo tee /etc/apt/sources.list.d/linuxcnc.list
echo deb-src http://linuxcnc.org/ buster base 2.8-rtpreempt | sudo tee -a /etc/apt/sources.list.d/linuxcnc.list

# upgrade and update the machine
apt-get update -y
apt-get upgrade -y

apt-get install zsync -y

# install linuxcnc and mesaflash
apt-get install linuxcnc-uspace -y
apt install mesaflash -y
