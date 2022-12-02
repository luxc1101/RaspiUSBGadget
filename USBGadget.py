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