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
import msvcrt  # windows
# import getch # linux
import os
import sys
from subprocess import PIPE, Popen, check_output, run

##########################
#       Paramters        #
##########################n
# color
Cyan    = '\033[1;96m'
Yellow  = '\033[1;93m'
Green   = '\033[1;92m'
Red     = '\033[1;91m'
C_off   = '\033[0m'
# logging
# create stdolog file
logfile = "Gadget.log"
stdolog = open(os.path.join(os.getcwd(),logfile), 'a')
# clear stdolog file
stdolog = open(os.path.join(os.getcwd(),logfile), 'w')
# cd RaspiUSBGadget && sudo rm USBGadget.py && sudo nano USBGadget.py
global numdev 
numdev  = {}
##########################
#       Functions        #
##########################
# menu
# read the device.json file and fill it
def menu(file):
    '''
    user menu
    root: list all emulatable device (read from json files)
    secondlayer: 0 supported devices 1 unsupported devices
    thirdlayer: list all 0 devices or 1 devieces
    fourthlayer: list the final selected device
    '''
    def Input(str):
        print(str)
        key = msvcrt.getch().decode('ASCII')# windows
        # key = getch.getch() # linux
        print(Green + key + C_off)
        return key
    
    def root():
        try:
            ## showing device type (root)
            print(Cyan + "all emulatable deivce wie following: " + C_off)
            for id, key in enumerate(device_dict.keys()):
                print('{}: {}'.format(id, key))
                # emulatable device dict
                numdev[str(id)] = key
            return numdev # Input 0
        except KeyboardInterrupt as e:
            print(e)

    def secondlayer(Input0):
        global Input1 
        global Func
        global Att
        Input1 = Input(str = Cyan + "Enter the device type: " + C_off)
        try:
            if Input1 == 'q':
                return
            else:
                for key in device_dict[Input0[Input1]].keys():
                    if key == "0":
                        print('{}: supported'.format(key))
                    if key == "1":
                        print('{}: unsupported'.format(key))
                    if key == "type":
                        Func = device_dict[Input0[Input1]][key]["func"]
                        Att = device_dict[Input0[Input1]][key]["attribute"]
                return Input1 
        except:
            secondlayer(Input0)

    def thirdlayer(Input1):
        global Input2
        Input2 = Input(str = Cyan + "{} Supported (0) or Unsupported (1) or return: ".format(numdev[Input1]) + C_off)
        try:
            if Input2 == "r":
               return thirdlayer(secondlayer(root()))
            elif Input2 == 'q':
                return
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
            elif Input3 == 'q':
                return
            else:
                for id, dev in enumerate(device_dict[numdev[Input1]][Input2]):
                    if str(id) == str(Input3):
                        DEV = dev["dev"]
                        VID = dev["VID"]
                        PID = dev["PID"]
                        print("{}. {}:  {} {}".format(str(id), DEV, VID, PID))
                        print("r: return")
                        # Gadget
                        #######################################################
                        print('>'*60)
                        Gadgets(DEV = DEV, VID = VID, PID = PID, FUNC = Func, ATT = Att)
                        print('<'*60)
                        #######################################################
                        break
                return fourthlayer(Input2)
        except: 
            return fourthlayer(Input2)
    # open and read device json data base
    with open(os.path.join(os.getcwd(), file), 'r', encoding="utf-8") as f:
        device_dict = json.load(f)
        f.close()

    # root()
    fourthlayer(thirdlayer(secondlayer(root())))
            
def reqcheck():
    '''
    Requirements
    ConfigFs must be avaiable, if it not avaiable it needs to be mounted firstly
    modules and device tree also
    '''
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

def Gadgets(DEV, VID, PID, FUNC, ATT):
    '''
    Creating the Gadgets
    
    try disabling the Gadget except pass
    firstly check if function in configuration folder eixited 
    ja -> remove it
    '''
    root            = "/sys/kernel/config/usb_gadget"
    udcname         = ''
    bcdDevice       = '0x0100'                          # Device release number
    bcdUSB          = '0x0200'                          # Initialize this descriptor to the usb version that the device supportes (accceptatble version are 0x0110 0x0200 0x0300 0x0310)
    bDeviceClass    = '0xEF'                            # The class code indicating the behavior of this device. 
    bDeviceSubClass = '0x02'                            # The subclass code that further defines the behavior of this device.
    bDeviceProtocol = '0x01'                            # The protocol that the device supports.
    serialnumber    = 'fedcba9876543210'                # Device serial number
    manufacturer    = 'SWTE Media'                      # Manufacturer attribute
    product         = 'SWTE Emulated multi USB Device'  # Cleartext product description
    configuration   = 'Config 1'                        # Name of this configuration
    MaxPower        = '250'                             # max power this configuration can consume in mA
    bmAttributes    = '0x80'                            # Configuration characteristics (D7: Reserved (set to one), D6: Self-powered, D5: Remote Wakeup, D4...0: Reserved (reset to zero)) 
    print('going to emulate {} device'.format(DEV))
    print(FUNC + ' ' + VID + ' ' + PID)
    print("attribute dict: " + ATT)

    # cleaning up
    if os.path.exists("{}/g1/UDC".format(root)):
        catUDC = check_output('cat {}/g1/UDC'.format(root), shell=True, encoding='utf-8').split('\n')[0]                                # cat the content of UDC 
        if 'usb' in catUDC:                                                                                                             # if usb in UDC
            Popen('sudo bash -c "echo {} > {}/g1/UDC" || echo pass'.format(udcname, root), shell=True, stdout=stdolog, stderr=stdolog)  # disable the Gadget

    if os.path.exists("{}/g1/configs/c.1".format(root)):
        funcname = check_output('ls {}/g1/configs/c.1 | grep usb0 || echo pass'.format(root), shell=True, encoding='utf-8').split('\n')[0] # get the symlink name
        if "usb0" in funcname:
            Popen('sudo rm {}/g1/configs/c.1/{}'.format(root, funcname), shell=True, stdout=stdolog, stderr=stdolog)           # remove the sysmlink
            Popen('sudo rmdir {}/g1/configs/c.1/strings/0x409'.format(root), shell=True, stdout=stdolog, stderr=stdolog)       # remove the string dir in the configuations
            Popen('sudo rmdir {}/g1/configs/c.1'.format(root), shell=True, stdout=stdolog, stderr=stdolog)                     # remove the configurations
            Popen('sudo rmdir {}/g1/functions/{}'.format(root, funcname), shell=True, stdout=stdolog, stderr=stdolog)          # remove the functions
            Popen('sudo rmdir {}/g1/strings/0x409'.format(root), shell=True, stdout=stdolog, stderr=stdolog)                   # remove the string dir in gadget
            Popen('sudo rmdir {}/g1'.format(root), shell=True, stdout=stdolog, stderr=stdolog)                                 # remove the string dir in gadget
    
    # creating the gadget
    Popen("sudo mkdir -p {}/g1".format(root), shell=True, stdout=stdolog, stderr=stdolog)                                       # For gadget its corresponding directory to be created
    Popen("sudo bash -c 'echo {} > {}/g1/idVendor'".format(VID, root), shell=True, stdout=stdolog, stderr=stdolog)              # Hex vendor ID, assigned by USB Group      
    Popen("sudo bash -c 'echo {} > {}/g1/idProduct'".format(PID, root), shell=True, stdout=stdolog, stderr=stdolog)             # Hex Product ID, assigned by USB Group 
    Popen("sudo bash -c 'echo {} > {}/g1/bcdDevice'".format(bcdDevice, root), shell=True, stdout=stdolog, stderr=stdolog)             # Hex Product ID, assigned by USB Group 
    Popen("sudo bash -c 'echo {} > {}/g1/bcdUSB'".format(bcdUSB, root), shell=True, stdout=stdolog, stderr=stdolog)             
    Popen("sudo bash -c 'echo {} > {}/g1/bDeviceClass'".format(bDeviceClass, root), shell=True, stdout=stdolog, stderr=stdolog)   
    Popen("sudo bash -c 'echo {} > {}/g1/bDeviceSubClass'".format(bDeviceSubClass, root), shell=True, stdout=stdolog, stderr=stdolog)            
    Popen("sudo bash -c 'echo {} > {}/g1/bDeviceProtocol'".format(bDeviceProtocol, root), shell=True, stdout=stdolog, stderr=stdolog)            
    Popen("sudo mkdir -p {}/g1/strings/0x409".format(root), shell= True, stdout=stdolog, stderr=stdolog)                   # setup standard device attribute strings LANGID 0x409: US-Eng
    Popen("sudo bash -c 'echo {} > {}/g1/strings/0x409/serialnumber'".format(serialnumber, root), shell= True, stdout=stdolog, stderr=stdolog) 
    Popen("sudo bash -c 'echo {} > {}/g1/strings/0x409/manufacturer'".format(manufacturer, root), shell= True, stdout=stdolog, stderr=stdolog)                  
    Popen("sudo bash -c 'echo {} > {}/g1/strings/0x409/product'".format(product, root), shell= True, stdout=stdolog, stderr=stdolog)                   

    # creating the configurations
    Popen("sudo mkdir -p {}/g1/configs/c.1".format(root), shell=True, stdout=stdolog, stderr=stdolog)                   # make the skeleton for a config for this gadget
    Popen("sudo mkdir -p {}/g1/configs/c.1/strings/0x409".format(root), shell=True, stdout=stdolog, stderr=stdolog)                   # This group contains subdirectories for language-specific strings for this configuration
    Popen("sudo bash -c 'echo {} > {}/g1/configs/c.1/strings/0x409/configuration'".format(configuration, root), shell=True, stdout=stdolog, stderr=stdolog)                 
    Popen("sudo bash -c 'echo {} > {}/g1/configs/c.1/MaxPower'".format(MaxPower, root), shell=True, stdout=stdolog, stderr=stdolog)                  
    catbmA = check_output('cat {}/g1/configs/c.1/bmAttributes'.format(root), shell=True, encoding='utf-8').split('\n')[0]       # cat bmAttributes 0x80 default 
    if catbmA != bmAttributes:
        Popen("sudo bash -c 'echo {} > {}/g1/configs/c.1/bmAttributes'".format(bmAttributes, root), shell=True, stdout=stdolog, stderr=stdolog)                   

    # creating the functions
    Popen("sudo mkdir -p {}/g1/functions/{}".format(root, FUNC), shell=True, stdout=stdolog, stderr=stdolog)
    # ecm it emulates an Eth device but uses USB instead of Eth as the medium. 
    if "ecm" in FUNC:
        Popen("sudo bash -c 'echo {} > {}/g1/functions/{}/host_addr'".format(ATT['HOST'], root, FUNC), shell=True, stdout=stdolog, stderr=stdolog)          # assign HOST MAC address
        Popen("sudo bash -c 'echo {} > {}/g1/functions/{}/dev_addr'".format(ATT['SELF'], root, FUNC), shell=True, stdout=stdolog, stderr=stdolog)           # assign device MAC address
    
    if "hid" in FUNC:
        Popen("sudo bash -c 'echo {} > {}/g1/functions/{}/protocol'".format(ATT['protocol'], root, FUNC), shell=True, stdout=stdolog, stderr=stdolog)       # assign protocol for keyboard
        Popen("sudo bash -c 'echo {} > {}/g1/functions/{}/subclass'".format(ATT['subclass'], root, FUNC), shell=True, stdout=stdolog, stderr=stdolog)       # assign subclass for keyboard
        Popen("sudo bash -c 'echo {} > {}/g1/functions/{}/subclass'".format(ATT['report_length'], root, FUNC), shell=True, stdout=stdolog, stderr=stdolog)       # assign report_length for keyboard
        try:
            DESCRIPTOR = os.path.join(os.getcwd(), ATT['report_desc'])
            Popen("sudo bash -c 'echo {} > {}/g1/functions/{}/report_desc'".format(DESCRIPTOR, root, FUNC), shell=True, stdout=stdolog, stderr=stdolog)       # assign report_desc for keyboard
        except:
            Popen("sudo bash -c 'echo '05010906a101050719e029e71500250175019508810275089501810175019503050819012903910275019505910175089506150026ff00050719002aff008100c0' | xxd -r -ps > {}/g1/functions/{}/report_desc'".format(root, FUNC), shell=True, stdout=stdolog, stderr=stdolog)       # assign report_desc for keyboard



    # try:

    #     pass
    # except:
        # pass



    # Popen('cd /sys/kernel/config/usb_gadget/ && sudo mkdir -p g1 && cd g1', shell=True, stdout=stdolog, stderr=stdolog)
    # Popen("sudo bash -c 'echo {} > {}/idVendor'".format(VID, root), shell=True, stdout=stdolog, stderr=stdolog)    
    # Popen("sudo bash -c 'echo {} > {}/idProduct'".format(PID, root), shell=True, stdout=stdolog, stderr=stdolog)    
    # Popen("sudo bash -c 'echo '0xEF' > {}/bDeviceClass'".format(root), shell=True, stdout=stdolog, stderr=stdolog)    
    # Popen("sudo bash -c 'echo '0x02' > {}/bDeviceSubClass'".format(root), shell=True, stdout=stdolog, stderr=stdolog)
    # Popen("sudo bash -c 'echo '0x01' > {}/bDeviceProtocol'".format(root), shell=True, stdout=stdolog, stderr=stdolog)
    # Popen("sudo mkdir -p {}/strings/0x409".format(root), shell=True, stdout=stdolog, stderr=stdolog)
    # Popen("sudo bash -c 'echo fedcba9876543210 > {}/strings/0x409/serialnumber'".format(root), shell=True, stdout=stdolog, stderr=stdolog)
    # Popen("sudo bash -c 'echo SWTE Media > {}/strings/0x409/manufacturer'".format(root), shell=True, stdout=stdolog, stderr=stdolog)
    # Popen("sudo bash -c 'echo SWTE USB Device > {}/strings/0x409/product'".format(root), shell=True, stdout=stdolog, stderr=stdolog)



  

    
    
if __name__ == "__main__":
    # reqcheck()
    menu(file='device.json')
    stdolog.close()
    
