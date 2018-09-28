"""
EXOS script for Extreme Networks switches
Written by Nicholas Bishop

Returns a csv file containing the downtime for each port not currently live.
"""
import exsh
import sys
import re
import csv
from datetime import datetime

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

SHOW_WORKING_PORTS = 0
if len(sys.argv) >= 2 and sys.argv[1] == "1":
    SHOW_WORKING_PORTS = 1

# all relevant info between these tags
PORT_INF_DET = "<show_ports_info_detail>"
PORT_INF_DET_CLOSE = "</show_ports_info_detail>"

# change for different tftp servers
TFTP_IP = "172.16.1.32"
VIR_ROUTER = "VR-Default"

DATE = datetime.now()

FILENAME = "/usr/local/cfg/{0}-{1}-{2}_unused_ports.csv".format(DATE.year, \
                                                                DATE.month,\
                                                                DATE.day)

def get_switch_start_dates():
    """
    Returns an array of strings containing the initial start date of each
    switch in the stack
    """
    raw_out = exsh.clicmd("sho odometers", capture=True, xml=False)
    #odo_info = re.findall('[a-zA-z]{3}-\d+-\d+', raw_out)
    odo_info = re.findall('Switch.*', raw_out)
    odo_info = [re.findall('[a-zA-z]{3}-\d+-\d+', line)[0] \
                for line in odo_info]
    return odo_info

def get_unused_ports():
    """
    Retrieves list of all inactive ports, with downtime for each port
    """
    csv_file = open(FILENAME, 'wb')
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', \
                            quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['Port', 'Display String', 'Downtime'])

    portinfo_xml = exsh.clicmd("sho port inf det", xml=True)
    if portinfo_xml != None:
        port_num = 0
        while True:
            # assume stack
            slot_num_fmt = port_num // 55 + 1
            port_num_fmt = port_num % 54 +1

            # get xml for port
            start = str.find(portinfo_xml, PORT_INF_DET)
            end = str.find(portinfo_xml, PORT_INF_DET_CLOSE)
            if start == -1 or end == -1: # no more ports
                break

            end += len(PORT_INF_DET_CLOSE)
            port_info = portinfo_xml[start:end]

            # extract port info
            xmlextract = port_info[:end]
            tree = ET.fromstring(xmlextract)

            link_state = 0
            time_last_down = 0
            display_string = ""

            # find relevant port info
            for elem in tree.iter():
                if 'linkState' == elem.tag:
                    link_state = int(elem.text)
                if 'timeLastDown' == elem.tag:
                    time_last_down = int(elem.text) #convt to microseconds
                if 'displayString' == elem.tag:
                    display_string = elem.text

            # if down, report downtime
            if link_state == 1:
                if SHOW_WORKING_PORTS:
                    col1 = "{0}:{1}".format(slot_num_fmt, port_num_fmt)
                    csv_writer.writerow([col1, display_string, "PORT IS UP"])
            elif time_last_down == 0:
                col1 = "{0}:{1}".format(slot_num_fmt, port_num_fmt)
                csv_writer.writerow([col1, display_string, "NEVER USED"])
            else:
                time_last_down = datetime.fromtimestamp(time_last_down)
                time_diff = DATE - time_last_down
                time_diff_str = (str(time_diff.days) + " days " + 
                                 str(time_diff.seconds / 3600) + " hours " + 
                                 str(time_diff.seconds % 3600 / 60) + " minutes"
                col1 = "{0}:{1}".format(slot_num_fmt, port_num_fmt))
                csv_writer.writerow([col1, display_string, time_diff_str])

            # strip off the first XML transaction from group and continue
            portinfo_xml = portinfo_xml[end:]
            port_num += 1

    csv_file.close()
    exsh.clicmd("save")

    # if file can't be sent, leave on switch
    try:
        cmd = exsh.clicmd("tftp put {0} vr {1} ".format(
                           TFTP_IP, VIR_ROUTER) + FILENAME, False)
        exsh.clicmd("rm " + FILENAME, False)
    except RuntimeError:
        print("Failed to send file to TFTP server.")

get_unused_ports()
