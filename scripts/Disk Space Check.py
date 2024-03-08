#!/usr/bin/env python

import sys, getopt
import shutil
import os
import string
import wmi

#test
DRIVE_TYPES = {
    0: "Unknown",
    1: "No Root Directory",
    2: "Removable Disk",
    3: "Local Disk",
    4: "Network Drive",
    5: "Compact Disc",
    6: "RAM Disk"
}

def check_disk_space(fail_percent, fail_gigabytes, warn_percent, warn_gigabytes):
    c = wmi.WMI()
    exit_code = 0
    print(f"Fail conditions: drive size <= {fail_gigabytes}GB or free space less than {fail_percent}%")
    print(f"Warn conditions: drive size <= {warn_gigabytes}GB or free space less than {warn_percent}%")

    for drive in c.Win32_LogicalDisk():
        drive_name = drive.VolumeName if drive.VolumeName != '' else 'Unlabeled'
        print('\n[%s] - "%s" (%s)' % (drive.Caption, drive_name, DRIVE_TYPES[drive.DriveType]))
        if drive.DriveType != 3:
            continue
        free = drive.FreeSpace
        size = drive.Size
        gbTotal = float(size) / float(1 << 30)
        gbFree = float(free) / float(1 << 30)
        gbPctFree = float(free) / float(size)
        print(f"Total: {gbTotal:.1f}GB, Free: {gbFree:.1f}GB ({gbPctFree:.0%})")
        if gbTotal <= fail_gigabytes or gbPctFree <= fail_percent:
            print(f"Fail: {drive.Caption} has less than {fail_gigabytes}GB total space or less than {fail_percent}% free space")
            exit_code = 2 
        elif gbTotal <= warn_gigabytes or gbPctFree <= warn_percent:
            print(f"Warning: {drive.Caption} has less than {warn_gigabytes}GB total space or less than {warn_percent}% free space")
            exit_code = max(exit_code, 1)
        sys.exit(exit_code)

def main(argv):
    fail_gigabytes = 20.0
    fail_percent = 15.0
    warn_gigabytes = 30.0
    warn_percent = 25.0

    try:
        opts, args = getopt.getopt(argv,"h",["fail_gigabytes=","fail_percent=", "warn_gigabytes=","warn_percent="])
    except getopt.GetoptError:
        print ('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt == "--fail_gigabytes":
            fail_gigabytes = float(arg)
        elif opt == "--fail_percent":
            fail_percent = float(arg)
        elif opt == "--warn_gigabytes":
            warn_gigabytes = float(arg)
        elif opt == "--warn_percent":
            warn_percent = float(arg)
    check_disk_space(fail_percent/100.0, fail_gigabytes, warn_percent/100.0, warn_gigabytes)

if __name__ == "__main__":
   main(sys.argv[1:])