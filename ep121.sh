#!/usr/bin/env sh

## Fix Bluetooth applet/service
# note: on board bluetooth seems to still lacks kernel driver .. or something ..

# replace buggy bluez 4.91 with 4.60
sudo apt-get purge bluez
wget http://archive.ubuntu.com/ubuntu/pool/main/b/bluez/bluez_4.60-0ubuntu8_amd64.deb
sudo dpkg -i ./bluez_4.60-0ubuntu8_amd64.deb
# reinstall applet
sudo apt-get install gnome-bluetooth
# prevent bluez from upgrading
echo "bluez hold" | sudo dpkg --set-selections


## Fix touch screen

# install "driver" in user's bin folder
wget --no-check-certificate https://github.com/cskau/EP121-fixes-for-Ubuntu-11.04-Natty/raw/master/ep121_drv.py -P ~/bin/
# grant the driver read access to input devices
echo "SUBSYSTEM==\"input\", MODE=\"644\"" | sudo tee -a /etc/udev/rules.d/85-ep121.rules
# make sure the driver runs at start up (log in)
echo "ep121_drv.py &" >> ~/.profile


## Add hot keys

# We might want to fiddle with this at some point
# would be nice to get proper keybindings for them

# Rotation
#echo "0xF5 prog1" >> /lib/udev/keymaps/asus
# Screen
#echo "0xF6 f21 # Toggle touchpad" >> /lib/udev/keymaps/asus
# Keyboard
#echo "0xF7 bluetooth" >> /lib/udev/keymaps/asus
