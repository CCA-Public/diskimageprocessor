#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Disk Image Analyzer
Called from "Analysis" mode in CCA Disk Image Processor.
Can also be run as separate script.
Python 3

Tim Walsh 2017
MIT License
"""

import argparse
import csv
import datetime
import itertools
import math
import os
import shutil
import subprocess
import sys
from time import localtime, strftime

#import Objects.py from python dfxml tools
import Objects

def convert_size(size):
    """convert size to human-readable form"""
    if (size == 0):
        return '0 bytes'
    size_name = ("bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size,1024)))
    p = math.pow(1024,i)
    s = round(size/p)
    s = str(s)
    s = s.replace('.0', '')
    return '%s %s' % (s,size_name[i])

def write_to_spreadsheet(disk_result, spreadsheet_path):
    """append info for current disk to analysis CSV"""

    # open description spreadsheet
    spreadsheet = open(spreadsheet_path, 'a')
    writer = csv.writer(spreadsheet, quoting=csv.QUOTE_NONNUMERIC)

    # intialize values
    number_files = 0
    total_bytes = 0
    mtimes = []
    atimes = []
    ctimes = []
    crtimes = []

    # parse dfxml file
    dfxml_file = os.path.join(disk_result, 'dfxml.xml')

    # try to read DFXML file
    try:
        # gather info for each FileObject
        for (event, obj) in Objects.iterparse(dfxml_file):
            
            # only work on FileObjects
            if not isinstance(obj, Objects.FileObject):
                continue

            # skip directories and links
            if obj.name_type != "r":
                continue
            
            # gather info
            number_files += 1

            try:
                mtime = obj.mtime
                mtime = str(mtime)
                mtimes.append(mtime)
            except:
                pass

            try:
                atime = obj.atime
                atime = str(atime)
                atimes.append(atime)
            except:
                pass

            try:
                ctime = obj.ctime
                ctime = str(ctime)
                ctimes.append(ctime)
            except:
                pass

            try:
                crtime = obj.crtime
                crtime = str(crtime)
                crtimes.append(crtime)
            except:
                pass

            total_bytes += obj.filesize

        # filter 'None' values from date lists
        for date_list in mtimes, atimes, ctimes, crtimes:
            while 'None' in date_list:
                date_list.remove('None')

        # build extent statement
        size_readable = convert_size(total_bytes)
        if number_files == 1:
            extent = "1 digital file (%s)" % (size_readable)
        elif number_files == 0:
            extent = "EMPTY"
        else:
            extent = "%d digital files (%s)" % (number_files, size_readable)

        # determine earliest and latest MAC dates from lists
        date_earliest_m = ""
        date_latest_m = ""
        date_earliest_a = ""
        date_latest_a = ""
        date_earliest_c = ""
        date_latest_c = ""
        date_earliest_cr = ""
        date_latest_cr = ""
        date_statement = ""

        if mtimes:
            date_earliest_m = min(mtimes)
            date_latest_m = max(mtimes)
        if atimes:
            date_earliest_a = min(atimes)
            date_latest_a = max(atimes)
        if ctimes:
            date_earliest_c = min(ctimes)
            date_latest_c = max(ctimes)
        if crtimes:
            date_earliest_cr = min(crtimes)
            date_latest_cr = max(crtimes)

        # determine which set of dates to use (logic: use set with earliest start date)
        use_atimes = False
        use_ctimes = False
        use_crtimes = False

        if not date_earliest_m:
            date_earliest_m = "N/A"
            date_latest_m = "N/A"
        date_to_use = date_earliest_m # default to date modified

        if date_earliest_a:
            if date_earliest_a < date_to_use:
                date_to_use = date_earliest_a
                use_atimes = True
        if date_earliest_c:
            if date_earliest_c < date_to_use:
                date_to_use = date_earliest_c
                use_atimes = False
                use_ctimes = True
        if date_earliest_cr:
            if date_earliest_cr < date_to_use:
                date_to_use = date_earliest_cr
                use_atimes = False
                use_ctimes = False
                use_crtimes = True

        # store date_earliest and date_latest values based on datetype & record datetype
        date_type = 'Modified'
        if use_atimes == True:
            date_earliest = date_earliest_a[:10]
            date_latest = date_latest_a[:10] 
            date_type = 'Accessed'
        elif use_ctimes == True:
            date_earliest = date_earliest_c[:10]
            date_latest = date_latest_c[:10]
            date_type = 'Created'
        elif use_crtimes == True:
            date_earliest = date_earliest_cr[:10]
            date_latest = date_latest_cr[:10]
            date_type = 'Created'
        else:
            date_earliest = date_earliest_m[:10]
            date_latest = date_latest_m[:10]

        # write date statement
        if date_earliest == date_latest:
            date_statement = '%s' % (date_earliest[:4])
        else:
            date_statement = '%s - %s' % (date_earliest[:4], date_latest[:4])

        # gather file system info, discern tool used
        disktype = os.path.join(disk_result, 'disktype.txt')
        # pull filesystem info from disktype.txt
        disk_fs = ''
        try:
            for line in open(disktype, 'r'):
                if "file system" in line:
                    disk_fs = line.strip()
        except: # handle non-Unicode chars
            for line in open(disktype, 'rb'):
                if "file system" in line.decode('utf-8','ignore'):
                    disk_fs = line.decode('utf-8','ignore').strip()

        # gather info from brunnhilde
        if extent == 'EMPTY':
            scopecontent = ''
            formatlist = ''
        else:
            fileformats = []
            formatlist = ''
            fileformat_csv = ''
            fileformat_csv = os.path.join(disk_result, 'brunnhilde', 'csv_reports', 'formats.csv')
            try: 
                with open(fileformat_csv, 'r') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        fileformats.append(row[0])
            except:
                fileformats.append("ERROR! No formats.csv file to pull formats from.")
            fileformats = [element or 'Unidentified' for element in fileformats] # replace empty elements with 'Unidentified'
            formatlist = ', '.join(fileformats) # format list of top file formats as human-readable
        
        virus_found = False
        virus_log = os.path.join(disk_result, 'brunnhilde', 'logs', 'viruscheck-log.txt')
        try:
            with open(virus_log, 'r') as virus:
                first_line = virus.readline()
                if "FOUND" in first_line:
                    virus_found = True
        except:
            print("ERROR: Issue reading virus log for disk %s." % (os.path.basename(disk_result)))

        # write csv row
        writer.writerow([os.path.basename(disk_result), disk_fs, date_type, date_statement, date_earliest, date_latest, extent, virus_found, formatlist])

    # if error reading DFXML, print that to spreadsheet
    except:
        writer.writerow([os.path.basename(disk_result), 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 
            'N/A', 'N/A', 'Error reading DFXML file.'])

    spreadsheet.close()

# MAIN FLOW

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("source", help="Path to folder containing disk images")
parser.add_argument("destination", help="Output destination")
args = parser.parse_args()

source = args.source
destination = args.destination

# make outdir disks
if not os.path.exists(destination):
    os.makedirs(destination)
diskimages_dir = os.path.join(destination, 'diskimages')
results_dir = os.path.join(destination, 'reports')
for new_dir in diskimages_dir, results_dir:
    os.makedirs(new_dir)
    
# make list for unanalyzed disks
unanalyzed = []

# process each disk image
for file in sorted(os.listdir(source)):
    
    # determine if disk image
    if file.endswith(".E01") or file.endswith(".000") or file.endswith(".raw") or file.endswith(".img") or file.endswith(".dd") or file.endswith(".iso"):

        # save info about file
        image_path = os.path.join(source, file)
        image_id = os.path.splitext(file)[0]
        image_ext = os.path.splitext(file)[1]

        # create new folders
        disk_dir = os.path.join(results_dir, file)
        os.makedirs(disk_dir)

        # disk image status
        raw_image = False

        # check if disk image is ewf
        if image_ext == ".E01":
            # convert disk image to raw and write to diskimages_dir
            raw_out = os.path.join(diskimages_dir, image_id)
            try:
                subprocess.check_output(['ewfexport', '-t', raw_out, '-f', 'raw', '-o', '0', '-S', '0', '-u', image_path])
                raw_image = True
                os.rename(os.path.join(diskimages_dir, '%s.raw' % image_id), os.path.join(diskimages_dir, '%s.img' % image_id)) # change file extension from .raw to .img
                os.rename(os.path.join(diskimages_dir, '%s.raw.info' % image_id), os.path.join(diskimages_dir, '%s.img.info' % image_id)) # rename sidecar md5 file
                diskimage = os.path.join(diskimages_dir, '%s.img' % image_id) # use raw disk image in diskimages_dir moving forward
            except subprocess.CalledProcessError:
                print('ERROR: Disk image could not be converted to raw image format. Skipping disk.')

        else:
            raw_image = True
            for movefile in os.listdir(args.source):
                # if filename starts with disk image basename (this will also capture info and log files, multi-part disk images, etc.)
                if movefile.startswith(image_id):
                    # copy file to objects/diskimage
                    shutil.copyfile(os.path.join(args.source, movefile), os.path.join(diskimages_dir, movefile))
            diskimage = os.path.join(diskimages_dir, file) # use disk image in diskimages_dir moving forward

        # raw disk image
        if raw_image == True:
            
            # run disktype on disk image, save output to disk_dir
            disktype = os.path.join(disk_dir, 'disktype.txt')
            subprocess.call("disktype '%s' > '%s'" % (diskimage, disktype), shell=True)

            # pull filesystem info from disktype.txt
            disk_fs = ''
            try:
                for line in open(disktype, 'r'):
                    if "file system" in line:
                        disk_fs = line.strip()
            except: # handle non-Unicode chars
                for line in open(disktype, 'rb'):
                    if "file system" in line.decode('utf-8','ignore'):
                        disk_fs = line.decode('utf-8','ignore').strip()

            # handle differently by file system
            if any(x in disk_fs.lower() for x in ('ntfs', 'fat', 'ext', 'iso9660', 'hfs+', 'ufs', 'raw', 'swap', 'yaffs2')):
                # use fiwalk to make dfxml
                fiwalk_file = os.path.join(disk_dir, 'dfxml.xml')
                subprocess.check_output(['fiwalk', '-X', fiwalk_file, diskimage])

                # run brunnhilde
                subprocess.call("brunnhilde.py -zwbdr '%s' '%s' brunnhilde" % (diskimage, disk_dir), shell=True)

            elif ('hfs' in disk_fs.lower()) and ('hfs+' not in disk_fs.lower()):
                # mount disk image
                subprocess.call("sudo mount -t hfs -o loop,ro,noexec '%s' /mnt/diskid/" % (diskimage), shell=True)

                # use walk_to_dfxml.py to make dfxml
                dfxml_file = os.path.abspath(os.path.join(disk_dir, 'dfxml.xml'))
                subprocess.call("cd /mnt/diskid/ && python3 /usr/share/dfxml/python/walk_to_dfxml.py > '%s'" % (dfxml_file), shell=True)
                
                # run brunnhilde
                subprocess.call("brunnhilde.py -zwb /mnt/diskid/ '%s' brunnhilde" % (disk_dir), shell=True)

                # unmount disk image
                subprocess.call('sudo umount /mnt/diskid', shell=True)

            elif 'udf' in disk_fs.lower():
                # mount image
                subprocess.call("sudo mount -t udf -o loop '%s' /mnt/diskid/" % (diskimage), shell=True)

                # use walk_to_dfxml.py to create dfxml
                dfxml_file = os.path.abspath(os.path.join(disk_dir, 'dfxml.xml'))
                subprocess.call("cd /mnt/diskid/ && python3 /usr/share/dfxml/python/walk_to_dfxml.py > '%s'" % (dfxml_file), shell=True)
                
                # write files to tempdir
                temp_dir = os.path.join(disk_dir, 'temp')
                shutil.copytree('/mnt/diskid/', temp_dir, symlinks=False, ignore=None)

                # change file permissions in temp_dir
                subprocess.call("find '%s' -type d -exec chmod 755 {} \;" % (temp_dir), shell=True)
                subprocess.call("find '%s' -type f -exec chmod 644 {} \;" % (temp_dir), shell=True)

                # unmount disk image
                subprocess.call('sudo umount /mnt/diskid', shell=True)

                # run brunnhilde
                subprocess.call("brunnhilde.py -zwb '%s' '%s' brunnhilde" % (temp_dir, disk_dir), shell=True)
                
                # delete tempdir
                shutil.rmtree(temp_dir)
            
            else:
                # add disk to unanalyzed list
                unanalyzed.append(diskimage)
                

# delete disk images
shutil.rmtree(diskimages_dir)

# create analysis spreadsheet
spreadsheet_path = os.path.join(destination, 'analysis.csv')
# open description spreadsheet
spreadsheet = open(spreadsheet_path, 'w')
writer = csv.writer(spreadsheet, quoting=csv.QUOTE_NONNUMERIC)
header_list = ['Disk image', 'File system', 'Date type', 'Date statement', 'Date begin', 'Date end', 'Extent', 'Virus found', 'File formats']
writer.writerow(header_list)

# close description spreadsheet
spreadsheet.close()

# add info to description spreadsheet
for item in sorted(os.listdir(results_dir)):
    disk_result = os.path.join(results_dir, item)
    write_to_spreadsheet(disk_result, spreadsheet_path)

# write closing message
if unanalyzed:
    skipped_disks = ', '.join(unanalyzed)
    print('Analysis complete. Skipped disks: %s.' % (skipped_disks))
else:
    print('Analysis complete. All disk images analyzed. Results in %s.' % (destination))
