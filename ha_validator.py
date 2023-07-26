#!/usr/local/bin/python3

"""

@author    : Arslan Ahmad

VERSION_NUMBER = 3.7

"""

from __future__ import print_function
from array import *
import re
import sys
import os
import tarfile
import calendar
import fnmatch
import difflib
import shutil
import subprocess
import csv
import xml.dom.minidom
import glob
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import argparse
from prettytable import PrettyTable

path = []
vers = []
uname = []
v = []    # This array has kernel versions
u = []    # This array has list of all nodes (where nodelist is corresponding to kernel version)
hostDiff = []
hostSame = []
location = []
kern = []
node = 0
actualnode = 0
fence = []
stonithenabled = 1
fencedevices = []
myCmd1 = 'ls -lrt'
basedir = '/cases/'
rgmanager = 0
supported = 0
case = 0
clusternames = []
clusternodes = []
notclusternodes = []
newpath = []
close = 0
nocib = 0
final_sosreport = {}
comp_late = []  
different_cluster = 0
case = 0
yank = 0
halvm = 0
clulvm = 0
use_lvmetad = 0
locking_type = 0
hafs = 0
pkg_mismatch = []
pkg_duplicate = []
platform_fence_compatible = 1
iofence = 0

def __get_args() :
    description =  "This script will help to get the basic validation check of Pacemaker Cluster over RHEL6/7/8. "
    description += "It gives limited information for RHEL 6 rgmanager cluster. "
    description += "Please ensure that you have authorized your kerberos ID for performing 'yank'. "
    description += "If not, please kill the script and do 'yank -i'. Once done, re-run the script. "
    command_name = "ha_validator"
    epilog =  "Usage examples:\n"
    epilog += "Analyze a selected sosreports from case directory over supportshell.\n"
    epilog += "$ %s -c 02511046 \n\n" %(command_name)

    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--case",
                    help="The case number to be processed.",
                    default='False')
    args=parser.parse_args()


def samecluster():
    global path
    global vers
    global uname
    global v
    global u
    global hostDiff
    global hostSame
    global location
    global node
    global typeos
    global kern
    global fence
    global stonithenabled
    global myCmd1
    global basedir
    global rgmanager
    global case
    global close
    global final_sosreport
    global comp_late
    global different_cluster
    global case
    global yank
    global pkg_mismatch
    global pkg_duplicate
    global rhrelease

    ##### Get the path for sosreport of each cluster node #####
    
    z = 0
    loop = 0
    intpath = []
    nodata = 0
    rh6 = 0
    rh7 = 0
    rh8 = 0
    if (close == 0) & (different_cluster == 0):
        print("\n\t\033[1;32m {}\033[00m".format("READ:") + " Please make sure you have authorized your kerberos ID for performing 'yank'. If not, please kill the script and do 'yank -i'. Once done re-run the script.\n")

    inputcase = 0
    try:
        firstarg = sys.argv[2]
        case = str(firstarg)
        inputcase = 1
    except IndexError:
        print("") 
    
    while (close == 0):
        try:
            if (inputcase == 0) & (different_cluster == 0):
                case = input("Enter the case number: ")
            case = int(case)
            if different_cluster == 1:
                case = str('0' + str(case))
        except ValueError:
            print("Sorry, please enter a " + "\033[1;31m {}\033[00m".format("numeric value") + ".")
            inputcase = 0
            continue
        if (int(case) > 0) & (different_cluster == 0):
            case = str(case)
            case = str('0' + case)
        if not case:
            inputcase = 0
            continue
        elif int(case) == 0:
            print("Sorry, case number can't be zero.")
            inputcase = 0
            continue
        elif int(case) == 111:
            print("Closing.")
            exit()
        elif int(case) < 0 and int(case) != 0:
            print("Sorry, case number can't be negative.")
            inputcase = 0
            continue
        elif (int(case) > 0) & (int(case) != 111):
            if different_cluster == 0:
                print("\nExtracting data from " + str(case) + ":")
                yank = os.system("yank " + case + " -y > /dev/null")
            # yank = 0
            if yank == 0:
                loc = os.path.exists(basedir + str(case))
                if loc:
                    if different_cluster == 0:
                        print("\n\t\033[1;32m {}\033[00m".format("READ:") + " Once you are done with the sosreport selection, enter keyword" + "\033[1;33m {}\033[00m".format("end") + " so the processing of the sosreports can be initiated.\n")
                    os.chdir(basedir + str(case))
                    os.system(myCmd1)
                    while (loop == 0):
                        initial = input("Please select Node" + str(z+1) + "'s sosreport: ")
                        if not initial: 
                            print("Blank/Empty space can't be accepted.") 
                            continue
                        locate = str(basedir) + str(case) + "/" + str(initial)
                        loc = os.path.exists(locate)
                        if loc:
                            sosloop = 0
                            sos = 0
                            tmp = ''
                            for sosloop in range(0, len(intpath)):
                                tmp = str(intpath[int(sosloop)])
                                if str(tmp) == (locate + str("/*/")):
                                    sos = 1
                                    print("Sosreport already selected previously.")
                                    break
                            if sos == 1:
                                continue
                            comp_late.append(initial)
                            intpath.append(locate + str("/*/"))
                            node = node + 1
                            z = z + 1
                        elif (str(initial) == "end") & (loc == False):
                            if z == 0:
                                process = input("You have not given any sosreport to process. Do you wish to end this validation ? [Reply with" + "\033[1;32m {}\033[00m".format("yes") + " /" + "\033[1;31m {}\033[00m".format("no") + "] : ")
                                if str(process) == "yes":
                                    print("As you wish.. Bye!")
                                    return ("powerkill")
                                    break
                                elif str(process) == "no":
                                    continue
                                else:
                                    print("Seems like you are confused... Starting over again..!!")
                                    continue
                            else:
                                print("\n\t Processing the sosreport(s)...")
                                loop = 1
                                close = 1
                                break
                        elif (str(initial) != "end") & (loc == False):
                            print("This sosreport does not exist. Wake up and give another try for correct sosreport.\n")
                            continue
                else:
                    nodata = nodata + 1
                    if nodata == 2:
                        print("Do me a favor, check if customer has shared any attachment on the case " + str(case) + " and then re-initiate the script.\n")
                        exit()
                    else:
                        print("You must be thinking about what was the root cause, that you forgot to check if there are any attachments!!\n")
                        inputcase = 0
                    continue
            elif yank != 0:
                print("\033[1;33m {}\033[00m".format("Either the case number is incorrect or sosreport tar-ball is corrupt."))
                exit()

    if close == 1:
        z = 0
        for z in range(z, int(node)):
            i = glob.glob(intpath[int(z)])
            path.append(str(i[int(0)]))
            z = z + 1

    #******************************* Ends *******************************#

    ##### Check the kernel version #####

    z = 0
    repeat = "yes"
    for z in range(z, int(node)):
        if (close == 2) & (repeat == "yes"):
            v = []
            u = []
        loc = os.path.exists(str(path[int(z)]) + "sos_commands/kernel/uname_-a")
        if loc:
            h = open(str(path[int(z)]) + "sos_commands/kernel/uname_-a")
            uname = h.read()
            vers = uname.split()
            v.append(str(vers[2]))  # This array has kernel versions
            u.append(str(vers[1].split(".")[0]))  # This array has list of all nodes (where nodelist & is corresponding to kernel version)
            h.close()
            z = z + 1
            repeat = "no"
        else:
            print("Cannot find file for determining the kernel version and hostname in sosreport.")
            exit()

    ##### Deciding the OS version #####

    z = 0
    rhrelease = []
    for z in range(z, int(node)):
        search_term1 = '2.6.32'
        search_term2 = '3.10.0'
        search_term3 = '4.18.0'
        loc = os.path.exists(str(path[int(z)]) + "/etc/redhat-release")
        if loc:
            with open(str(path[int(z)]) + "/etc/redhat-release", "r") as ifile:
                temp = ifile.readlines()
                for line in temp:
                    if line.find('Red Hat Enterprise Linux Server release 5') != -1:
                        rhrelease.append(str(line.strip()))
                        redhatrelease = 'rhel5'
                    elif line.find('Red Hat Enterprise Linux Server release 6') != -1:
                        rhrelease.append(str(line.strip()))
                        redhatrelease = 'rhel6'
                    elif line.find('Red Hat Enterprise Linux Server release 7') != -1:
                        rhrelease.append(str(line.strip()))
                        redhatrelease = 'rhel7'
                    elif line.find('Red Hat Enterprise Linux release 8') != -1:
                        rhrelease.append(str(line.strip()))
                        redhatrelease = 'rhel8'
                    elif line.find('CentOS') != -1:
                        print("\nThis server is running with " + line.strip() + " operating system. Hence exiting.\n")
                        return ("powerkill")
        else:
            print("\nEither the file '/etc/redhat-release' is not captured or it is not a RHEL OS. Hence exiting.\n")
            return ("powerkill")

        if re.search(search_term1, v[int(z)]) or (redhatrelease == 'rhel6'):
            typeos = str("rhel6")
            rh6 = rh6 + 1
        elif re.search(search_term2, v[int(z)]) or (redhatrelease == 'rhel7'):
            typeos = str("rhel7")
            rh7 = rh7 + 1
        elif re.search(search_term3, v[int(z)]) or (redhatrelease == 'rhel8'):
            typeos = str("rhel8")
            rh8 = rh8 + 1
        else:
            typeos = str("rhel5")

    if typeos == str("rhel6"):
        print("\n\033[1;33m {}\033[00m".format("WARNING:") + " RHEL 6 is now ELS and ELS has only limited technical support. Still proceeding with the checks. Refer KCS: https://access.redhat.com/articles/4665701 .\n")
    elif typeos == str("rhel5"):
        print("\nThe cluster node is seems to be RHEL 5, which is no longer supported. Refer KCS: https://access.redhat.com/articles/2901061 .\n")
        exit()

    if (rh6 > rh7) & (rh6 > rh8):
        typeos = str("rhel6")
    elif (rh7 > rh6) & (rh7 > rh8):
        typeos = str("rhel7")
    elif (rh8 > rh6) & (rh8 > rh7):
        typeos = str("rhel8")
    elif rh6 == rh7:
        print("\n\033[1;33m {}\033[00m".format("WARNING:") + " Manual intervention required to check which of the sosreport belong to a cluster setup as nodes are running with different RHEL major version.\n")
        exit()
    elif rh7 == rh8:
        print("\n\033[1;33m {}\033[00m".format("WARNING:") + " Manual intervention required to check which of the sosreport belong to a cluster setup as nodes are running with different RHEL major version.\n")
        exit()
    elif rh6 == rh8:
        print("\n\033[1;33m {}\033[00m".format("WARNING:") + " Manual intervention required to check which of the sosreport belong to a cluster setup as nodes are running with different RHEL major version.\n")
        exit()           

    #******************************* Ends *******************************#

    #### Validating if all sosreport from same cluster environment ####

    global clusternames
    global clusternodes
    global notclusternodes
    global newpath
    NoCluster = False
    Allsos = False
    if typeos == str("rhel7") or typeos == str("rhel8"):
        z = 0
        newnode = 0
        for z in range(z, int(node)):
            loc = os.path.exists(str(path[int(z)]) + "/etc/corosync/corosync.conf")
            if loc:
                with open(str(path[int(z)]) + "/etc/corosync/corosync.conf", "r") as ifile:
                    newpath.append(str(path[int(z)]))
                    newnode = newnode + 1
                    temp = ifile.readlines()
                    for line in temp:
                        if re.search("cluster_name:", line):
                            line = line.strip()
                            line = line.split(": ")[1]
                            clusternames.append(str(line))
                            clusternodes.append(str(u[int(z)]))
                            Allsos = True
                            break
            else:
                NoCluster = True
                notclusternodes.append(str(u[int(z)]))
        clusterlist = len(set(clusternames))

        z = 0
        for z in range(z, int(newnode)):
            final_sosreport[str(comp_late[int(z)])] = str(clusternames[int(z)])
            z = z + 1

        if (clusterlist == 1) & (NoCluster == False) & (Allsos == True):
            return ("Same")
        elif (clusterlist == 1) & (NoCluster == True) & (Allsos == True):
            print("\n - Among all the sosreports, it seems system(s) " + str(notclusternodes) + " is not a cluster node. While others " + str(clusternodes) + " are cluster nodes.")
            path = newpath
            node = newnode
            close = 2
            return ("NotAll")
        else:
            return (NoCluster)
    elif typeos == str("rhel6"):
        z = 0
        newnode = 0
        for z in range(z, int(node)):
            loc = os.path.exists(str(path[int(z)]) + "/etc/cluster/cluster.conf")
            if loc:
                with open(str(path[int(z)]) + "/etc/cluster/cluster.conf", "r") as ifile:
                    newpath.append(str(path[int(z)]))
                    newnode = newnode + 1
                    temp = ifile.readlines()
                    for line in temp:
                        if re.search("config_version=", line):
                            line = line.strip()
                            line = line.split("name=")[1]
                            clusternames.append(str(line))
                            clusternodes.append(str(u[int(z)]))
                            Allsos = True
                            break
            else:
                NoCluster = True
                notclusternodes.append(str(u[int(z)]))
        clusterlist = len(set(clusternames))

        z = 0
        for z in range(z, int(newnode)):
            final_sosreport[str(comp_late[int(z)])] = str(clusternames[int(z)])
            z = z + 1
        
        if (clusterlist == 1) & (NoCluster == False) & (Allsos == True):
            return ("Same")
        elif (clusterlist == 1) & (NoCluster == True) & (Allsos == True):
            print("\n - Amoung all the sosreports, it seems system(s) " + str(notclusternodes) + " is not a cluster node. While others " + str(clusternodes) + " are cluster nodes.")
            path = newpath
            node = newnode
            close = 2
            return ("NotAll")
        else:
            return (NoCluster)

    #******************************* Ends *******************************#      

    #### Validating the number of cluster nodes v/s number of sosreports shared ####

def actnode():
    global actualnode
    global path
    global node
    if typeos == str("rhel7") or typeos == str("rhel8"):
        loc = os.path.exists(str(path[0]) + "/etc/corosync/corosync.conf")
        if loc:
            with open(str(path[0]) + "/etc/corosync/corosync.conf", "r") as ifile:
                temp = ifile.readlines()
                for line in temp:
                    if re.search("nodeid", line):
                        actualnode = actualnode + 1
    elif typeos == str("rhel6"):
        loc = os.path.exists(str(path[int(0)]) + "/etc/cluster/cluster.conf")
        if loc:
            with open(str(path[int(0)]) + "/etc/cluster/cluster.conf", "r") as ifile:
                temp = ifile.readlines()
                for line in temp:
                    if re.search("nodeid", line):
                        actualnode = actualnode + 1

    diffnode = actualnode - node
    if (diffnode == 0):
        print("\tWe have sosreport from all the " + str(actualnode) + " cluster nodes. Proceeding ahead...\n")
        if (actualnode == 1):
            print("\t\033[1;33m {}\033[00m".format("WARNING:") + " Since this is a single node cluster setup, please ensure the OS is RHEL 8.2 and later. Refer: https://access.redhat.com/articles/3069031 .")
    elif (diffnode > 0):
        print("\t\033[1;33m {}\033[00m".format("WARNING:") + " Out of " + str(actualnode) + " cluster nodes, you have only shared " + str(node) + " node's sosreport. Still proceeding ahead with the " + str(node) + " sosreports.")
    elif (diffnode < 0):
        print("\t\033[1;33m {}\033[00m".format("WARNING:") + " The environment consist of " + str(actualnode) + " cluster nodes. It seems one sosreport is selected multiple times. Still proceeding ahead with the selected sosreports.")

    #******************************* Ends *******************************#      

def main():
    global fence
    global stonithenabled
    global fencedevices
    global rgmanager
    global typeos
    global path
    global node
    global nocib
    global halvm
    global clulvm
    global locking_type
    global use_lvmetad
    global hafs
    global pkg_mismatch
    global pkg_duplicate
    global rhrelease
    global maintmode
    global azure
    global aws
    global gcp
    global cib_exists

    actnode()

        ##### Firewalld status of the cluster node #####
    
    firewalld = []
    z = 0
    for z in range(z, int(node)):
        flag = 0
        if (typeos == str("rhel7")) or (typeos == str("rhel8")):
            if (os.path.exists(str(path[int(z)]) + "sos_commands/firewalld/firewall-cmd_--list-all-zones")):
                firewall_file = open(str(path[int(z)]) + "sos_commands/firewalld/firewall-cmd_--list-all-zones", "rt")
                contents = firewall_file.readlines()
                for line in contents:
                    if line.find("FirewallD is not running") != -1:
                        flag = 1
                if flag == 1:
                    firewalld.append("FirewallD is not running.")
                else:
                    firewalld.append("FirewallD is running.")
            else:
                firewalld.append("File not found.")
        elif (typeos == str("rhel6")):
            if (os.path.exists(str(path[int(z)]) + "sos_commands/startup/chkconfig_--list")):
                firewall_file = open(str(path[int(z)]) + "sos_commands/startup/chkconfig_--list", "rt")
                contents = firewall_file.readlines()
                for line in contents:
                    if re.search("iptables", line):
                        if re.search("on", line):
                            flag = 1
                if flag == 1:
                    firewalld.append("Firewall/iptables is running")
                else:
                    firewalld.append("Firewall/iptables is not running")
            else:
                firewalld.append("File not found.")

            ##### Service Status #####
    
    ## Find the service & return a specific line
    def service_check(service, x, z):
        loc = os.path.exists(str(path[int(z)]) + "/sos_commands/systemd/systemctl_status_--all")
        if loc:
            with open(str(path[int(z)]) + "/sos_commands/systemd/systemctl_status_--all", "r") as ifile:
                lines = ifile.readlines()
                for index, line in enumerate(lines):
                    if line.startswith('* ' + service):
                        status = lines[index+x].strip()
                        if (x == 2) and (status.find("Active") == -1):
                            status = lines[index+x+2].strip()
                        return(status)

    ## Check if the service is enabled at boot
    def service_at_boot(srv_name):
        srv_boot_status = []
        i = 0
        for i in range(0, len(srv_name)):
            z = 0
            for z in range(z, int(node)):
                service_at_boot_check = service_check(srv_name[i],1,z)
                srv_boot_status.append(1 if re.search("; enabled;", str(service_at_boot_check)) else 0)
        return(srv_boot_status)

    ## Check if the service is active/running
    def service_is_active(srv_name):
        i = 0
        srv_active_status = []
        for i in range(0, len(srv_name)):
            z = 0
            for z in range(z, int(node)):
                service_is_active_chck = service_check(srv_name[i],2,z)
                srv_active_status.append(1 if re.match("Active: active", str(service_is_active_chck)) else 0)
        return(srv_active_status)

    #******************************* Ends *******************************#

    ##### Finding the HW Type #####

    def hwtype(count):
        global path
        if os.path.exists(str(path[int(z)]) + "/sos_commands/hardware/dmidecode"):
            if os.stat(str(path[int(count)]) + "/sos_commands/hardware/dmidecode").st_size != 0:
                with open(str(path[int(count)]) + "/sos_commands/hardware/dmidecode", "r") as ifile:
                    for line in ifile:
                        if line.startswith("System Information"):
                            hw = (next(ifile, '').strip())
                            if re.search("Red Hat", hw):
                                hws = (next(ifile, '').strip())
                                if re.search("KVM", hws):
                                    return("Manufacturer: KVM")
                                elif re.search("RHEV Hypervisor", hws):
                                    return("Manufacturer: RHEV")
                                elif re.search("OpenStack", hws):
                                    return("Manufacturer: OpenStack")
                                elif re.search("RHEL", hws):
                                    return("Manufacturer: RHEV")
                            elif re.search("RDO", hw):
                                hws = (next(ifile, '').strip())
                                if re.search("OpenStack", hws):
                                    return("Manufacturer: OpenStack")
                            elif re.search("Microsoft", hw):
                                hwss = (next(ifile, '').strip())
                                if re.search("Virtual Machine", hwss):
                                    return(hw)
                            else:
                                return(hw)
                    ifile.close()
            else:
                return("empty_file")
        else:
            return("no_file")

    #******************************* Ends *******************************#

        ##### Boot Time for the cluster node #####

    abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}        # function to convert number to month like 1-Jan-2019
    print("\n\t***** System Information ***** \n")

    z = 0
    for z in range(z, int(node)):
        if (typeos == str("rhel7") or typeos == str("rhel8")) & (os.path.exists(str(path[int(z)]) + "sos_commands/date/date")):
            myfile2 = open(str(path[int(z)]) + "sos_commands/date/date", "rt")
        elif (typeos == str("rhel7") or typeos == str("rhel8")) & (os.path.exists(str(path[int(z)]) + "sos_commands/general/date")):
            myfile2 = open(str(path[int(z)]) + "sos_commands/general/date", "rt")
        elif (typeos == str("rhel6")) & (os.path.exists(str(path[int(z)]) + "sos_commands/date/date")):
            myfile2 = open(str(path[int(z)]) + "sos_commands/date/date", "rt")
        elif (typeos == str("rhel6")) & (os.path.exists(str(path[int(z)]) + "sos_commands/general/date")):
            myfile2 = open(str(path[int(z)]) + "sos_commands/general/date", "rt")
        contents2 = myfile2.read()
        sosdate = contents2.split()
        myfile2.close()
        sdate = int(sosdate[2])
        smonth = str(sosdate[1])
        syear = int(sosdate[5])
        stime = str(sosdate[3])
        sostime = stime.split(':')
        shours = int(sostime[0])
        smin = int(sostime[1])
        ssec  = int(sostime[2])
        smonth = (abbr_to_num[smonth])

        sgdate = datetime(syear,smonth,sdate,shours,smin,ssec)
        if (typeos == str("rhel7") or typeos == str("rhel8")) & (os.path.exists(str(path[int(z)]) + "sos_commands/host/uptime")):
            myfile3 = open(str(path[int(z)]) + "sos_commands/host/uptime", "rt")
        elif (typeos == str("rhel7") or typeos == str("rhel8")) & (os.path.exists(str(path[int(z)]) + "sos_commands/general/uptime")):
            myfile3 = open(str(path[int(z)]) + "sos_commands/general/uptime", "rt")
        elif (typeos == str("rhel6")) & (os.path.exists(str(path[int(z)]) + "sos_commands/host/uptime")):
            myfile3 = open(str(path[int(z)]) + "sos_commands/host/uptime", "rt")
        elif (typeos == str("rhel6")) & (os.path.exists(str(path[int(z)]) + "sos_commands/general/uptime")):
            myfile3 = open(str(path[int(z)]) + "sos_commands/general/uptime", "rt")

        contents3 = myfile3.read()        
        uptimed = contents3.split()  
        myfile3.close()

        length = len(uptimed)

        if length == 12:
                udays = int(uptimed[2])
                uhour = str(uptimed[4])
                uphour = re.split('[: ,]',uhour)
                uphhor = int(uphour[0])
                uphmin = int(uphour[1])
                ld01 = uptimed[9].split(",")[0]
                ld05 = uptimed[10].split(",")[0]
                ld15 = uptimed[11]
        elif length == 11:
                udays = 0
                uhour = 0
                uphhor = 0
                uphmin = int(uptimed[2])
                ld01 = uptimed[8].split(",")[0]
                ld05 = uptimed[9].split(",")[0]
                ld15 = uptimed[10]
        elif length == 13 :
                udays = 0
                uhour = 0
                uphhor = 0
                uphmin = int(uptimed[4])
                ld01 = uptimed[10].split(",")[0]
                ld05 = uptimed[11].split(",")[0]
                ld15 = uptimed[12]
        else :
                udays = 0
                uhour = str(uptimed[2])
                uphour = re.split('[: ,]', uhour)
                uphhor = int(uphour[0])
                uphmin = int(uphour[1])
                ld01 = uptimed[7].split(",")[0]
                ld05 = uptimed[8].split(",")[0]
                ld15 = uptimed[9]

        bootdate =  sgdate - timedelta( days=udays, hours=uphhor , minutes=uphmin)

        hdware = hwtype(int(z))
        if re.match("empty_file", hdware):
            hware = "dmidecode file is empty."
        elif re.match("no_file", hdware):
            hware = "dmidecode file is not captured in sosreport."
        else:
            hware = str(hdware).split(": ")[1]

        print("\n - For cluster node " + str(u[int(z)]) + " :\n")
        print("Sos capture date/time : %s"%sgdate)
        print("Server Boot date/time : %s"%bootdate)
        print("Server Uptime         : %s day(s), %s hour(s), %s min(s)"%(udays,uphhor,uphmin))
        print("Load Average          : 01 min: %s | 05 min: %s | 15 min: %s"%(ld01,ld05,ld15))
        print("OS Release            : %s"%rhrelease[int(z)])
        print("FirewallD status      : %s"%firewalld[int(z)])
        print("Hardware Type         : %s"%str(hware))
    z = z + 1

    if len(set(firewalld)) != 1:
        print("\n\033[1;31m {}\033[00m".format("ALERT") + " : FirewallD status is not same on all the cluster nodes.")

    ## Check for cluster service status

    cluster_daemon = ['pcsd.service', 'corosync.service', 'pacemaker.service']
    cluster_service_name = ['PCSD', 'Corosync', 'Pacemaker']

    service_table = PrettyTable()
    srv_active_final = []
    temp_srv_active = service_is_active(cluster_daemon)
    for i in range(0, len(temp_srv_active)):
        if (temp_srv_active)[i] == 1:
            srv_active_final.append("Active")
        else:
            srv_active_final.append("Inactive")

    srv_boot_final = []
    temp_srv_boot = service_at_boot(cluster_daemon)
    for i in range(0, len(temp_srv_boot)):
        if (temp_srv_boot)[i] == 1:
            srv_boot_final.append("Enabled")
        else:
            srv_boot_final.append("Disabled")

    i = 0
    def split(list_a, chunk_size):
        for i in range(0, len(list_a), chunk_size):
            yield list_a[i:i + chunk_size]
    
    chunk_size = int(node)
    cluster_srv_active = list(split(srv_active_final, chunk_size))
    cluster_srv_enabled = list(split(srv_boot_final, chunk_size))
    pcsd_is_active = cluster_srv_active[0]
    corosync_is_active = cluster_srv_active[1]
    pacemaker_is_active = cluster_srv_active[2]
    pcsd_is_enabled = cluster_srv_enabled[0]
    corosync_is_enabled = cluster_srv_enabled[1]
    pacemaker_is_enabled = cluster_srv_enabled[2]

    z = 0
    if typeos != ("rhel6"):
        for z in range(z, int(node)):
            if z == 0:
                print("\n\t***** Checking the Cluster daemon status across nodes *****\n")
                service_table.field_names = ["Cluster Node", "Service", "pcsd", "corosync", "pacemaker"]
            service_table.add_row([str(u[int(z)]), 'Is Active?', str(pcsd_is_active[z]), str(corosync_is_active[z]), str(pacemaker_is_active[z])])
            service_table.add_row([str(""), 'At boot?', str(pcsd_is_enabled[z]), str(corosync_is_enabled[z]), str(pacemaker_is_enabled[z])])
            if z == 0:
                print(service_table)
            if z != 0:
                print("\n".join(service_table.get_string().splitlines()[-3:]))


        ##### Check the kernel version on all the cluster nodes or from the set of cluster nodes's sosreport shared #####

    j = 0

    print("\n\t***** Checking the Kernel Version across the nodes ***** \n")

    result = False
    result = len(set(v)) == 1  ## Check the unique entries in array containing all the kernel version from all nodes ##
        
    if result:
        kernel = "True"
    else:
        kernel = "False"      
        print("\033[1;31m {}\033[00m".format("ALERT") + " : Kernel version is not same on all the cluster nodes. Now checking the different version.\n")

    nTemp = v[0]   ## Fixing one value for reference to compare the other node's kernel version ##
    bEqual = True

    for item in v:
        if nTemp != item:
            bEqual = False
            kern.append(str(item))

            hostDiff.append(str(u[j]))
        j = j + 1
        if j == int(node):
            hostSame.append(list(set(u) - set(hostDiff)))
            break
    if bEqual:
        print(" - Kernel version is same on " + str(node) + " nodes. All nodes running on " + str(v[0]) + " version.")
    else:
        chknode = len(set(kern))
        if chknode == 1:
            print(" - The node(s) " + str(hostDiff) + " is running on " + str(kern[0]) + ". \nWhile the rest of the node(s) " + str(hostSame) +  " is running on " + str(v[0]) + " version.")
        else:
            print(" - The node(s) " + str(hostDiff) + " is running on " + str(kern) + " respectively. \nWhile the rest of the node(s) " + str(hostSame) +  " is running on " + str(v[0]) + " version.")
        print(" - Please note: It is recommended & supported to keep the same kernel version on all the cluster nodes. Refer support policies article: https://access.redhat.com/articles/3069091. Hence please bring all the cluster nodes to same kernel version.\n")

    #******************************* Ends *******************************#

    ##### Deciding which is the directory path for cluster status/configuration #####
    
    # Running this in loop because what if only one node in cluster does not have cluster services running.

    z = 0
    for z in range(z, int(node)):
        search_term1 = '2.6.32'
        search_term2 = '3.10.0'
        search_term3 = '4.18.0'
        flag = False
        if re.search(search_term1, v[int(z)]):
            typeos = str("rhel6")
            with open(str(path[int(z)]) + "/etc/cluster/cluster.conf") as f:
                if 'fence_pcmk' in f.read():
                    flag = True
                f.close()
            if flag == True:
                location.append(str(path[int(z)]) + "/sos_commands/cluster/")
            elif flag == False:
                rgmanager = 1
                break
        elif re.search(search_term2, v[int(z)]):
            typeos = str("rhel7")
            loc = os.path.exists(str(path[int(z)]) + "/sos_commands/pacemaker/")
            if loc:
                location.append(str(path[int(z)]) + "/sos_commands/pacemaker/")
            else:
                location.append(str(path[int(z)]) + "/sos_commands/cluster/")
        elif re.search(search_term3, v[int(z)]):
            typeos = str("rhel8")
            loc = os.path.exists(str(path[int(z)]) + "/sos_commands/pacemaker/")
            if loc:
                location.append(str(path[int(z)]) + "/sos_commands/pacemaker/")
            else:
                location.append(str(path[int(z)]) + "/sos_commands/cluster/")
        else:
            kernel_vendor = []
            nonrhel_kernel_vendor = []
            w = 0
            for w in range(w, int(node)):
                if os.path.exists(str(path[int(w)]) + "/sos_commands/rpm/package-data"):
                    h = open(str(path[int(w)]) + "/sos_commands/rpm/package-data", "r")
                    hp = h.read()
                    fl = hp.split("\n")
                    res = [n for n in fl if re.search("kernel-", n)]
                    resnewer = [ resnew.split(None, 9)[0] for resnew in res ]
                    for j in resnewer:
                        if re.search(v[int(w)], j):
                            kernel_vendor = [ resnew.split(None, 9)[7] for resnew in res ]

            for i in kernel_vendor:
                if i != 'Red':
                    nonrhel_kernel_vendor.append(str(i))
            
            if len(set(nonrhel_kernel_vendor)) == 1:
                print(" - All the cluster nodes are currently running with a non-RHEL Kernel and is shipped by " + str(nonrhel_kernel_vendor[0]) + ". Hence exiting from script.\n")
                return("powerkill")
            elif len(set(nonrhel_kernel_vendor)) > 1:
                x = 0
                for x in range(x, int(node)):
                    if x == 0:
                        print("\n - The cluster node " + str(u[int(x)]) + " is running with Kernel shipped by " + str(nonrhel_kernel_vendor[int(x)]) + ".")
                    else:
                        print(" - The cluster node " + str(u[int(x)]) + " is running with Kernel shipped by " + str(nonrhel_kernel_vendor[int(x)]) + ".")
                return("powerkill")

    if typeos == ("rhel7"):
        print(" - This is a RHEL7 pacemaker cluster.")
    elif typeos == ("rhel8"):
        print(" - This is a RHEL8 pacemaker cluster.")
    elif (typeos == ("rhel6")) & (flag == True):
        print(" - This is a RHEL6 pacemaker cluster.")
    elif (typeos == ("rhel6")) & (flag == False) & (rgmanager == 1):
        print(" - This is a RHEL6 rgmanager cluster.")

    #******************************* Ends *******************************#

    ##### Cluster Ring details #####

    z = 0
    ip = []
    ring_rhel6 = []
    ring_rhel7 = []
    ring_rhel8 = []
    ring = []
    ring2 = []
    final_ip = []
    final_ring = []
    new_ring = []
    cluster_name = []
    interface = []
    cluster_notrunning = 0
    for z in range(z, int(node)):
        if ((typeos == str("rhel7")) or (typeos == str("rhel8"))) & (os.path.exists(str(path[int(z)]) + "sos_commands/corosync/corosync-cmapctl")):
            with open(str(path[int(z)]) + "sos_commands/corosync/corosync-cmapctl", "r") as coro:
                for line in coro:
                    if (line.find("Failed to initialize the cmap API")) != -1:
                        cluster_notrunning = 1
                        break
                    if (line.find("ip(")) != -1:
                        ip.append(line)
                    if (line.find("ring")) != -1:
                        if (line.find("nodelist")) != -1:
                            ring_rhel7.append(line)
                    if (line.find("name")) != -1:
                        if (line.find("nodelist")) != -1:
                            ring_rhel8.append(line)
                    if (line.find("cluster_name")) != -1:
                        cluster_name.append((line.split('(str) =')[1]).strip())
                        print(" - Cluster Name: %s\n"%cluster_name[0])
                for i in ip:
                    test_ip = i.split('ip(')
                    for test in test_ip:
                        if test.find("runtime") == -1:
                            final_ip.append(test.split(')')[0])
                if typeos == str("rhel7"):
                    for i in ring_rhel7:
                        final_ring.append((i.split('(str) =')[1]).strip())
                elif typeos == str("rhel8"):
                    for i in ring_rhel8:
                        final_ring.append((i.split('(str) =')[1]).strip())
            break
        elif (typeos == str("rhel6")) & (os.path.exists(str(path[int(z)]) + "sos_commands/corosync/corosync-objctl_-a")):
            with open(str(path[int(z)]) + "sos_commands/corosync/corosync-objctl_-a", "r") as coro:
                for line in coro:
                    if (line.find("Failed to initialize the cmap API")) != -1:
                        cluster_notrunning = 1
                        break
                    if (line.find("ip(")) != -1:
                        ip.append(line)
                    if (line.find("cluster.clusternodes.clusternode.name")) != -1:
                        ring_rhel6.append(line)
                    if (line.find("cluster.name")) != -1:
                        cluster_name.append((line.split('cluster.name=')[1]).strip())
                        print(" - Cluster Name: %s\n"%cluster_name[0])
                ip.sort()        
                for i in ip:
                    final_ip.append((i.split('ip(')[1]).split(')')[0])
                for i in ring_rhel6:
                    final_ring.append((i.split('cluster.clusternodes.clusternode.name=')[1]).strip()) 
            break

    if len(cluster_name) == 0:
        z = 0
        for z in range(z, int(node)):
            if os.path.exists(str(path[int(z)]) + "/etc/corosync/corosync.conf"):
                with open(str(path[int(z)]) + "/etc/corosync/corosync.conf", "r") as ifile:
                    temp = ifile.readlines()
                    for line in temp:
                        if re.search("cluster_name", line):
                            cluster_name.append((line.split(': ')[1]).strip())
                            print(" - Cluster Name: %s\n"%cluster_name[0])
            break

    i = 0
    for i in range(i, len(final_ip)):
        k = 0
        z = 0
        for z in range(z, int(node)):
            if ((typeos == str("rhel7")) or (typeos == str("rhel8"))) & (os.path.exists(str(path[int(z)]) + "sos_commands/networking/ip_-o_addr")):
                with open(str(path[int(z)]) + "sos_commands/networking/ip_-o_addr", "r") as nic:
                    for line in nic:
                        line_new = (line.split('/')[0]).split('inet')[1].strip()
                        if line_new.find(final_ip[i]) != -1:
                            interface.append((line.split('inet')[0].split()[1]))
                            k = 1
                            break
            elif (typeos == str("rhel6"))& (os.path.exists(str(path[int(z)]) + "sos_commands/networking/ip_-o_addr")):
                with open(str(path[int(z)]) + "sos_commands/networking/ip_-o_addr", "r") as nic:
                    for line in nic:
                        if line.find('inet') != -1:
                            line_new = (line.split('/')[0]).split('inet')[1].strip()
                            if line_new.find(final_ip[i]) != -1:
                                interface.append((line.split('inet')[0].split()[1]))
                                k = 1
                                break
        if k == 0:
            interface.append("N/A")

    y = PrettyTable(["Node ID", "Ring ID", "Ring IP", "Interface", "Cluster Node Name"])
    y.align["Value"] = "l"
    i = 0
    m = 0
    for i in range(i, actualnode):
        k = 1
        j = 1
        n = 0
        q = int((len(final_ip)/actualnode))
        l = int((len(final_ip)/actualnode) + 1)

        if (typeos == str("rhel8")) & (len(final_ip) > len(final_ring)):
            if (len(final_ip) % len(final_ring) == 0):
                b = 1
                r = q
                for i in range(i, actualnode):
                    for b in range(b, q):
                        final_ring.insert(b, " ")
                        r = r + 2
                    b = 2

        for j in range(j, l):
            if k == 1:
                y.add_row([i+1, "ring" + str(n) + "_addr", final_ip[m], interface[m], final_ring[m]])
                n = n + 1
                k = 2
            else:
                y.add_row(["", "ring" + str(n) + "_addr", final_ip[m], interface[m], final_ring[m]])
                n = n + 1
            m = m + 1
        y.add_row(["", "", "", "", ""])
    
    if (len(final_ip) == len(final_ring)) & (cluster_notrunning == 0):
        print(y)
    else:
        print(" - Seems like cluster is not running, so ring details cannot be determined.\n")

    #******************************* Ends *******************************#

    ##### Validate if the interface has DHCP enabled #####

    def dhcp_fun():
        dhcp = 0
        r = 0
        for r in range(0, int(node)):
            for inface in interface:
                if inface != "N/A":
                    if os.path.exists(str(path[int(r)]) + "/etc/sysconfig/network-scripts/ifcfg-" + inface):
                        nw_script = open(str(path[int(r)]) + "/etc/sysconfig/network-scripts/ifcfg-" + inface, "r")
                        nw = nw_script.read()
                        nw_entry = nw.split("\n")
                        for entry in nw_entry:
                            if re.search('BOOTPROTO', entry):
                                if re.search('dhcp', entry):
                                    dhcp = 1
                                break
        return dhcp
        # if dhcp == 1:
        #     print('\n\t***** Validating if the HB interface configured with DHCP *****\n')
        #     print("\033[1;31m {}\033[00m".format("ALERT") + ": Heartbeat interface is configured with DHCP. The use of DHCP for obtaining an ip address on a network interface that it utilized by the corosync daemon is *not* supported. Refer KCS: https://access.redhat.com/solutions/1529133 .\n")


    #******************************* Ends *******************************#

    ##### Compare the cluster package version across all the cluster nodes #####

    print("\n\t***** Validating the Cluster packages version across the nodes ***** \n")

    z = 0
    pkg = ['^pcs-', '^ctdb', '^pacemaker-1', '^pacemaker-2', '^dlm', '^gfs2-utils', '^resource-agents', '^corosync-2', '^corosync-3', '^clusterlib', '^cman', '^lvm2-cluster', '^lvm2-2', '^libqb', '^rgmanager', '^ccs', '^ricci', '^fence-agents-common', '^resource-agents-sap', '^corosync-qdevice']
    res = []
    resnew = []
    resnewer = []
    match = 0
    nomatch = 0    
    i = 0

    for i in range(i, len(pkg)):  
        h = open(str(path[int(0)]) + "/installed-rpms", "r")
        hp = h.read()
        fl = hp.split("\n")
        res = [n for n in fl if re.search(pkg[int(i)], n)]
        resnewer = [ resnew.split(None, 1)[0] for resnew in res ]
        locals()["node_{}".format(u[int(0)])] = []
        for n in resnewer:
            locals()["node_{}".format(u[int(0)])].append(n)
        h.close()
        
        r = 0
        for r in range(r, int(node)):
            h = open(str(path[int(r)]) + "/installed-rpms", "r")
            hp = h.read()
            fl = hp.split("\n")
            res = [n for n in fl if re.search(pkg[int(i)], n)]
            resnewer = [ resnew.split(None, 1)[0] for resnew in res ]
            locals()["node_new_{}".format(u[int(r)])] = []
            for n in resnewer:
                locals()["node_new_{}".format(u[int(r)])].append(n)
            if locals()["node_new_{}".format(u[int(r)])] != locals()["node_{}".format(u[int(0)])]:
                pkg_mismatch.append(pkg[int(i)])
                nomatch = 1
                if len(locals()["node_new_{}".format(u[int(r)])]) != len(locals()["node_{}".format(u[int(0)])]):
                    pkg_duplicate.append(pkg[int(i)])
                break
            else:
                match = 1    

    # print(str(pkg_mismatch) + "\n")
    # print(str(pkg_duplicate) + "\n")

    if match == 1 and nomatch == 0:
        print(" - All cluster packages are same over all the sosreport shared for analysis.\n")
    elif nomatch == 1:
        print("\033[1;31m {}\033[00m".format("ALERT") + " : All cluster nodes are not running on same cluster package version.\nMismatch of cluster packages version is not supported. Please refer KCS: https://access.redhat.com/articles/3069091 .")
        i = 0
        for i in range(i, len(pkg_mismatch)):
            try:
                for n in pkg_mismatch:
                    if re.search(pkg_duplicate[int(i)].strip('^'), n):
                        print("\nDuplicate package for '" + str(pkg_mismatch[int(i)].strip('^')) + "' found:")
                        break
            except IndexError:
                print("\nPackage '" + str(pkg_mismatch[int(i)].strip('^')) + "' is not same across the cluster nodes.")
            print("\n\tNode\t\t\tPackage version")
            print("\t----------------------------------------------------------")
            z = 0
            for z in range(z, int(node)):
                h = open(str(path[int(z)]) + "/installed-rpms", "r")
                hp = h.read()
                fl = hp.split("\n")
                res = [n for n in fl if re.search(pkg_mismatch[int(i)], n)]
                resnewer = [ resnew.split(None, 1)[0] for resnew in res ]
                if len(resnewer) > 1:
                    print("\t" + str(u[int(z)]), end =" ")
                    ji = []
                    for j in range(len(resnewer)):
                        ji.append(j)
                    j = 0
                    for n,j in zip(resnewer,ji):
                        if j == 0:
                            print("\t\t" + str(n.strip('^')))
                        else:
                            print("\t\t\t\t" + str(n.strip('^')))
                else:
                    try:
                        print("\t" + str(u[int(z)]) + "\t\t\t" + str(resnewer[0].strip('^')))
                    except IndexError:
                        print("\t" + str(u[int(z)]) + "\t\t\tdoes not have " + str(pkg_mismatch[int(i)].strip('^')) + " installed.")


    #******************************* Ends *******************************#

    ##### Check all cluster packages are Red Hat shipped #####

    z = 0
    nonrhel = []
    res = []
    resnew = []
    resnewer = []
    nonrhel_dict = {}
    vendor = []
    pkg = ['^pcs-', '^ctdb', '^pacemaker', '^dlm', '^gfs2-utils', '^resource-agents', '^corosync-2', '^corosync-3', '^clusterlib', '^cman', '^lvm2-cluster', '^lvm2-2', '^libqb', '^rgmanager', '^ccs', '^ricci', '^fence-agents-common', '^resource-agents-sap', '^corosync-qdevice']
    i = 0
    for i in range(i, len(pkg)):  
        r = 0
        for r in range(r, int(node)):
            if os.path.exists(str(path[int(r)]) + "/sos_commands/rpm/package-data"):
                z = 1
                h = open(str(path[int(r)]) + "/sos_commands/rpm/package-data", "r")
                hp = h.read()
                fl = hp.split("\n")
                res = [n for n in fl if re.search(r'\b' + pkg[int(i)]+ r'\b', n)]
                resnewer = [ resnew.split(None, 9)[7] for resnew in res ]
                locals()["node_new_{}".format(u[int(r)])] = []
                for n in resnewer:
                    locals()["node_new_{}".format(u[int(r)])].append(n)
                h.close()
                try:
                    if resnewer[0] != 'Red':
                        nonrhel.append(pkg[int(i)].strip('^'))
                        nonrhel_dict.update({pkg[int(i)].strip('^'): resnewer[0]})
                except IndexError:
                    break
                # break 
    
    if (len(nonrhel) != 0) & (z == 1):
        print("\n\t***** Validating the installed Cluster packages are Red Hat shipped ***** \n")
        print("\033[1;31m {}\033[00m".format("ALERT") + " : The following installed packages are non-RHEL " + str(set(nonrhel)) + ".")
        for key,value in nonrhel_dict.items():
            vendor.append(value)
        if len(set(vendor)) == 1:
            print('\t All the above list of package(s) are shipped by '+ vendor[0] + '.\n')
        else:
            for key,value in nonrhel_dict.items():
                print('\t The cluster package "' + key + '" is shipped by ' + value + '.')
    elif (len(nonrhel) == 0) & (z == 1):
        print("")  # No need to print anything as all the cluster packages are Red Hat shipped.
    elif (len(nonrhel) == 0) & (z == 0):
        print("The file 'package-data' is not captured in sosreport, so script cannot validate if all cluster packages are Red Hat shipped.\n")


    #******************************* Ends *******************************#

    ##### Get the cluster configuration #####

    print ("\n\t***** Getting the Cluster Status *****\n")

    def clu_stats(config):
        global path
        global node
        if rgmanager != 1:
            z = 0
            for z in range(z, int(node)):
                exist = os.path.exists(str(location[int(z)]) + config)
                newflag = "nofile"
                if exist:
                    newflag = ""
                    with open(str(location[int(z)]) + "pcs_config", 'r') as fin:
                        fin = open(str(location[int(z)]) + "pcs_config", 'r')
                        for line in fin:
                            if re.match("Error: error running crm_mon, is pacemaker running?", line) or re.match("Error: unable to get cib", line):
                                newflag = True
                                fin.close()
                                pcs = "Cluster is not running"
                                break
                        else:
                            newflag = False
                            fin = open(str(location[int(z)]) + config, 'r')
                            pcs = fin.read()
                            fin.close()
                            break
                z = z + 1
            if newflag == "nofile":
                pcs = "Cluster status/configuration is not captured in sosreport."
            return pcs, newflag
        elif rgmanager == 1:
            print(" - This script can get the status for Pacemaker cluster only..!!")

    if rgmanager != 1: 
        pcsstatus, newflag = (clu_stats("pcs_status"))
        if newflag == True:
            print("\n\033[1;33m {}\033[00m".format("WARNING:") + " - Cluster is not running on any of the node from which sosreport are shared.")
        elif newflag == "nofile":
            pcsstatus, newflag = (clu_stats("pcs_status_--full"))
            if newflag == "nofile":
                print("\n\033[1;33m {}\033[00m".format("WARNING:") + " - Cluster status/configuration files not captured in any of the sosreport.")
            elif newflag == True:
                print("\n\033[1;33m {}\033[00m".format("WARNING:") + " - Cluster is not running on any of the node from which sosreport are shared.")
        elif newflag == False:
            print("\n - Cluster Status/Configuration is captured, proceeding ahead ...")

    #******************************* Ends *******************************#

    ##### Validating Stonith Status for Supportability #####

    azure = 0
    aws = 0
    gcp = 0
    cib_exists = 0
    if rgmanager != 1:
        global maintmode
        if (newflag == False) or (newflag == True):
            z = 0
            # cib_exists = 0

            def stonithconf(cib):
                global path
                global node
                global iofence
                global only_kdump
                global sbd
                global aws
                global azure
                global gcp
                iofence = 0
                only_kdump = 0
                sbd = 0
                print("\n\t***** Validating the Stonith configuration *****\n")
                global stonithenabled
                global ssh_fence
                mycib = ET.parse(cib)
                myroot = mycib.getroot()
                lst = myroot[0].findall('resources/primitive')
                for item in lst:
                    if item.get('class') == 'stonith':
                        fencedevices.append(item.get('type'))
                        print("\nStonith Details\n----------------\nName: %s \nType: %s "%(item.get('id'),item.get('type')))
                        if (item.get('type') == 'fence_scsi') or (item.get('type') == 'fence_mpath'):
                            iofence = 1
                        if (item.get('type') == 'fence_aws'):
                            aws = 1
                        if (item.get('type') == 'fence_sbd'):
                            sbd = 1
                        if (item.get('type') == 'fence_azure_arm'):
                            azure = 1
                        if (item.get('type') == 'fence_gce'):
                            gcp = 1

                if len(set(fencedevices)) == 0:
                    lst = myroot[0].findall('resources/group/primitive')
                    for item in lst:
                        if item.get('class') == 'stonith':
                            fencedevices.append(item.get('type'))
                            print("\nStonith Details\n----------------\nName: %s \nType: %s "%(item.get('id'),item.get('type')))
                            if (item.get('type') == 'fence_scsi') or (item.get('type') == 'fence_mpath'):
                                iofence = 1
                            if (item.get('type') == 'fence_aws'):
                                aws = 1
                            if (item.get('type') == 'fence_sbd'):
                                sbd = 1
                            if (item.get('type') == 'fence_azure_arm'):
                                azure = 1
                            if (item.get('type') == 'fence_gce'):
                                gcp = 1
                    if len(set(fencedevices)) != 0:
                        print("\n\033[1;33m {}\033[00m".format("WARNING:") + " The fence resource is configured under a resource group. Please remove stonith from resource group using command: 'pcs resource group remove <Group ID> <Stonith ID>'")

                if (len(set(fencedevices)) == 1):
                    if fencedevices[0] == 'fence_kdump':
                        only_kdump = 1
                        print("\n\033[1;33m {}\033[00m".format("WARNING:") + " Cluster is running with only 'fence_kdump' as the fence agent. You must configure a valid power fence agent and fence level with KCS: https://access.redhat.com/solutions/891323 .")
                if len(set(fencedevices)) > 1:
                    print("\n\t----------- Fencing Topolgy -----------")
                    lst1 = myroot[0].findall('fencing-topology/')
                    if len(lst1) == 0:
                        print("\nCluster has multiple fence agents configured but no fence level configured. It is recommended to configure fence level. Please refer: https://access.redhat.com/solutions/891323 .")
                    for item in lst1:
                        if item.get('index') == str(1):
                            print("\n1st Fencing Level\n------------------\nDevice: %s \nTarget: %s"%(item.get('devices'),item.get('target')))
                        else:
                            print("\n2nd Fencing Level\n------------------\nDevice: %s \nTarget: %s" % (item.get('devices'),item.get('target')))
                doc = xml.dom.minidom.parse(cib)
                group = doc.getElementsByTagName("nvpair")
                for i in group:
                    if (i.getAttribute("name") == "stonith-enabled") & (i.getAttribute("value") == "false"):
                        stonithenabled = 0
                        break
                    continue
                if (len(fencedevices) == 0) & (stonithenabled == 1):
                    print("\n\033[1;31m {}\033[00m".format("ALERT") + " : NO fence resource is configured. We highly recommend you to configure fence device as cluster without fencing is not supported." + "\n" +" Support Policies for RHEL High Availability Clusters - General Requirements for Fencing/STONITH -- https://access.redhat.com/articles/2881341 .\n")
                elif (len(fencedevices) == 0) & (stonithenabled == 0):
                    print("\n\033[1;31m {}\033[00m".format("ALERT") + " : NO fence resource is configured. We would recommend you to configure fence device as cluster without fencing is not supported." + "\n" + " Support Policies for RHEL High Availability Clusters - General Requirements for Fencing/STONITH -- https://access.redhat.com/articles/2881341 ." + "\n\n" + " - In addition, the cluster property for 'stonith-enabled' is set to false. Refer KCS article:" + "\n" + " 'How to set stonith-enabled to true in a Pacemaker cluster' -- https://access.redhat.com/solutions/2476841 .\n")
                elif (len(fencedevices) != 0) & (stonithenabled == 0):
                    print("\n\033[1;31m {}\033[00m".format("ALERT") + " : Although the fence resource is configured, the cluster property for 'stonith-enabled' is set to false. Refer KCS article:" + "\n" + " 'How to set stonith-enabled to true in a Pacemaker cluster' -- https://access.redhat.com/solutions/2476841 .")

                ssh_fence = 0
                for fen in fencedevices:
                    if re.search('fence_ilo._ssh', fen):
                        ssh_fence = 1
                
                if ssh_fence == 1:
                    print("\n\033[1;33m {}\033[00m".format("WARNING:") + " The fence agent 'fence_ilo{3,4,5}_ssh' is susceptible to random failure in checking the status. Although this fence agent can be used, however it is recommended to use fence_ipmilan instead. Refer KCS: https://access.redhat.com/solutions/4040221 .\n")

            for z in range(z, int(node)):
                crm_report = False
                repeat = "Yes"
                print(" - Checking for cib.xml file existance & proceeding ahead ...")
                for cibexists in glob.iglob(str(location[int(z)]) + '/crm_report/*/'):
                    crm_report = True
                    break

                
                if crm_report == True:
                    for root, dirs, files in os.walk(cibexists):
                        if 'cib.xml' in files:
                            cib_exists = 1
                            repeat = "No"
                            print(" - cib.xml file found... ")
                            cib = os.path.join(root, 'cib.xml')
                        break
                    
                if (cib_exists == 0) & (repeat == "Yes"):
                    for cibexists in glob.iglob(str(path[int(z)]) + '/var/lib/pacemaker/cib/'):
                        if os.path.exists(cibexists):
                            for root, dirs, files in os.walk(cibexists):
                                if 'cib.xml' in files:
                                    cib_exists = 1
                                    print(" - cib.xml file found... ")
                                    cib = os.path.join(root, 'cib.xml')
                                break
                            break
                        break

                if cib_exists == 1:
                    doc = xml.dom.minidom.parse(cib)
                    group = doc.getElementsByTagName("nvpair")
                    for i in group:
                        if (i.getAttribute("name") == "maintenance-mode") & (i.getAttribute("value") == "true"):
                            maintmode = 1
                            print(" - Cluster is running with maintenance-mode enabled.")
                            break
                    # stonithconf(cib)
                elif cib_exists == 0:
                    nocib = 1
                    print("\033[1;33m {}\033[00m".format("WARNING:") + " cib.xml file is not captured on any of the sosreport.")
                    break
                break
                z = z + 1
            
            global sbd
            stonith = pcsstatus.find("sbd")
            if stonith != -1:
                sbd = 1
    elif rgmanager == 1:
            print(" - This script is capable to get the status for Pacemaker cluster only..!!\n")

    #******************************* Ends *******************************#

    ##### Validating the DC node ID and DC node name #####

    dc_nodeID = "no_ID"
    dc_nodeName = "no_name"
    if ((cib_exists == 1) or (nocib == 0)) and rgmanager != 1:
        doc = xml.dom.minidom.parse(cib)
        dc_id = doc.getElementsByTagName("cib")
        for i in dc_id:
            dc_nodeID = i.getAttribute("dc-uuid")

        dc_name = doc.getElementsByTagName("node")
        for i in dc_name:
            if i.getAttribute("id") == dc_nodeID:
                dc_nodeName = i.getAttribute("uname")

        if (dc_nodeID != "no_ID") & (dc_nodeName != "no_name"):
            print(" - DC node ID is " + str(dc_nodeID) +" and DC nodename is " + str(dc_nodeName) + ".")

    #******************************* Ends *******************************#

    ##### Validating the fence configuration of pcmk_host_list/map #####

    if ((cib_exists == 1) or (nocib == 0)) and rgmanager != 1:
        stonithconf(cib)   ### This is printing the stonith details
        pcmk_map = []
        pcmk_list = []
        fence_ip = []
        doc = xml.dom.minidom.parse(cib)
        group = doc.getElementsByTagName("nvpair")
        for i in group:
            if (i.getAttribute("name") == "pcmk_host_map"):
                pcmk_map.append(i.getAttribute("value"))
            if (i.getAttribute("name") == "pcmk_host_list"):
                pcmk_list.append(i.getAttribute("value"))
            if (i.getAttribute("name") == "ipaddr"):
                fence_ip.append(i.getAttribute("value"))

        group_primitive = doc.getElementsByTagName("primitive")
        fence_name = []
        for i in group_primitive:
            if i.getAttribute("class") == "stonith":
                fence_name.append(i.getAttribute("id"))
        
        fence_disabled = []
        for j in fence_name:
            for i in group:
                if i.getAttribute("id") == str(str(j) + "-meta_attributes-target-role"):
                    if (i.getAttribute("name") == "target-role") & (i.getAttribute("value") == "Stopped"):
                        fence_disabled.append(str(j))


        pcmk_host_map1 = []
        k = 0
        for k in range(k, len(pcmk_map)):
            for i in pcmk_map[k].split(";"):
                pcmk_host_map1.append(i.split(":")[0])

        pcmk_host_map2 = []
        k = 0
        for k in range(k, len(pcmk_map)):
            for i in pcmk_map[k].split(" "):
                pcmk_host_map2.append(i.split(":")[0])

        pcmk_host_list1 = []
        k = 0
        for k in range(k, len(pcmk_list)):
            for i in pcmk_list[k].split(" "):
                pcmk_host_list1.append(i)

        pcmk_host_list2 = []
        k = 0
        for k in range(k, len(pcmk_list)):
            for i in pcmk_list[k].split(","):
                pcmk_host_list2.append(i)

        if len(pcmk_host_map1) > len(pcmk_host_map2):
            pcmk_host_map = pcmk_host_map1
        else:
            pcmk_host_map = pcmk_host_map2

        if len(pcmk_host_list1) > len(pcmk_host_list2):
            pcmk_host_list = pcmk_host_list1
        else:
            pcmk_host_list = pcmk_host_list2

        if len(final_ring) == 0:
            if typeos == str("rhel7"):
                z = 0
                for z in range(z, int(node)):
                    if (os.path.exists(str(path[int(z)]) + "etc/corosync/corosync.conf")):
                        fin = open(str(path[int(z)]) + "etc/corosync/corosync.conf", 'r')
                        for line in fin:
                            if line.find("ring0_addr") != -1:
                                line = line.strip()
                                final_ring.append(line.split("ring0_addr: ")[1])
                        fin.close()
                    break
            elif typeos == str("rhel8"):
                z = 0
                for z in range(z, int(node)):
                    if (os.path.exists(str(path[int(z)]) + "etc/corosync/corosync.conf")):
                        fin = open(str(path[int(z)]) + "etc/corosync/corosync.conf", 'r')
                        for line in fin:
                            if line.find("name") != -1:
                                line = line.strip()
                                final_ring.append(line.split("name: ")[1])
                        fin.close()
                    break

        i=0
        correct_map = 0
        for i in set(pcmk_host_map):
            j=0
            for j in range(j, len(final_ring)):
                if i == final_ring[j]:
                    correct_map = correct_map + 1
                    break
        
        correct_list = 0
        for i in set(pcmk_host_list):
            j=0
            for j in range(j, len(final_ring)):
                if i == final_ring[j]:
                    correct_list = correct_list + 1
                    break

        if (correct_map != len(pcmk_host_map)) & (correct_map != len(final_ring)):
            print("\n\033[1;33m {}\033[00m".format("WARNING:") + " The value of pcmk_host_map needs a correction else fence failures will be reported. Refer: https://access.redhat.com/solutions/2619961")
        
        if (correct_list != len(pcmk_host_list)) & (correct_list != len(final_ring)):
            print("\n\033[1;33m {}\033[00m".format("WARNING:") + " The value of pcmk_host_list needs a correction else fence failures will be reported. Refer: https://access.redhat.com/solutions/2619961")

        if len(fence_ip) > 1:
            if len(set(fence_ip)) == 1:
                print("\n - All fence resources are configured to connect with same IP " + str(fence_ip[0]) + ", hence a single fence resource can be used in place of multiple resources.")

        if len(fence_disabled) != 0:
            print("\n\033[1;33m {}\033[00m".format("WARNING:") + " The following fence resource(s) are disabled: " + str(fence_disabled) + ".\n")

        if (len(pcmk_host_list) == 0) & (len(pcmk_host_map) == 0) & (sbd !=1 ) & (len(fencedevices) != 0):
            if (len(pcmk_host_list) == 0):
                print("\n - None of the fence resources are configured with 'pcmk_host_list' parameter. This will need a correction as fence resources must be defined with 'pcmk_host_list'.")
            elif (len(pcmk_host_map) == 0):
                print("\n - None of the fence resources are configured with 'pcmk_host_map' parameter. This will need a correction as fence resources must be defined with 'pcmk_host_map'.")

    #******************************* Ends *******************************#

    ##### Verify if fence agent is valid for the platform #####

    global platform_fence_compatible
    hardware = hwtype(0)
    if (len(fencedevices) != 0):
        for i in fencedevices:
            if (hardware.find("VMware") != -1):
                if ((str(i) != 'fence_vmware_soap') and (str(i) != 'fence_vmware_rest') and (str(i) != 'fence_scsi') and (str(i) != 'fence_mpath') and (str(i) != 'fence_kdump')):
                    platform_fence_compatible = 0
            elif re.search('HP|Lenovo|IBM|LENOVO|Cisco', hardware):
                if ((str(i) != 'fence_ipmilan') and (str(i) != 'fence_scsi') and (str(i) != 'fence_mpath') and (str(i) != 'fence_kdump') and (str(i) != 'fence_idrac') and (str(i) != 'fence_cisco_ucs') and (str(i) != 'fence_sbd')) and (not re.search('fence_ilo.+', str(i))):
                    platform_fence_compatible = 0
            elif (hardware.find("Google") != -1):
                if ((str(i) != 'fence_gce') and (str(i) != 'fence_kdump')):
                    platform_fence_compatible = 0
            elif (hardware.find("Amazon EC2") != -1):
                if ((str(i) != 'fence_aws') and (str(i) != 'fence_kdump')):
                    platform_fence_compatible = 0
            elif (hardware.find("Microsoft Corporation") != -1):
                if ((str(i) != 'fence_azure_arm') and (str(i) != 'fence_kdump')):
                    platform_fence_compatible = 0

    if platform_fence_compatible == 0:
        print("\n\033[1;31m {}\033[00m".format("ALERT:") + " The fence agent %s is incompatible with the platform %s."%(str(i),hardware))

    #******************************* Ends *******************************#

    ##### Suggest the fence device to be configured provided environment as a whole is supported #####

    global supported
    global ssh_fence
    global iofence
    hardware = hwtype(0)
    if rgmanager != 1:
        hwlist = 'HP|Dell|Cisco|Lenovo|VMware|KVM|RHEV|Google|Amazon EC2|Microsoft Corporation|IBM|LENOVO'
        phyHW = 'HP|Dell|Lenovo|IBM|LENOVO'   ## Removed 'Cisco' from this list
        cloudHW = 'Google|Amazon EC2|Microsoft Corporation'
        if re.search(hwlist, hardware):
            supported = 1
        else:
            supported = 0

        if (supported == 0) & (re.match("empty_file", hdware) == None) & (re.match("no_file", hdware) == None):
            if re.search("OpenStack", hardware):
                print("\n\033[1;33m {}\033[00m".format("WARNING:") + " The cluster environment is configured over OpenStack VMs which is not supported. Refer KCS: https://access.redhat.com/articles/3131311 .")
            elif re.search("Xen", hardware):
                if (aws == 0):
                    print("\n\033[1;33m {}\033[00m".format("WARNING:") + " The cluster environment is configured over Xen systems which is not supported. Refer KCS: https://access.redhat.com/articles/3131361 .")
            elif re.search("Nutanix", hardware):
                print("\n\033[1;33m {}\033[00m".format("WARNING:") + " The cluster environment is configured over Nutanix AHV which is not a supported platform for RHEL. Refer KCS: https://access.redhat.com/solutions/3432561 .")            
            else:
                print("\n\033[1;33m {}\033[00m".format("WARNING:") + " Please check if the hardware '" + str(hardware) + "' is supported for RHEL Cluster Setup or not.")

        elif (supported == 1) & ((cib_exists == 1) or (nocib == 0)):
            if ((len(fencedevices) == 0) & (sbd == 0)) or (only_kdump == 1) or (platform_fence_compatible == 0):
                print("\n\t***** Fence Agent recommendation *****")
                if (hardware.find("VMware") != -1):
                    if (typeos == str("rhel6")):
                        print("\n - Since the environment is configured over " + hardware + ", please configure 'fence_vmware_soap' fence agent as detailed in KCS: https://access.redhat.com/solutions/68064 .")
                    else:
                        print("\n - Since the environment is configured over " + hardware + ", please configure 'fence_vmware_soap' fence agent as detailed in KCS: https://access.redhat.com/solutions/917813 .")
                elif re.search(phyHW, hardware):
                    print("\n - Since the environment is configured over hardware " + hardware + ", please configure 'fence_ipmilan' fence agent as detailed in KCS: https://access.redhat.com/solutions/2271811 .")
                elif (hardware.find("Cisco") != -1):
                    print("\n - Since the environment is configured over Cisco, please configure 'fence_cisco_ucs' fence agent as detailed in KCS: https://access.redhat.com/solutions/31225 .")
                elif (hardware.find("KVM") != -1):
                    print("\n - Since the environment is configured over KVM, please configure 'fence_xvm' fence agent as detailed in KCS: https://access.redhat.com/solutions/917833 . If KVMs are running on separate hosts, then refer: https://access.redhat.com/solutions/2386421 .")
                elif (hardware.find("RHEV") != -1):
                    print("\n - Since the environment is configured over RHEV, please configure 'fence_rhevm' fence agent as detailed in KCS: https://access.redhat.com/articles/3335601 .")
                elif re.search("Google", hardware):
                    print("\n - Since the environment is configured over GCP, please configure 'fence_gce' fence agent as detailed in KCS: https://access.redhat.com/articles/3479821 .")
                elif re.search("Amazon EC2", hardware):
                    print("\n - Since the environment is configured over AWS, please configure 'fence_aws' fence agent as detailed in KCS: https://access.redhat.com/articles/3354781 .")
                elif re.search("Microsoft Corporation", hardware):
                    print("\n - Since the environment is configured over Azure, please configure 'fence_azure_arm' fence agent as detailed in KCS: https://access.redhat.com/articles/3252491 .")
                else:
                    print("\n - Contact Red Hat Techincal Support team for the correct fence agent to be configured in your environment via customer portal 'access.redhat.com'.")

            elif (newflag == False) & (hardware.find("VMware") != -1):
                if (len(set(fencedevices)) == 1) & (iofence == 1):
                    print("\n\033[1;33m {}\033[00m".format("WARNING:") + " You are currently using only I/O fence agent " + str(set(fencedevices)) + " in VMware platform. Please ensure the pre-requisites are met. Refer: https://access.redhat.com/articles/3078811 .\n")
                elif (iofence == 1):
                    print("\n\033[1;33m {}\033[00m".format("WARNING:") + " You are using I/O fence agent " + str(set(fencedevices)) + " in VMware platform. Please ensure the pre-requisites are met. Refer: https://access.redhat.com/articles/3078811 .\n")
                elif (sbd == True):
                    if (len(set(fencedevices)) == 0):
                        print("\n\033[1;31m {}\033[00m".format("ALERT:") + " You are currently using sbd as fence agent in your VMware environment. Please note: this fence agent is not supported in VMware due to unavailability of software watchdog (KCS: https://access.redhat.com/articles/2800691). Hence please configure 'fence_vmware_soap'." + "\n")
                    else:
                        print("\n\033[1;31m {}\033[00m".format("ALERT:") + " You are currently using fence_sbd/sbd as fence agent in your VMware environment. Please note: this fence agent is not supported in VMware due to unavailability of software watchdog (KCS: https://access.redhat.com/articles/2800691). Hence please configure 'fence_vmware_soap'." + "\n")
                    if (typeos == "rhel6"):
                        print(" - Refer KCS article for fence_vmware_soap: https://access.redhat.com/solutions/68064 .\n")
                    elif (typeos == "rhel7") or (typeos == "rhel8"):
                        print(" - Refer KCS article for fence_vmware_soap: https://access.redhat.com/solutions/917813 .\n")
            else:
                if ssh_fence == 0:
                    print("\n - Depending on the hardware '" + str(hardware) + "', cluster is configured using a correct fence agent.\n")
                if re.search("Microsoft Corporation", hardware):
                    print(" *NOTE* - The file 'dmidecode' says same for Hyper-V and Azure. Please ensure that the environment is Azure, because Hyper-V in cluster is not yet supported. Refer: https://access.redhat.com/articles/3131321 .")
        else:
            if ((cib_exists != 1) or (nocib != 0)):
                print("\n - Without cib.xml file being captured, the fence details cannot be captured.\n")
            elif (re.match("empty_file", hdware)):
                print("\n - Cannot determine the platform (hardware) as dmidecode file is empty. Please check with customer.")
            elif (re.match("no_file", hdware)):
                print("\n - Cannot determine the platform (hardware) as dmidecode file is not captured in sosreport. Please check with customer.")


    #******************************* Ends *******************************#

    ##### Checking login.defs file for hard reboot parameter in RHEL7 physical system #####

    z = 0
    graceful_reboot = []
    ignore_reboot = []
    if typeos == str("rhel7") or (typeos == "rhel8"):
        if re.search("HP", hardware) or re.search("Dell", hardware) or re.search("Cisco", hardware) or re.search("Lenovo", hardware) or re.search("IBM", hardware) or re.search("LENOVO", hardware):
            for z in range(z, int(node)):
                loc = os.path.exists(str(path[int(z)]) + "/etc/systemd/logind.conf")
                if loc:
                    with open(str(path[int(z)]) + "/etc/systemd/logind.conf", "r") as ifile:
                        temp = ifile.readlines()
                        grace = 1
                        for line in temp:
                            if line.startswith("HandlePowerKey"):
                                if re.search("ignore", line):
                                    grace = 0
                        if grace == 1:
                            clu_name = (str(u[int(z)]).split("."))[0]
                            graceful_reboot.append(clu_name)
                z = z + 1
    elif typeos == str("rhel6"):
        if re.search("HP", hardware) or re.search("Dell", hardware) or re.search("Cisco", hardware) or re.search("Lenovo", hardware) or re.search("IBM", hardware) or re.search("LENOVO", hardware):
            for z in range(z, int(node)):
                loc = os.path.exists(str(path[int(z)]) + "sos_commands/startup/chkconfig_--list")
                if loc:
                    with open(str(path[int(z)]) + "sos_commands/startup/chkconfig_--list", "r") as ifile:
                        temp = ifile.readlines()
                        for line in temp:
                            if re.search("acpid", line):
                                if re.search("3:on", line):
                                    clu_name = (str(u[int(z)]).split("."))[0]
                                    graceful_reboot.append(clu_name)
                z = z + 1

    if rgmanager != 1:
        if (len(graceful_reboot) != 0) & (typeos == str("rhel7")) & (iofence == 0):
            print("\033[1;33m {}\033[00m".format("WARNING:") + " The cluster node(s) " + str(graceful_reboot) + " is configured for graceful reboot & this may lead to fence failure. Refer KCS: https://access.redhat.com/solutions/1578823 .")
        elif (len(graceful_reboot) != 0) & (typeos == str("rhel8")) & (iofence == 0):
            print("\033[1;33m {}\033[00m".format("WARNING:") + " The cluster node(s) " + str(graceful_reboot) + " is configured for graceful reboot & this may lead to fence failure. Refer KCS: https://access.redhat.com/solutions/1578823 .")
        elif (len(graceful_reboot) != 0) & (typeos == str("rhel6")):
            print("\033[1;33m {}\033[00m".format("WARNING:") + " The cluster node(s) " + str(graceful_reboot) + " is configured for graceful reboot & this may lead to fence failure. Refer KCS: https://access.redhat.com/solutions/5414 .")

        
    #******************************* Ends *******************************#

    ##### HP-ASRD status of the cluster node #####

    # From sosreport we can only detemine the status via "chkconfig" on RHEL6

    z = 0
    status = 0
    kcs = 0
    hpasr = []
    if typeos == str('rhel6'):
        for z in range(z, int(node)):
            if re.search("HP", hardware):
                flag = 0
                if (os.path.exists(str(path[int(z)]) + "/sos_commands/startup/chkconfig_--list")):
                    hpasr_file = open(str(path[int(z)]) + "/sos_commands/startup/chkconfig_--list", "rt")
                    contents = hpasr_file.readlines()
                    for line in contents:
                        if re.search("hp-asrd", line):
                            flag = 1
                            status = 1
                            if re.search("on", line):
                                flag = 2

                    if flag == 1:
                        hpasr.append("ASR is disabled.")
                    elif flag == 2:
                        hpasr.append("ASR is enabled.")
                        kcs = 1
                    elif flag == 0:
                        hpasr.append("ASR service not found.")
    
    if status == 1:
        print("\n\t***** HP-ASR Service status *****\n")
        z = 0
        for z in range(z, int(node)):
            print(" - On cluster node " + (str(u[int(z)]).split("."))[0] + ", " + str(hpasr[int(z)]))
        if kcs == 1:
            print("\n\033[1;33m {}\033[00m".format("WARNING:") + " ASR service should be disabled. Please refer article: https://access.redhat.com/solutions/501543.")


    #******************************* Ends *******************************#

    ## DHCP Continued ... ##
    
    dhcp = dhcp_fun()
    if (dhcp == 1) & (azure != 1) & (aws != 1) & (gcp != 1) & (len(fencedevices) != 0):
        print('\n\t***** Validating if the HB interface configured with DHCP *****\n')
        print("\033[1;31m {}\033[00m".format("ALERT") + ": Heartbeat interface is configured with DHCP. The use of DHCP for obtaining an ip address on a network interface that it utilized by the corosync daemon is *not* supported. Refer KCS: https://access.redhat.com/solutions/1529133 .\n")

    #******************************* Ends *******************************#

    ##### Read corosync.conf/cluster.conf file entries #####

    def corosync(word):
        global path
        global node
        corosync_value = []
        if typeos == str("rhel7") or (typeos == "rhel8"):
            z = 0
            for z in range(z, int(node)):
                flag = 0
                loc = os.path.exists(str(path[int(z)]) + "/etc/corosync/corosync.conf")
                if loc:
                    with open(str(path[int(z)]) + "/etc/corosync/corosync.conf", "r") as ifile:
                        temp = ifile.readlines()
                        for line in temp:
                            if re.search(word, line):
                                corosync_value.append((line.split(": ")[1]).strip())
                                flag = 1
                                break
                        if flag != 1:
                            corosync_value.append(str(" - "))
                    ifile.close()
                else:
                    corosync_value.append("no-corosync-file")
            # print(corosync_value)
            return(corosync_value)
        elif (typeos == str("rhel6")) & (word != "rrp_mode"):
            z = 0
            flag = 0
            for z in range(z, int(node)):
                loc = os.path.exists(str(path[int(z)]) + "/etc/cluster/cluster.conf")
                if loc:
                    with open(str(path[int(z)]) + "/etc/cluster/cluster.conf", "r") as ifile:
                        temp = ifile.readlines()
                        for line in temp:
                            if re.search(word, line):
                                corosync_value.append((line.split(str(word) + "=")[1].strip().strip('"/>')))
                                flag = 1
                                break
                        if flag != 1:
                            corosync_value.append(str(" - "))
                    ifile.close()
                else:
                    corosync_value.append("no-corosync-file")
            # print(corosync_value)
            return(corosync_value)          
        elif (typeos == str("rhel6")) & (word == "rrp_mode"):
            z = 0
            for z in range(z, int(node)):
                corosync_value.append(str(" - "))
            # print(corosync_value)
            return(corosync_value)
        else:
            corosync_value.append("rhel6")
            return (corosync_value)

    ##### Read runtime value of cluster via corosync-cmapctl #####

    def corosync_runtime(word):
        if typeos == str("rhel7") or (typeos == "rhel8"):
            z = 0
            corosync_runtime_value = []
            for z in range(z, int(node)):
                flag = 0
                loc = os.path.exists(str(path[int(z)]) + "sos_commands/corosync/corosync-cmapctl")
                if loc:
                    with open(str(path[int(z)]) + "sos_commands/corosync/corosync-cmapctl", "r") as ifile:
                        temp = ifile.readlines()
                        for line in temp:
                            if re.search(word, line):
                                corosync_runtime_value.append((line.split(" = ")[1]).strip())
                                flag = 1
                                break
                        if (flag != 1) & (word != str("totem.rrp_mode ")):
                            corosync_runtime_value.append(str("Cluster Stopped"))
                        elif (flag != 1):
                            corosync_runtime_value.append(str(" - "))
                    ifile.close()
                else:
                    corosync_runtime_value.append("no-corosync-cmapctl-file")
            # print(corosync_runtime_value)
            return(corosync_runtime_value)
        elif (typeos == str("rhel6")) & (word != str("totem.rrp_mode ")):
            z = 0
            flag = 0
            corosync_runtime_value = []
            for z in range(z, int(node)):
                loc = os.path.exists(str(path[int(z)]) + "sos_commands/corosync/corosync-objctl_-a")
                if loc:
                    with open(str(path[int(z)]) + "sos_commands/corosync/corosync-objctl_-a", "r") as ifile:
                        temp = ifile.readlines()
                        for line in temp:
                            if re.search(word, line):
                                corosync_runtime_value.append((line.split("=")[1]).strip())
                                flag = 1
                                break
                        if flag != 1:
                            corosync_runtime_value.append(str("Cluster Stopped"))
                    ifile.close()
                else:
                    corosync_runtime_value.append("no-corosync-objctl-file")
            # print(corosync_runtime_value)        
            return(corosync_runtime_value)
        elif (typeos == str("rhel6")) & (word == str("totem.rrp_mode ")):
            z = 0
            corosync_runtime_value = []
            for z in range(z, int(node)):
                corosync_runtime_value.append(' - ')
            # print(corosync_runtime_value)        
            return(corosync_runtime_value)

    ##### Confirm corosync.conf file is same across all nodes #####

    def corosync_conf_file_consistency():
        import hashlib
        global path
        global node
        md5 = []
        z = 0
        for z in range(z, int(node)):
            loc = os.path.exists(str(path[int(z)]) + "/etc/corosync/corosync.conf")
            if loc:
                with open(str(path[int(z)]) + "/etc/corosync/corosync.conf", "r") as ifile:
                    data = ifile.read()
                    md5_returned = hashlib.md5((data).encode()).hexdigest()
                    md5.append(md5_returned)
            else:
                md5.append('file-unavailable')

        # print(md5)
        if not 'file-unavailable' in md5:
            if len(set(md5)) != 1:
                return(False)
            else:
                return(True)

    #******************************* Ends *******************************#

    ##### Availability of corosync.conf file & corosync-cmapctl output file captured in sosreport #####

    test_corosync_conf = corosync("cluster_name")
    test_corosync_cmapctl = corosync_runtime("totem.cluster_name ")

    if test_corosync_conf[0] == "no-corosync-file":
        print("\n - None of the cluster node's sosreport has corosync.conf file captured.")
    if test_corosync_cmapctl[0] == "no-corosync-cmapctl-file":
        print("\n - None of the cluster node's sosreport has 'corosync-cmapctl' output file captured.")

    #******************************* Ends *******************************#

    ##### RRP Mode #####

    rrp_runtime = corosync_runtime("totem.rrp_mode ")
    rrp = corosync("rrp_mode")
    rrp_table = PrettyTable()
    if (len(rrp) == len(rrp_runtime)):
        if (typeos != str("rhel8")):
            print("\n\t***** Validating Redundant Ring Protocol *****\n")
            z = 0
            for z in range(z, len(rrp)):
                if z == 0:
                    rrp_table.field_names = ["Cluster Node", "Corosync.conf Entry", "Runtime Value"]
                rrp_table.add_row([str(u[int(z)]), str(rrp[int(z)]), str(rrp_runtime[int(z)])])
                if z == 0:
                    print(rrp_table)
                if z != 0:
                    print("\n".join(rrp_table.get_string().splitlines()[-2:]))
        elif (typeos == str("rhel8")) & ((len(set(rrp_runtime)) == 1) or (len(set(rrp)) == 1)) & ((rrp[0] != ' - ') or (rrp_runtime[0] != ' - ')):
            print("\n\033[1;31m {}\033[00m".format("ALERT:") + " This is a RHEL 8 cluster setup with redundant rings and has `rrp_mode` configured. RRP is not supported in RHEL 8 - it is replaced by the knet. KCS: https://access.redhat.com/articles/3068841 for more information).\n")
    else:
        print("\n Seems to be some issue, please validate the RRP values manually and report this issue. Thank you & Sorry!")

    tag_rrp = 0
    if len(set(rrp)) == 1:
        if ((rrp[0] != str("rhel6")) & (typeos != str("rhel8"))):
            if re.search("active", rrp[0]):
                support_rrp = "No"
                tag_rrp = "True"
                print("\033[1;31m {}\033[00m".format("ALERT:") + " Cluster is configured with RRP Mode set as 'active'. Please note this configuration for RRP is unsupported (Refer KCS: https://access.redhat.com/articles/3068841 for more information).\n")
            elif re.search("passive", rrp[0]):
                support_rrp = "Yes"
                tag_rrp = "True"
                # print(" - Current RRP mode of cluster is 'passive'.\n")
            else:
                support_rrp = "Yes"
                tag_rrp = "False"
                # print(" - No RRP configuration.\n")
        elif (typeos == "rhel8"):
            if (str(rrp[0]) == " - ") & (len(final_ip) > actualnode):
                support_rrp = "Yes"
                tag_rrp = "True"
                # print(" - This RHEL 8 cluster has redundant rings configured.\n")
            elif (str(rrp[0]) != " - ") & (len(final_ip) > actualnode):
                support_rrp = "No"
                tag_rrp = "True"
                # print("\033[1;31m {}\033[00m".format("ALERT:") + " RHEL8 cluster is not supported with RRP, it is replaced by the knet transport protocol. Please refer: https://access.redhat.com/articles/3068841 .\n")
            else:
                support_rrp = "Yes"
                tag_rrp = "False"
                print("\n - No redundant rings configuration.\n")            
        else:
            print(" - RHEL6 cluster do not have corosync.conf file.\n")
    elif len(set(rrp)) != 1:
        print("\033[1;31m {}\033[00m".format("ALERT:") + "Runtime value of RRP is different from value under corosync.conf file.")


    #******************************* Ends *******************************#

    ##### DLM + RRP Mode Confirmation #####

    if rgmanager != 1:
        support_dlm = "False"
        pcsconfig, newflag = clu_stats("pcs_config")
        if newflag == False:
            if re.search("controld", pcsconfig):
                print("\n\t***** DLM is configured, so is RRP mode/Multi Ring set ? *****\n")
                if re.search("controld", pcsconfig):
                    support_dlm = "True"
                if (support_dlm == "True") & (tag_rrp == "True") & (typeos != "rhel8"):
                    print("\033[1;31m {}\033[00m".format("ALERT:") + " Yes, it is..!!! RRP Mode (be it 'active' or 'passive') with DLM is not supported. Please refer to following article for more details: https://access.redhat.com/articles/3068921 .\n")
                elif (support_dlm == "True") & (tag_rrp == "True") & (typeos == "rhel8"):
                    print("\033[1;31m {}\033[00m".format("ALERT:") + " Yes, it is..!!! RRP Mode in RHEL8 cluster is not supported. Please refer: https://access.redhat.com/articles/3068841 .\n" )
                    # TO-DO: Need to check for multiple ring in RHEL8 setup as multiple ring in DLM is not supported.
                else:
                    print(" - No RRP configuration alongside DLM, so all good.\n")
        elif (newflag == True) or (newflag == "nofile"):
            for z in range(z, int(node)):
                if (cib_exists == 1) or (nocib == 0):
                    quorum = xml.dom.minidom.parse(cib)
                    group = quorum.getElementsByTagName("primitive")
                    for i in group:
                        if i.getAttribute("type") == "controld":
                            print("\n\t***** DLM is configured, so is RRP mode set ? *****\n")
                            support_dlm = "True"
                            if tag_rrp == "True":
                                if typeos == "rhel7":
                                    print("\033[1;31m {}\033[00m".format("ALERT:") + " Yes, it is..!!! RRP Mode (be it 'active' or 'passive') with DLM is not supported. Please refer to following article for more details: https://access.redhat.com/articles/3068921 .\n")
                                elif typeos == "rhel8":
                                    print("\033[1;31m {}\033[00m".format("ALERT:") + " Yes, it is..!!! RRP Mode in RHEL8 cluster is not supported. Please refer: https://access.redhat.com/articles/3068841 .\n" )
                            else:
                                print(" - No RRP configuration alongside DLM, so all good.\n")
                            break
                        continue
                break
                z = z + 1

    #******************************* Ends *******************************#

    ##### TOTEM Token timeout Configuration  #####

    if (typeos == "rhel7") or (typeos == "rhel8"):
        token_runtime = corosync_runtime("runtime.config.totem.token ")
    elif (typeos == str("rhel6")):
        token_runtime = corosync_runtime("totem.token")
    token = corosync("token")
    token_table = PrettyTable()
    if (len(token) == len(token_runtime)):
        print("\n\t***** Validating TOTEM Token timeout *****\n")
        z = 0
        for z in range(z, len(token)):
            if z == 0:
                token_table.field_names = ["Cluster Node", "Corosync.conf Entry", "Runtime Value"]
            token_table.add_row([str(u[int(z)]), str(token[int(z)]), str(token_runtime[int(z)])])
            if z == 0:
                print(token_table)
            if z != 0:
                print("\n".join(token_table.get_string().splitlines()[-2:]))
    else:
        print("\n Seems to be some issue, please validate the totem token timeout values manually and report this issue. Thank you & Sorry!")

    ##### Calculation for default totem token timeout #####

    boundary_version = 8.4
    rhrelease_version = []
    coefficient = []
    z = 0
    for z in range(z, int(node)):
        j = rhrelease[int(z)]
        j = j.split(" ")
        if typeos == "rhel8":
            j = j[5]
        else:
            j = j[6]
        rhrelease_version.append(j)
    
    coro_vers = []
    if (typeos == "rhel8"):
        z = 0
        pkg_coro = []
        pkg_corosync = []
        for z in range(z, int(node)):
            h = open(str(path[int(0)]) + "/installed-rpms", "r")
            hp = h.read()
            fl = hp.split("\n")
            pkg_coro = [n for n in fl if re.search("corosync-3.", n)]
            pkg_corosync = [ pkg_coros.split(None, 1)[0] for pkg_coros in pkg_coro ]

        for i in pkg_corosync:
            temp = i.split('corosync-3.')[1].split(".")[0]  # 'corosync-3.0.2-3.el8_1.1.x86_64' -> '0.2-3.el8_1.1.x86_64' -> '0': 0 if pck version is lesser than the updated version which starts with 'corosync-3.1.0-3.el8.x86_64'
            if temp == str(1):
                coro_vers.append('3k')

    z = 0
    for z in range(z, int(node)):
        if (typeos == "rhel7") or (typeos == "rhel8"):
            if (boundary_version > float(rhrelease_version[int(z)])) & (len(coro_vers) == 0) :
                coefficient.append(1000)
            elif (boundary_version > float(rhrelease_version[int(z)])) & (len(coro_vers) != 0) :
                coefficient.append(3000)
            elif (boundary_version < float(rhrelease_version[int(z)])) & (len(coro_vers) == 0) :
                coefficient.append(1000)
            elif (boundary_version < float(rhrelease_version[int(z)])) & (len(coro_vers) != 0) :
                coefficient.append(3000)
            elif (boundary_version == float(rhrelease_version[int(z)])) & (len(coro_vers) == 0) :
                coefficient.append(1000)
            elif (boundary_version == float(rhrelease_version[int(z)])) & (len(coro_vers) != 0) :
                coefficient.append(3000)
    
    if (typeos == "rhel7") or (typeos == "rhel8"):
        if len(set(coefficient)) == 1:
            if (len(set(token)) == 1) & (str(token[0]) == str(" - ")):
                if ((typeos == "rhel7") or (typeos == "rhel8")) & (actualnode > 2):
                    defaulttoken = int(coefficient[0]) + ((actualnode - 2)*650)
            if (len(set(token)) == 1) & (str(token[0]) != str(" - ") ):
                if ((typeos == "rhel7") or (typeos == "rhel8")) & (actualnode > 2):
                    increasedtoken = int(token[0]) + ((actualnode - 2)*650)
            if (len(set(token)) == 1) & (len(set(token_runtime)) == 1) & (actualnode > 2) & (token_runtime[0] != "Cluster Stopped") & (token_runtime[0] != "no-corosync-cmapctl-file"):
                if (str(token[0]) == str(" - ")) & (int(token_runtime[0]) > int(coefficient[0])):
                    if (int(token_runtime[0]) == defaulttoken):
                        print("\n - This is a " + str(actualnode) + " node setup, so the runtime totem token timeout & timeout as per corosync.conf file is correct.\n")
                    if (int(token_runtime[0]) != defaulttoken):
                        print("\n\033[1;31m {}\033[00m".format("ALERT:") + " Runtime totem token timeout is different from the configured value in corosync.conf file.\n")
                elif (str(token[0]) != str(" - ")):
                    if (int(token_runtime[0]) > int(token[0])) & (int(token_runtime[0]) == increasedtoken):
                        print("\n - This is a " + str(actualnode) + " node setup with increased token timeout of " + str(token[0]) + "ms in corosync.conf, so the runtime totem token timeout & timeout as per corosync.conf file is correct.\n")        
                    if (int(token_runtime[0]) > int(token[0])) & (int(token_runtime[0]) != increasedtoken):
                        print("\n\033[1;31m {}\033[00m".format("ALERT:") + " Runtime totem token timeout is different from the configured value in corosync.conf file.\n")
            if (len(set(token)) == 1) & (len(set(token_runtime)) == 1) & (actualnode == 2) & (token_runtime[0] != "Cluster Stopped") & (token_runtime[0] != "no-corosync-cmapctl-file"):
                if ((str(token[0]) == str(" - ")) & (int(token_runtime[0]) != int(coefficient[0]))) or ((str(token[0]) != str(" - ")) & (int(token_runtime[0]) == int(coefficient[0]))):
                    print("\n\033[1;31m {}\033[00m".format("ALERT:") + " Runtime totem token timeout is different from the configured value in corosync.conf file.\n")
        else:
            print("\033[1;33m {}\033[00m".format("WARNING:") + " Due to mismatch of OS release, default totem token cannot be calculated. The default for RHEL 8.4 and above is 3sec else 1sec.")

    #******************************* Ends *******************************#

    #### Validating the transport mode used in cluster ####

    if (typeos == "rhel7") or (typeos == "rhel8"):
        transport_runtime = corosync_runtime("totem.transport ")
    elif (typeos == str("rhel6")):
        transport_runtime = corosync_runtime("totem.transport")
    transport = corosync("transport")
    transport_table = PrettyTable()
    if (len(transport) == len(transport_runtime)):
        print("\n\t***** Validating Transport Protocol *****\n")
        z = 0
        for z in range(z, len(transport)):
            if z == 0:
                transport_table.field_names = ["Cluster Node", "Corosync.conf Entry", "Runtime Value"]
            transport_table.add_row([str(u[int(z)]), str(transport[int(z)]), str(transport_runtime[int(z)])])
            if z == 0:
                print(transport_table)
            if z != 0:
                print("\n".join(transport_table.get_string().splitlines()[-2:]))
    else:
        print("\n Seems to be some issue, please validate the transport protocol values manually and report this issue. Thank you & Sorry!")

    #******************************* Ends *******************************#

    #### Validating the corosync.conf file being consitent across all the nodes ####

    if typeos == str("rhel7") or (typeos == "rhel8"):
        consistent = corosync_conf_file_consistency()
        if consistent is False:
            print("\n\033[1;31m {}\033[00m".format("ALERT:") + " Corosync.conf file is not consistent across all the cluster nodes. Please sync the file which may require a full cluster restart.")

    #******************************* Ends *******************************#

    #### Checking the quorum device configuration ####

    qdevice_algorithm = corosync("algorithm")
    qdevice_host = corosync("host")
    qdevice_model = corosync("model")
    if (len(set(qdevice_algorithm)) == 1) & (len(set(qdevice_host)) == 1) & (len(set(qdevice_model)) == 1):
        if (qdevice_algorithm[0] != " - ") & (qdevice_host[0] != " - ") & (qdevice_model[0] != " - "):
            print("\n\t***** Validating Quorum Device Configuration *****\n")
            print(" - Qdevice Model    : %s"%qdevice_model[0])
            print(" - Qdevice Algorithm : %s"%qdevice_algorithm[0])
            print(" - Qdevice Host     : %s"%qdevice_host[0])
    else:
        print("\n\033[1;33m {}\033[00m".format("WARNING:") + " Quorum device configuration under corosync.conf file is not matching across all the cluster nodes.")

    #******************************* Ends *******************************#

    #### Checking if Cluster has GFS2 filesystem configured ####

    gfs2 = 0
    gfs2_resource = 0
    gfs2_fstab = 0
    if (rgmanager != 1) & (nocib == 0):
        filesys = xml.dom.minidom.parse(cib)
        group = filesys.getElementsByTagName("nvpair")
        for i in group:
            if i.getAttribute("name") == "fstype":
                fstype = str(i.getAttribute("value"))
                if fstype == "gfs2":
                    gfs2 = 1
                    gfs2_resource = 1
                    break
        z = 0
        for z in range(z, int(node)):
            loc = os.path.exists(str(path[int(z)]) + "/etc/fstab")
            if loc:
                with open(str(path[int(z)]) + "/etc/fstab", "r") as ifile:
                    temp = ifile.readlines()
                    for line in temp:
                        if re.search("gfs2", line):
                            gfs = line.startswith("#")
                            if gfs == False:
                                gfs2 = 1
                                gfs2_fstab = 1
                            break
    elif rgmanager == 1:
        filesys = corosync("fstype")
        filesystem = []
        if len(filesys) != 0:
            i = 0
            for i in range(i, len(filesys)):
                filesystem.append(filesys[int(i)].split('"')[0])
            i = 0
            for i in range(i, len(filesystem)):
                if filesystem[int(i)] == 'gfs2':
                    gfs2 = 1
                    gfs2_resource = 1
        z = 0
        for z in range(z, int(node)):
            loc = os.path.exists(str(path[int(z)]) + "/etc/fstab")
            if loc:
                with open(str(path[int(0)]) + "/etc/fstab", "r") as ifile:
                    temp = ifile.readlines()
                    for line in temp:
                        if re.search("gfs2", line):
                            gfs = line.startswith("#")
                            if gfs == False:
                                gfs2 = 1
                                gfs2_fstab = 1
                            break

    if gfs2 == 1:
        print("\n\t***** GFS2 related details *****\n")
        if (gfs2_fstab == 1) & (gfs2_resource == 1):
            print("\n\033[1;33m {}\033[00m".format("WARNING:") + " GFS2 filesystem is managed using Filesystem resource as well as entry in '/etc/fstab' file. Ensure that the same filesystem is not managed using both ways (manual check required). Refer KCS: https://access.redhat.com/articles/3244841 .\n")

        if (actualnode > 2) & (transport[0] == "udpu") & (gfs2 == 1) & (typeos != "rhel8"):
            print("\n - This cluster environment has " + str(actualnode) + " nodes with GFS2 filesystem configured. It is highly recommended to switch the protocol to multicast 'udp'. Refer KCS articles: https://access.redhat.com/solutions/162193 and https://access.redhat.com/articles/22304 .")

        if (actualnode == 2) & (gfs2 == 1):
            print("\n - This two node cluster has GFS2 filesystem configured.\n")

        if (gfs2 == 1):
            if re.search('VMware|RHEV|KVM', hardware):
                if len(set(token)) == 1:
                    if (str(token[0]) != " - ") & (typeos == str("rhel7") or typeos == str("rhel8")):
                        if int(token[0]) > 15000:
                            print("\033[1;33m {}\033[00m".format("WARNING:") + " The environment is susceptible to clvmd start operation time out with dlm socket error. Consider reducing the totem token timeout value or increasing the boot time. Please refer `Workaround` section of KCS article: https://access.redhat.com/solutions/3667531 .\n")

    #******************************* Ends *******************************#

    #### Validating if any GFS2 filesystem is withdrawn ####

    z = 0
    gfs2_withdrawn_locktable = []
    for withdraw in glob.iglob(str(path[int(z)]) + '/sys/fs/gfs2/'):
        i = -1
        for root, dirs, files in os.walk(withdraw):
            if z == 0:
                locktable = dirs
                z = 1
            if 'withdraw' in files:
                gfs_withdraw = os.path.join(root, 'withdraw')
                with open(gfs_withdraw, "r") as ifile:
                    for line in ifile:
                        if re.search("1", line):
                            gfs2_withdrawn_locktable.append(locktable[i])
            i = i + 1

    if len(gfs2_withdrawn_locktable) != 0:
        z = 0
        mount_dict = {}
        for z in range(z, int(node)):
            loc = os.path.exists(str(path[int(z)]) + "/sos_commands/filesys/mount_-l")
            if loc:
                with open((str(path[int(z)]) + "/sos_commands/filesys/mount_-l"), "r") as ifile:
                    for line in ifile:
                        for ele in gfs2_withdrawn_locktable:
                            if ele in line:
                                mount_dict.update({ele: [line.split(" on ")[0],line.split(" on ")[1].split(" type ")[0]]})

        print("\n\t***** Validating for any GFS2 filesystem in withdrawn state *****\n")
        for key, value in zip(mount_dict, mount_dict.values()):
            print(" - GFS2 filesystem '%s' mounted at '%s' with locktable '%s' has been withdrawn."%(value[0],value[1],key))

        print("\n - Perform fsck of GFS2 filesystem in a scheduled downtime window referring to steps in KCS: https://access.redhat.com/solutions/332223.")

    #******************************* Ends *******************************#

    #### Validating the number of cluster nodes falling within the support range ####

    if (typeos == str("rhel7")) or (typeos == "rhel8"):
        if (actualnode > 16) & (actualnode < 33):   # This will consider till 32 & exclude 33.
            if (support_dlm == "False"):
                print("\033[1;33m {}\033[00m".format("WARNING:") + " The number of cluster nodes is greater than 16. Please check for the RHEL version.")
            elif (support_dlm == "True"):
                print("\033[1;31m {}\033[00m".format("ALERT:") + " The number of cluster nodes is greater than 16 with cluster utilizing dlm. The maximum supported number of nodes is 16. Please refer: https://access.redhat.com/solutions/4346851 .\n")

            rh = open(str(path[int(0)]) + "etc/redhat-release")
            rhos = rh.read()
            print("By the way, RHEL version is: " + str(rhos).strip() + ". Refer support policy article: https://access.redhat.com/articles/3069031 .")
            rh.close
        elif (actualnode >= 33):
            print("\033[1;31m {}\033[00m".format("ALERT:") + " The cluster nodes count is greater than the supported limit. Refer support policy article: https://access.redhat.com/articles/3069031 .")

    #******************************* Ends *******************************#      


    ##### Check for Quorum policy & Resource defaults #####

    if (rgmanager != 1):
        print("\n\t***** Checking Quorum policy & Resource defaults *****\n")

        pcsproperty, newflag = (clu_stats("pcs_property_list_--all"))
        qpolicy = 0
        if newflag == False:
            if re.search("no-quorum-policy: stop", pcsproperty):
                quorum_policy = "stop"
                qpolicy = 1
            elif re.search("no-quorum-policy: freeze", pcsproperty):
                quorum_policy = "freeze"
                qpolicy = 1
            elif re.search("no-quorum-policy: ignore", pcsproperty):
                quorum_policy = "ignore"
                qpolicy = 1
            elif re.search("no-quorum-policy: suicide", pcsproperty):
                quorum_policy = "suicide"
                qpolicy = 1
        elif (newflag == True) or (newflag == "nofile"):
            if (cib_exists == 1) or (nocib == 0):
                quorum = xml.dom.minidom.parse(cib)
                group = quorum.getElementsByTagName("nvpair")
                for i in group:
                    if i.getAttribute("name") == "no-quorum-policy":
                        quorum_policy = str(i.getAttribute("value"))
                        qpolicy = 1
                        break
                    else:
                        quorum_policy = "stop"
                        qpolicy = 1

        if qpolicy == 1:
            if (quorum_policy == "stop") & (support_dlm == "True"):
                print("\033[1;33m {}\033[00m".format("WARNING:") + " The 'no-quorum-policy' needs to be updated from 'stop' to 'freeze' as you are using DLM controld. The command to update the same: 'pcs property set no-quorum-policy=freeze'.\n")
                
            elif (quorum_policy == "stop") & (support_dlm == "False"):
                print(" - Quorum policy rightly configured as 'stop'.\n")

            elif (quorum_policy == "suicide"):
                print(" - Quorum policy is configured as 'suicide'.\n")

            elif (quorum_policy == "freeze") & (support_dlm == "True"):
                print(" - Quorum policy rightly configured as 'freeze'.\n")
                
            elif (quorum_policy == "freeze") & (support_dlm == "False"):
                print("\033[1;33m {}\033[00m".format("WARNING:") + " Since there is no DLM controld resource configured, you should use 'no-quorum-policy' value from 'freeze' to 'stop'. The command to update the same: 'pcs property set no-quorum-policy=stop'.\n")
                
            elif quorum_policy == "ignore":
                print("\033[1;31m {}\033[00m".format("ALERT:") + " Quorum policy 'ignore' is not supported. Refer KCS: https://access.redhat.com/solutions/645843 .\n")
        
        elif qpolicy == 0:
            print("\033[1;33m {}\033[00m".format("WARNING:") + " Sosreport does not have a file captured via which quorum policy can be determined.\n")

        if (cib_exists == 1) or (nocib == 0):
            resource_stick = 0
            migration_threshold = 0
            doc = xml.dom.minidom.parse(cib)
            group = doc.getElementsByTagName("nvpair")
            for i in group:
                if (i.getAttribute("name") == "resource-stickiness"):
                    resource_stick = i.getAttribute("value")
                if (i.getAttribute("name") == "migration-threshold"):
                    migration_threshold = i.getAttribute("value")

            if (resource_stick != 0):
                print(" - Resource stickiness value = " + str(resource_stick))
            if (migration_threshold !=0):
                print(" - Migration threshold value = " + str(migration_threshold))

    #******************************* Ends *******************************#

    #### Checking if Cluster has LVM resource configured ####

    nfs = 0
    glusterfs = 0
    drbd = 0
    lvm_res_name = []
    filesystem_res_name = []
    if (rgmanager != 1) & (nocib == 0):
        filesys = xml.dom.minidom.parse(cib)
        group = filesys.getElementsByTagName("primitive")
        for i in group:
            if (i.getAttribute("type") == "LVM") or (i.getAttribute("type") == "LVM-activate"):
                halvm = 1
                lvm_res_name.append(str(i.getAttribute("id")))
            if i.getAttribute("type") == "Filesystem":
                hafs = 1
                filesystem_res_name.append(str(i.getAttribute("id")))
        
        if hafs == 1:
            filesys = xml.dom.minidom.parse(cib)
            group = filesys.getElementsByTagName("nvpair")
            for i in group:
                if i.getAttribute("name") == "fstype":
                    fstype = str(i.getAttribute("value"))
                    if fstype.find("nfs") != -1:
                        nfs = 1
                        # break
                    if fstype.find("glusterfs") != -1:
                        glusterfs = 1
                        # break
                if i.getAttribute("name") == "device":
                    dev = str(i.getAttribute("value"))
                    if dev.find("drbd") != -1:
                        drbd = 1

    #******************************* Ends *******************************#

    #### Check if every Filesystem resource has its corresponding LVM resource configured ####

    fs_device = []
    fstype_value = []
    vgname = []
    position = []
    attr = ["volgrpname", "vgname"]
    mt_point_cluster = []
    res_name = []
    fs_cib_group = []
    if (rgmanager != 1) & (nocib == 0):
        filesys = xml.dom.minidom.parse(cib)
        group = filesys.getElementsByTagName("nvpair")
        for i in group:
            if i.getAttribute("name") == "fstype":
                fstype_value.append(i.getAttribute("value"))
                
            if i.getAttribute("name") == "device":
                fs_device.append(i.getAttribute("value"))

            if i.getAttribute("name") == "vgname":
                vgname.append(i.getAttribute("value"))
                
            if i.getAttribute("name") == "volgrpname":
                vgname.append(i.getAttribute("value"))

        group = filesys.getElementsByTagName("primitive")
        for i in group:
            if i.getAttribute("type") == "Filesystem":
                res_name.append(i.getAttribute("id"))
        
        group = filesys.getElementsByTagName("nvpair")
        for j in res_name:
            for i in group:
                if (j+"-instance_attributes-directory").find(i.getAttribute("id")) != -1:
                    fs_cib_group.append(i)

        for i in fs_cib_group:
            if i.getAttribute("name") == "directory":
                mt_point_cluster.append(i.getAttribute("value"))

        z = 0
        if typeos == str("rhel7"):
            for i in fstype_value:
                if (i.find("nfs") != -1) or (i.find("gfs") != -1) or (i.find("glusterfs") != -1):
                    position.append(z)
                z = z + 1
        elif typeos == str("rhel8"):
            for i in fstype_value:
                if (i.find("nfs") != -1) or (i.find("glusterfs") != -1):  # excluding gfs2 as in RHEL 8 we have its corresponding LVM-activate cloned resource
                    position.append(z)
                z = z + 1            

        unwanted_fs_resources = []
        for i in position:
            unwanted_fs_resources.append(filesystem_res_name[i])
        filesystem_res_name = [ele for ele in filesystem_res_name if ele not in unwanted_fs_resources]

        unwanted_fs_device = []
        for i in position:
            unwanted_fs_device.append(fs_device[i])
        fs_device = [ele for ele in fs_device if ele not in unwanted_fs_device]

        for index, line in enumerate(fs_device):
            if "--" in line:
                fs_device[index] = line.replace("--", "-")
            else:
                fs_device[index] = line                

        configured_filesystem_res_name = []
        for i in vgname:
            z = 0
            for z in range(z, len(fs_device)):
                if fs_device[z].find(i) != -1:
                    configured_filesystem_res_name.append(filesystem_res_name[z])
        net_filesystem_resources = []
        net_filesystem_resources = [x for x in filesystem_res_name if x not in configured_filesystem_res_name]

    #******************************* Ends *******************************#

    ##### Validate for different devices mounted at same mount-point #####

    if (rgmanager != 1) & (nocib == 0):
        if len(set(mt_point_cluster)) != len(mt_point_cluster):
            multimount = [i for i in mt_point_cluster if i in list(set(mt_point_cluster))]
            print("\033[1;33m {}\033[00m".format("WARNING:") + " Multiple Filesystem resources are managing the mount at %s mountpoint."%(list(set(multimount))))

    #******************************* Ends *******************************#

    ##### Check for entries in lvm.conf file #####

    print("\n\t**** Validating entries under lvm.conf file ****\n")
    z = 0
    for z in range(z, int(node)):
        exist = os.path.exists(str(path[int(z)]) + "/etc/lvm/lvm.conf")
        if exist:
            lvmconf = True
            print(" - Checking for node " + str(u[int(z)]) + ":")
            with open(str(path[int(z)]) + "/etc/lvm/lvm.conf", "r") as ifile:
                for line in ifile:
                    if re.search("locking_type|use_lvmetad|volume_list|filter|global_filter|system_id_source|auto_activation_volume_list|use_lvmlockd", line):
                        param = line.lstrip()
                        if (param.startswith("locking_type")):
                            param = param.strip()
                            if param == 'locking_type = 1':
                                locking_type = 1
                            elif param == 'locking_type = 3':
                                locking_type = 3
                            print(param, end='\n')
                        if (param.startswith("use_lvmetad")):
                            param = param.strip()
                            if param == 'use_lvmetad = 1':
                                use_lvmetad = 1
                            print(param, end='\n')
                        if (param.startswith("volume_list")):
                            print(param, end='')
                        if (param.startswith("filter")):
                            print(param, end='')
                        if (param.startswith("global_filter")):
                            print(param, end='')
                        if (param.startswith("system_id_source")):
                            param = param.strip()
                            if typeos == str("rhel8"):
                                print(param, end='\n')
                            # if param.find("none") == -1:
                            #     print(param, end='')
                        if (param.startswith("use_lvmlockd")):
                            param = param.strip()
                            if typeos == str("rhel8"):
                                print(param, end='\n')
                        if (param.startswith("auto_activation_volume_list")):
                            param = param.strip()
                            if typeos == str("rhel8"):
                                print(param, end='')
        else:
            lvmconf = False

        if lvmconf == False:
            print("\033[1;33m {}\033[00m".format("WARNING:") + " None of the sosreport has captured lvm.conf file.")
        print("\n")

    lvmetad_daemon = ['lvm2-lvmetad.service']
    lvmetad_socket = ['lvm2-lvmetad.socket']
    lvmetad_socket_srv = 0
    lvmetad_srv = 0
    lvmetad_daemon_status = service_is_active(lvmetad_daemon)
    lvmetad_socket_status = service_is_active(lvmetad_socket)
    if 1 in lvmetad_daemon_status:
        lvmetad_srv = 1
    if 1 in lvmetad_socket_status:
        lvmetad_socket_srv = 1

    if ((use_lvmetad == 1) or (lvmetad_srv == 1) or (lvmetad_socket_srv == 1)) & (halvm == 1):
        if typeos == str("rhel7"):
            if ((use_lvmetad == 1) & (lvmetad_srv == 1) & (lvmetad_socket_srv == 1)):
                print("\033[1;33m {}\033[00m".format("WARNING:") + " `use_lvmetad` is set to 1 in `lvm.conf` file and `lvm2-lvmetad` service & socket is active. Please disable with the steps detailed in KCS: https://access.redhat.com/solutions/2053483 .\n")
            elif ((use_lvmetad == 0) & (lvmetad_srv == 1) & (lvmetad_socket_srv == 1)):
                print("\033[1;33m {}\033[00m".format("WARNING:") + " `use_lvmetad` is set to 0 in `lvm.conf` file. However `lvm2-lvmetad` service & socket is active. Please disable with the steps detailed in KCS: https://access.redhat.com/solutions/2053483 .\n")
            elif (use_lvmetad == 0):
                if (lvmetad_srv == 1):
                    print("\033[1;33m {}\033[00m".format("WARNING:") + " `use_lvmetad` is set to 0 in `lvm.conf` file. However `lvm2-lvmetad.service` is active. Please disable with the steps detailed in KCS: https://access.redhat.com/solutions/2053483 .\n")
                elif (lvmetad_socket_srv == 1):
                    print("\033[1;33m {}\033[00m".format("WARNING:") + " `use_lvmetad` is set to 0 in `lvm.conf` file. However `lvm2-lvmetad.socket` is active. Please disable with the steps detailed in KCS: https://access.redhat.com/solutions/2053483 .\n")
        elif typeos == str("rhel8"):
            print("\033[1;33m {}\033[00m".format("WARNING:") + " lvmetad is no longer supported with RHEL8 setup. The correct steps to configure HA-LVM is detailed in KCS: https://access.redhat.com/solutions/3792761 .\n")

    if (halvm == 0) & (hafs == 1) & (gfs2 == 0) & (nfs == 0) & (glusterfs == 0) & (drbd == 0):
        if typeos == "rhel8":
            print("\033[1;31m {}\033[00m".format("ALERT:") + " LVM-activate resource is not configured, improper HA-LVM configuration. Refer KCS for correct configuration: https://access.redhat.com/solutions/3792761 .\n")
        if typeos == "rhel7":
            print("\033[1;31m {}\033[00m".format("ALERT:") + " LVM resource is not configured, improper HA-LVM configuration. Refer KCS for correct configuration: https://access.redhat.com/solutions/3067 .\n")
    if (locking_type == 1) & (gfs2 == 1):
        print("\033[1;31m {}\033[00m".format("ALERT:") + " locking_type needs to be corrected and set to 3 with re-build of initramfs: https://access.redhat.com/solutions/1958 .\n")
    if (rgmanager != 1):
        if (locking_type == 3) & (support_dlm == 'True') & (halvm == 1) & (gfs2 == 0):
            print("\033[1;33m {}\033[00m".format("WARNING:") + " HA-LVM setup is configured using CLVM which is adding an overhead to the configuration. Proper setup for HA-LVM is detailed in following KCS: https://access.redhat.com/solutions/3067 .\n")
    if (drbd == 1):
        print("The cluster has filesystem using a DRBD device. If the issue is with DRBD device, then LINBIT vendor should be first contacted. Please refer KCS: https://access.redhat.com/solutions/32085.\n")
    if (rgmanager != 1) & (nocib == 0):
        if len(net_filesystem_resources) != 0:
            print("\033[1;31m {}\033[00m".format("ALERT:") + " The following list of Filesystem resource(s) are missing their corresponding LVM/LVM-activate resources: " + str(net_filesystem_resources) + ".\n")

    #******************************* Ends *******************************#

    ##### Validate for the existing of custom script resource #####

    lsb_res = []
    if (rgmanager != 1) & (nocib == 0):
        filesys = xml.dom.minidom.parse(cib)
        group = filesys.getElementsByTagName("primitive")
        for i in group:
            if i.getAttribute("class") == "lsb":
                lsb_res.append(i.getAttribute("id"))

    if len(lsb_res) != 0:
        print(" - The cluster is configured with a custom script resource. Ensure that the custom script is LSB compliant. Refer KCS: https://access.redhat.com/solutions/753443 \n")

    #******************************* Ends *******************************#

    ##### Validate if nfs-server.service is enabled at boot if cluster manages NFS #####

    nfs_res = []
    if (rgmanager != 1) & (nocib == 0):
        filesys = xml.dom.minidom.parse(cib)
        group = filesys.getElementsByTagName("primitive")
        for i in group:
            if i.getAttribute("type") == "nfsserver":
                nfs_res.append(i.getAttribute("id"))

    nfs_enabled_nodes = []
    nfsd = service_at_boot(['nfs-server.service'])
    for index, line in enumerate(nfsd):
        if line == 1:
            nfs_enabled_nodes.append(str(u[int(index)]))
    if nfs_enabled_nodes and (len(nfs_res) != 0):
        print("\033[1;31m {}\033[00m".format("ALERT:") + " The cluster node " + str(nfs_enabled_nodes) + " has nfs-server.service enabled at boot while cluster is managing nfs-daemon via resource " + str(nfs_res) + ". Disable the nfs-server.service at boot.\n")

    #******************************* Ends *******************************#

    ##### Validate if LVM-activate or lvmlockd is configured in RHEL 7 #####

    if (rgmanager != 1) & (nocib == 0) & (typeos == str("rhel7")):
        lvm_activate = 0
        lvmlockd = 0
        filesys = xml.dom.minidom.parse(cib)
        group = filesys.getElementsByTagName("primitive")
        for i in group:
            if i.getAttribute("type") == "LVM-activate":
                lvm_activate = 1
            if i.getAttribute("type") == "lvmlockd":
                lvmlockd = 1
        if (lvm_activate == 1) or (lvmlockd == 1):
            print("\033[1;33m {}\033[00m".format("WARNING:") + " Cluster is configured with 'LVM-activate/lvmlockd' resource agent which is a Tech-Preview in RHEL 7. To migrate on LVM resource agent, please refer KCS: https://access.redhat.com/solutions/6211831\n")

    #******************************* Ends *******************************#

    ##### Validate if NFS filesystem is loopback mounted #####

    if (rgmanager != 1) & (nocib == 0):
        filesys = xml.dom.minidom.parse(cib)
        res_type = filesys.getElementsByTagName("primitive")
        res_value = filesys.getElementsByTagName("nvpair")
        loopback_nfs = 0
        dev_all = []
        ip_value = []
        fs_all = []
        fs_id = []
        ip_id = []
        for i in res_type:
            if i.getAttribute("type") == "IPaddr2":
                ip_id.append(i.getAttribute("id"))
            if i.getAttribute("type") == "Filesystem":
                fs_id.append(i.getAttribute("id"))

        for i in res_value:
            if i.getAttribute("name") == "ip":
                ip_value.append(i.getAttribute("value"))

        for i in res_value:
            if i.getAttribute("name") == "device":
                dev_all.append(i.getAttribute("value"))
            if i.getAttribute("name") == "fstype":
                fs_all.append(i.getAttribute("value"))

        dev_nfs = []
        for index, line in enumerate(fs_all):
            if line == 'nfs':
                dev_nfs.append(dev_all[index])

        dev_nfs_ip = []
        for i in dev_nfs:
            dev_nfs_ip.append(i.split(":")[0])

        z = 0
        ip_in_mount = []
        for z in range(z, int(node)):
            if os.path.exists(str(path[int(z)]) + "/sos_commands/filesys/mount_-l"):
                with open(str(path[int(z)]) + "/sos_commands/filesys/mount_-l", "r") as ifile:
                    for line in ifile:
                        if re.search("type nfs ",line):
                            entry = line.split("mountaddr=")[1].split(",mountvers")[0]
                            ip_in_mount.append(entry)

        for i in ip_value:
            if i in dev_nfs_ip:
                loopback_nfs = 1
            elif i in ip_in_mount:
                loopback_nfs = 1

        if loopback_nfs == 1:
            print("\033[1;31m {}\033[00m".format("ALERT:") + " The cluster is configured with loopback mount of NFS and it is unsupported. Please refer KCS: https://access.redhat.com/articles/3290371 \n")

    #******************************* Ends *******************************#

    ##### Vaidate if Anti-Virus Software is running #####

    anti_virus = ['ma.service', 'cma.service', 'mfetpd.service', 'rtvscand.service', 'ds_agent.service', 'falcon-sensor.service', 'b9daemon.service', 'traps_pmd.service', 'lightagent.service', 'efs.service']
    anti_virus_software = ['McAfee', 'McAfee', 'McAfee', 'Symantec', 'Trend Micro', 'Falcon Sensor (CrowdStrike)', 'Carbon Black', 'Traps Endpoint Security Manager', 'Kaspersky Security for Virtualization 5.2 Light Agent', 'ESET Server Security']

    i = 0
    av_status = []
    av_final = []
    temp_av_active = service_is_active(anti_virus)  

    def split(list_a, chunk_size):
        for i in range(0, len(list_a), chunk_size):
            yield list_a[i:i + chunk_size]
    
    chunk_size = int(node)
    split_av_active = list(split(temp_av_active, chunk_size))

    i = 0
    for i in range(0, len(split_av_active)):
        if 1 in split_av_active[i]:
            av_status.append(1)
            av_final.append(str(anti_virus_software[i]))
        else:
            av_status.append(0)

    if len(av_final) != 0:
        print("\t**** Validating anti-virus status ****\n")
        print("\033[1;33m {}\033[00m".format("WARNING:") + " Cluster node running with Antivirus " + str(set(av_final)) + ".\n")
    
    z = 0
    for z in range(z, int(node)):
        y = 0
        loc = os.path.exists(str(path[int(z)]) + "/sos_commands/systemd/systemctl_status_--all")
        if loc:
            i = 0
            for i in range(i, len(av_status)):
                if av_status[i] == 1:
                    with open(str(path[int(z)]) + "/sos_commands/systemd/systemctl_status_--all", "r") as ifile:
                        lines = ifile.readlines()
                        for index, line in enumerate(lines):
                            if line.startswith('* ' + anti_virus[i]):
                                if y == 0:
                                    print(" - Service status for node " + str(u[int(z)]) + ":")
                                    y = 1
                                x = 0
                                for x in range(x, 4):
                                    if x == 0:
                                        print("\033[1;32m {}\033[00m".format("---"))
                                    print(lines[index+x].strip('\n'))
                                    if x == 3:
                                        print("\033[1;32m {}\033[00m".format("---\n"))

    #******************************* Ends *******************************#

    ##### Resource Display #####

    res_display = input("Do you wish to see the cluster resource(s) configuration? (y/n Default:n): ").lower() or "n"
    if res_display == "y" or res_display == "yes":
        if (rgmanager != 1) & (nocib == 0):
            x = PrettyTable(["Resource Name", "Type", "Parameter", "Value"])
            x.align["Value"] = "l"
            mycib = ET.parse(cib)
            myroot = mycib.getroot()
            resource_stnd = myroot[0].findall('resources/primitive')
            resource_stnd_0 = myroot[0].findall('resources/primitive/instance_attributes/nvpair')
            resource_grp = myroot[0].findall('resources/group/primitive')
            resource_grp_0 = myroot[0].findall('resources/group/primitive/instance_attributes/nvpair')
            resource_clone = myroot[0].findall('resources/clone/primitive')
            resource_clone_0 = myroot[0].findall('resources/clone/*/nvpair')
            resource_clone_1 = myroot[0].findall('resources/clone/*/*/nvpair')
            resource_mstr = myroot[0].findall('resources/master/primitive')
            resource_mstr_0 = myroot[0].findall('resources/master/primitive/*/nvpair')
            resource_mstr_1 = myroot[0].findall('resources/master/meta_attributes/nvpair')

            ## This section is for Standalone Resources ##

            for item in resource_stnd:
                for key, value in item.items():
                    if key == 'id' :
                        # print(item.attrib['id'])
                        # print(item.attrib['type'])
                        ids = item.attrib['id']
                        types = item.attrib['type']
                        id1 = 0 # This variable is to print only once the resource name
                        for item0 in resource_stnd_0:
                            if re.search(value, item0.attrib[key]):
                                # print(item0.attrib['name'])
                                # print(item0.attrib['value'])
                                names = item0.attrib['name']
                                values = item0.attrib['value']
                                if id1 == 0:
                                    x.add_row([" ", " ", " ", " "])
                                    x.add_row([ids, types, names, values])
                                    id1 = 1
                                else:
                                    x.add_row([" ", " ", names, values])
                        # print("\n")
                        break

            x.add_row([" ", " ", " ", " "])  ## This is added to make a space

            ## This section is for Master/Slave Resources ##

            for item in resource_mstr:
                for key, value in item.items():
                    if key == 'id' :
                        # print(item.attrib['id'])
                        # print(item.attrib['type'])                
                        ids = item.attrib['id']
                        types = item.attrib['type']
                        id1 = 0 # This variable is to print only once the resource name
                        for item0 in resource_mstr_0:
                            if re.search(value, item0.attrib[key]):
                                # print(item0.attrib['name'])
                                # print(item0.attrib['value'])
                                names = item0.attrib['name']
                                values = item0.attrib['value']
                                if id1 == 0:
                                    x.add_row([" ", " ", " ", " "])
                                    types = item.attrib['type'] + ' (Instance Attributes)'
                                    x.add_row([ids, types, names, values])
                                    id1 = 1
                                else:
                                    x.add_row([" ", " ", names, values])
                        id1 = 0 # This variable is to print only once the resource name
                        for item1 in resource_mstr_1:
                            if re.search(value, item1.attrib[key]):
                                # print(item1.attrib['name'])
                                # print(item1.attrib['value'])
                                names = item1.attrib['name']
                                values = item1.attrib['value']
                                if id1 == 0:
                                    x.add_row([" ", " ", " ", " "])
                                    types = item.attrib['type'] + ' (Meta Attributes)'
                                    x.add_row([ids, types, names, values])
                                    id1 = 1
                                else:
                                    x.add_row([" ", " ", names, values])

            x.add_row([" ", " ", " ", " "])  ## This is added to make a space

            ## This section is for the resources within a Group ##

            for item in resource_grp:
                for key, value in item.items():
                    if key == 'id' :
                        # print(item.attrib['id'])
                        # print(item.attrib['type'])
                        ids = item.attrib['id']
                        types = item.attrib['type']
                        id1 = 0 # This variable is to print only once the resource name
                        for item0 in resource_grp_0:
                            if re.search(value, item0.attrib[key]):
                                # print(item0.attrib['name'])
                                # print(item0.attrib['value'])
                                names = item0.attrib['name']
                                values = item0.attrib['value']
                                if id1 == 0:
                                    x.add_row([" ", " ", " ", " "])
                                    x.add_row([ids, types, names, values])
                                    id1 = 1
                                else:
                                    x.add_row([" ", " ", names, values])
                        break

            x.add_row([" ", " ", " ", " "])  ## This is added to make a space

            ## This section is for the Cloned Resources ##

            for item in resource_clone:
                for key, value in item.items():
                    if key == 'id' :
                        # print(item.attrib['id'])
                        # print(item.attrib['type'])
                        ids = item.attrib['id'] + "-clone"
                        types = item.attrib['type']
                        id1 = 0 # This variable is to print only once the resource name
                        for item0 in resource_clone_0:
                            if re.search(value, item0.attrib[key]):
                                # print(item0.attrib['name'])
                                # print(item0.attrib['value'])
                                names = item0.attrib['name']
                                values = item0.attrib['value']
                                if id1 == 0:
                                    x.add_row([" ", " ", " ", " "])
                                    x.add_row([ids, types, names, values])
                                    id1 = 1
                                else:
                                    x.add_row([" ", " ", names, values])                        
                        for item1 in resource_clone_1:
                            if re.search(value, item1.attrib[key]):
                                # print(item1.attrib['name'])
                                # print(item1.attrib['value'])
                                names = item1.attrib['name']
                                values = item1.attrib['value']
                                if id1 == 0:
                                    x.add_row([" ", " ", " ", " "])
                                    x.add_row([ids, types, names, values])
                                    id1 = 1
                                else:
                                    x.add_row([" ", " ", names, values])

            print(x)
        elif (rgmanager == 1):
            print("This is RHEL6 rgmanager cluster. Script can get details from pacemaker cluster only.")
        elif (nocib == 1):
            print("Sosreport did not captured cib.xml file which is necessary for resource configuration display.")
    else:
        print("Exiting.")

    #******************************* Ends *******************************#

if __name__ == "__main__":
    try:
        parseargs_ns = __get_args()
        if parseargs_ns == None:
            proceed = samecluster()
            if proceed == "Same":
                main()
            elif proceed == True:
                print("\n\tThere is no cluster configuration file. Is it a RHEL Cluster..?? I don't think so. ¯\_(ツ)_/¯ \n")
            elif proceed == "NotAll":
                print(" - Most probably the earlier one is a standalone system.\n")
                proceed = samecluster()
                if proceed == "Same":
                    main()
            elif proceed == "powerkill":
                exit()
            else:
                print("\n\t\033[1;31m {}\033[00m".format("ALERT:") + " Sosreport are from different clusters.\n")
                different_cluster = 1
                for i in final_sosreport:
                    print("\tSosreport " + i + " belongs to cluster_name: " + final_sosreport[i])
                print("\n\tNow select the sosreport wisely... \n")
                path = []
                vers = []
                uname = []
                v = []
                u = []
                hostDiff = []
                hostSame = []
                location = []
                kern = []
                node = 0
                actualnode = 0
                fence = []
                stonithenabled = 1
                fencedevices = []
                myCmd1 = 'ls -lrt'
                basedir = '/cases/'
                rgmanager = 0
                supported = 0
                clusternames = []
                clusternodes = []
                notclusternodes = []
                newpath = []
                nocib = 0
                final_sosreport = {}
                comp_late = []
                close = 0
                halvm = 0
                clulvm = 0
                use_lvmetad = 0
                locking_type = 0
                hafs = 0
                platform_fence_compatible = 1

                proceed = samecluster()
                if proceed == "Same":
                    main()
    except KeyboardInterrupt:
        print("\nThis script will exit since control-c was executed by end user.")
        sys.exit(1)
