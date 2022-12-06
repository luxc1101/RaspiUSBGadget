#!/usr/bin/python3
#*****************************************************
# Project:   Raspberrypi Zero USB Gadget
# Autor:     Xiaochuan Lu
# Abteilung: SWTE
#*****************************************************
'''
A USB Linux Gadget is a device which has a UDC (USB Device Controller) and
can be connected to a USB Host to extend it with additional functions like
a serial port, Ethernet or a mass storage capability. To automatically test
the following RQs, the Ethernet adapter, Android Auto device, keyboard can
be emulated by using the Raspi USB gadget.

| RQ        | Description                                  |
| --------- | -------------------------------------------- |
| GP-38773  | Support of Defined List of Ethernet Adapters |
| GP-38777  | Support of Android Auto Devices              |
| GP-38775  | No Support of Unknown Devices                |

'''
##########################
# Import all needed libs #
##########################
import os
import sys
from subprocess import PIPE, Popen, check_output, run

##########################
#       Paramters        #
##########################
# color
Cyan = '\033[1;96m'
Yellow = '\033[1;93m'
Green = '\033[1;92m'
Red = '\033[1;91m'
C_off = '\033[0m'
# create stdolog file
stdolog = open('Gadget.log', 'a')
# clear stdolog file
stdolog = open('Gadget.log', 'w')
# sudo rm USBGadget.py && sudo nano USBGadget.py

##########################
#       Functions        #
##########################
## menu



'''
Requirements
ConfigFs must be avaiable, if it not avaiable it needs to be mounted firstly
modules and device tree also
'''
def reqcheck():
    cmdfindmnt = "findmnt | grep 'configfs'"
    status = True
    mount_OK = Popen(cmdfindmnt, shell=True, stdout=PIPE, stderr=stdolog).communicate()[0].decode('utf-8')
    if 'configfs' not in mount_OK:
        status = False
        sys.stdout.write("Checking mount status of configfs: {} \n".format(status))
        Popen('sudo mount -t configfs none /sys/kernel/config',shell=True, stdout=stdolog, stderr=stdolog)
        return reqcheck()
    sys.stdout.write("Checking mount status of configfs: {} \n".format(status))
    
    Popen("ls /sys/kernel/config/", shell=True, stdout=stdolog, stderr=stdolog)
    
    devicetree = Popen("cat /boot/config.txt", shell=True, stdout=PIPE, stderr=stdolog).communicate()[0].decode('utf-8')
    if 'dwc2' not in devicetree:
        status = False
        sys.stdout.write("Checking devicetree: {} \n".format(status))
        Popen('echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt', shell=True, stdout=stdolog, stderr=stdolog)
        return reqcheck()
    sys.stdout.write("Checking devicetree: {} \n".format('dtoverlay=dwc2'))
    
    modules = Popen("cat /etc/modules", shell=True, stdout=PIPE, stderr=stdolog).communicate()[0].decode('utf-8')
    if 'libcomposite' not in modules:
        status = False
        sys.stdout.write("Checking modules: {} \n".format(status))
        sys.stdout.write("loading libcomposite modules \n")
        Popen('modprobe libcomposite', shell=True, stdout=stdolog, stderr=stdolog)
        Popen('echo "libcomposite" | sudo tee -a /etc/modules',shell=True, stdout=stdolog, stderr=stdolog)
        return reqcheck()
    if 'dwc2' not in modules:
        status = False
        sys.stdout.write("Checking modules: {} \n".format(status))
        Popen('echo "dwc2" | sudo tee -a /etc/modules', shell=True, stdout=stdolog, stderr=stdolog)
        return reqcheck()
    sys.stdout.write("Checking modules: {} {} \n".format('libcomposite', 'dwc2'))


'''
Creating the Gadgets
'''    
    
    
    
if __name__ == "__main__":
    reqcheck()
    stdolog.close()
    
