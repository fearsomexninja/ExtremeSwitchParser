# Extreme Switch Parser

This repository contains python scripts for Extreme Networks switches running XOS, tested on version 16.1.2b14.

## Usage

After copying the script onto an Extreme Networks switch using a USB memory stick or a TFTP server, run the script using
`load script <file_name>.py`

## AP_doc_gen.py

When run, this script parses the FDB for a switch, generates a file listing all devices attached to the switch (recording port numbers for each device and VLANS for Aruba wireless access points), and sends the file to a TFTP server.

## Lock_learning_script.py

This script is an extension of AP_doc_gen.py; it parses the FDB to generate a list of all devices attached to the switch and locks MAC learning on all ports with Aruba wireless access points connected, so that port can only be used with that access point. The script generates a logfile listing all devices connected to the switch, as well as which ports were locked, and sends the logfile to a TFTP server.

## Unlock_learning_script.py 

Similar to the previous script, this script unlocks MAC learning on all ports with an Aruba wireless access point attached, so that the port can be used with another device, generating a logfile to be sent to a TFTP server.