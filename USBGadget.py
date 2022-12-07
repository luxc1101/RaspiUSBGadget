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
import json
import msvcrt
import os
import sys
from subprocess import PIPE, Popen, check_output, run

##########################
#       Paramters        #
##########################n
# color
Cyan = '\033[1;96m'
Yellow = '\033[1;93m'
Green = '\033[1;92m'
Red = '\033[1;91m'
C_off = '\033[0m'
# logging
# create stdolog file
logfile = "Gadget.log"
stdolog = open(os.path.join(os.getcwd(),logfile), 'a')
# clear stdolog file
stdolog = open(os.path.join(os.getcwd(),logfile), 'w')
# cd RaspiUSBGadget && sudo rm USBGadget.py && sudo nano USBGadget.py
global numdev 
numdev = {}
##########################
#       Functions        #
##########################
## menu
# read the device.json file and fill it
def menu(file):
    # def esc():
    #     if msvcrt.getch() == chr(27):
    #         aborted = True  
    def Input(str):
        print(str)
        key = msvcrt.getch().decode('ASCII')
        print(Green + key + C_off)
        return key
    
    def root():
        ## showing device type (root)
        print(Cyan + "all emulatable deive wie following: " + C_off)
        for id, key in enumerate(device_dict.keys()):
            print('{}: {}'.format(id, key))
            # emulatable device dict
            numdev[str(id)] = key
        return numdev

    def secondlayer(Input0):
        global Input1 
        Input1 = Input(str = Cyan + "Enter the device type or : " + C_off)
        try:
            for key in device_dict[Input0[Input1]].keys():
                if key == "0":
                    print('{}: supported'.format(key))
                if key == "1":
                    print('{}: unsupported'.format(key))
            print("r: return")
            return Input1 
        except:
            secondlayer(Input0)

    def thirdlayer(Input1):
        global Input2
        Input2 = Input(str = Cyan + "{} Supported (0) or Unsupported (1) or return: ".format(numdev[Input1]) + C_off)
        try:
            if Input2 == "r":
               return thirdlayer(secondlayer(root()))
            else: 
                for id, dev in enumerate(device_dict[numdev[Input1]][Input2]):
                    print(str(id) + '. ' +  dev["dev"] + ':' + ' ' + dev["VID"] + ' ' +  dev["PID"])
                print("r: return")
                return Input2
        except:
            thirdlayer(Input1) 

    def fourthlayer(Input2):
        global Input3
        Input3 = Input(str = Cyan + "Enter the device number or return: " + C_off)
        try:
            if Input3 == "r":
                return fourthlayer(thirdlayer(Input1))
            else:
                for id, dev in enumerate(device_dict[numdev[Input1]][Input2]):
                    if str(id) == str(Input3):
                        print(str(id) + '. ' +  dev["dev"] + ':' + ' ' + dev["VID"] + ' ' +  dev["PID"])
                        print("r: return")
                        break
                return fourthlayer(Input2)
        except: 
            return fourthlayer(Input2)

    with open(os.path.join(os.getcwd(), file), 'r', encoding="utf-8") as f:
        device_dict = json.load(f)
        f.close()

    # root()
    # Output1 = secondlayer(root())
    fourthlayer(thirdlayer(secondlayer(root())))
    # try:
    #     for key in device_dict[numdev[Input1]].keys():
    #         if key == "0":
    #             print('{}: supported'.format(key))
    #         if key == "1":
    #             print('{}: unsupported'.format(key))
    #     print("r: return")
    # except:
    #     Input1
    ## Input 0 or 1 or return
    # Input2 = Input(str = Cyan + "Supported (0) or Unsupported (1) : " + C_off)
    # # Input2 = input(Cyan + "{}".format(msvcrt.getch().decode('ASCII')) + C_off)
    # ## showing all supported or unsupported devices root/sup or usup/devs
    # for id, dev in zip(range(0,len(device_dict[Input1][Input2])),device_dict[Input1][Input2]):
    #     print(str(id) + '. ' +  dev["dev"] + ':' + ' ' + dev["VID"] + ' ' +  dev["PID"])
    # print("ESC")
    # ## Input selected deive
    # print(Cyan + "Enter the device number: " + C_off)
    # Input3 = msvcrt.getch().decode('ASCII')
    # ## showing selected deivce root/sup or usup/devs/dev
    # for id, dev in enumerate(device_dict[Input1][Input2]):
    #     if str(id) == str(Input3):
    #         print(str(id) + '. ' +  dev["dev"] + ':' + ' ' + dev["VID"] + ' ' +  dev["PID"])
    #         break


    # print(len(device_dict))
    # for keys, values in device_dict.items():
    #     print(keys)
    #     for key, devs in values.items():
    #         print(key)
    #         for dev in devs:
    #             devname = dev["dev"]
    #             VID = dev["VID"]
    #             PID = dev["PID"]
    #             print(devname + ':' + ' ' +VID + ' ' +  PID)
            
        






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
    # reqcheck()
    menu(file='device.json')
    stdolog.close()
    
