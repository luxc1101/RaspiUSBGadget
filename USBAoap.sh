#!/bin/bash
cd /sys/kernel/config/usb_gadget/
sudo mkdir -p g2
cd g2
sudo bash -c 'echo "" > UDC'
sudo bash -c "echo '0x18d1' > idVendor" # VID
sudo bash -c "echo '0x2d00' > idProduct" # PID
sudo bash -c "echo '0x0100' > bcdDevice" # v1.0.0
sudo bash -c "echo '0x0200' > bcdUSB" # USB2
sudo mkdir -p strings/0x409
sudo bash -c "echo 'fedcba9876543210' > strings/0x409/serialnumber"
sudo bash -c "echo 'SWTE Media' > strings/0x409/manufacturer"
sudo bash -c "echo 'SWTE USB Device' > strings/0x409/product"
sudo mkdir -p configs/c.1/strings/0x409
sudo bash -c "echo 'Config 1' > configs/c.1/strings/0x409/configuration"
sudo bash -c "echo '250' > configs/c.1/MaxPower"
# <<com
# Add functions here
sudo mkdir -p functions/mass_storage.usb0
sudo ln -s functions/mass_storage.usb0 configs/c.1/
# End functions
# com
name="$(ls /sys/class/udc)"
sudo bash -c "echo $name > UDC"