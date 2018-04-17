#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Disk Image Analyzer

Call from "Analysis" mode in CCA Disk Image Processor
or run as separate script.

Python 3

Tim Walsh
https://bitarchivist.net
"""

import argparse
import csv
import datetime
import itertools
import logging
import math
import os
import shutil
import subprocess
import sys
import time

#import Objects.py from python dfxml tools
import Objects

def convert_size(size):
    """ Convert size to human-readable form """
    if (size == 0):
        return '0 bytes'
    size_name = ("bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size,1024)))
    p = math.pow(1024,i)
    s = round(size/p)
    s = str(s)
    s = s.replace('.0', '')
    return '%s %s' % (s,size_name[i])

def time_to_int(str_time):
    """ Convert datetime to unix integer value """
    dt = time.mktime(datetime.datetime.strptime(str_time, "%Y-%m-%dT%H:%M:%S").timetuple())
    return dt

def write_to_spreadsheet(disk_result, spreadsheet_path, exportall, LOGGER):
    """ Append info for current disk to analysis CSV """

    # open description spreadsheet
    spreadsheet = open(spreadsheet_path, 'a')
    writer = csv.writer(spreadsheet, quoting=csv.QUOTE_NONNUMERIC)

    # intialize values
    number_files = 0
    total_bytes = 0
    mtimes = []
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

            # skip unallocated if args.exportall is False
            if exportall == False:
                if obj.unalloc:
                    if obj.unalloc == 1:
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
        for date_list in mtimes, ctimes, crtimes:
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
        date_earliest_c = ""
        date_latest_c = ""
        date_earliest_cr = ""
        date_latest_cr = ""
        date_statement = ""

        if mtimes:
            date_earliest_m = min(mtimes)
            date_latest_m = max(mtimes)
        if ctimes:
            date_earliest_c = min(ctimes)
            date_latest_c = max(ctimes)
        if crtimes:
            date_earliest_cr = min(crtimes)
            date_latest_cr = max(crtimes)

        # determine which set of dates to use (logic: use set with earliest start date)
        use_ctimes = False
        use_crtimes = False

        if not date_earliest_m:
            date_earliest_m = "N/A"
            date_latest_m = "N/A"
        date_to_use = date_earliest_m # default to date modified

        if date_earliest_c:
            if date_earliest_c < date_to_use:
                date_to_use = date_earliest_c
                use_ctimes = True
        if date_earliest_cr:
            if date_earliest_cr < date_to_use:
                date_to_use = date_earliest_cr
                use_ctimes = False
                use_crtimes = True

        # store date_earliest and date_latest values based on datetype & record datetype
        date_type = 'Modified'
        if use_ctimes == True:
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
        if date_earliest[:4] == date_latest[:4]:
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
           LOGGER.error("Issue reading virus log for disk %s." % (os.path.basename(disk_result)))

        # write csv row
        writer.writerow([os.path.basename(disk_result), disk_fs, date_type, date_statement, date_earliest, date_latest, extent, virus_found, formatlist])
        LOGGER.info('Described %s successfully.' % (os.path.basename(disk_result)))

    # if error reading DFXML,LOGGER.error that to spreadsheet
    except:
        writer.writerow([os.path.basename(disk_result), 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 
            'N/A', 'N/A', 'Error reading DFXML file.'])
        LOGGER.error('DFXML file for %s not well-formed.' % (os.path.basename(disk_result)))

    spreadsheet.close()

def _make_parser():

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--exportall", help="Export all (not only allocated) with tsk_recover", action="store_true")
    parser.add_argument("-k", "--keepfiles", help="Retain exported logical files from each disk", action="store_true")
    parser.add_argument("-r", "--resforks", help="Export AppleDouble resource forks from HFS-formatted disks", action="store_true")
    parser.add_argument("--quiet", action="store_true", help="Write only errors to log")
    parser.add_argument("source", help="Path to folder containing disk images")
    parser.add_argument("destination", help="Output destination")

    return parser

def _configure_logging(args, log):
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    if args.quiet:
        level = logging.ERROR
    else:
        level = logging.INFO
    logging.basicConfig(filename=log, level=level, format=log_format)

def main():

    parser = _make_parser()
    args = parser.parse_args()

    source = os.path.abspath(args.source)
    destination = os.path.abspath(args.destination)

    # make output directories
    if not os.path.exists(destination):
        os.makedirs(destination)
    else: # delete and replace if exists
        shutil.rmtree(destination)
        os.makedirs(destination)
    diskimages_dir = os.path.join(destination, 'diskimages')
    files_dir = os.path.join(destination, 'files')
    results_dir = os.path.join(destination, 'reports')
    for new_dir in diskimages_dir, files_dir, results_dir:
        os.makedirs(new_dir)

    # open log file
    LOGGER = logging.getLogger()
    log_file = os.path.join(destination, 'diskimageanalyzer.log')
    _configure_logging(args, log_file)
        
    # make list for unanalyzed disks
    unanalyzed = []

    # process each disk image
    for file in sorted(os.listdir(source)):
        
        # record filename in log
        LOGGER.info('NEW FILE: %s' % (file))

        # determine if disk image
        if file.lower().endswith((".e01", ".000", ".001", ".raw", ".img", ".dd", ".iso")):

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
                   LOGGER.error('Disk image %s could not be converted to raw image format. Skipping disk.' % (file))

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
                    fiwalk_file = os.path.abspath(os.path.join(disk_dir, 'dfxml.xml'))
                    try:
                        subprocess.check_output(['fiwalk', '-X', fiwalk_file, diskimage])
                    except subprocess.CalledProcessError as e:
                       LOGGER.error('Fiwalk could not create DFXML for disk %s. STDERR: %s' % (diskimage, e.output))

                    # carve files
                    disk_files_dir = os.path.join(files_dir, file)
                    if not os.path.exists(disk_files_dir):
                        os.makedirs(disk_files_dir)
                    # carve allocated or all files depending on option selected
                    if args.exportall == True:
                        try:
                            subprocess.check_output(['tsk_recover', '-e', diskimage, disk_files_dir])
                        except subprocess.CalledProcessError as e:
                           LOGGER.error('tsk_recover could not carve all files from disk %s. STDERR: %s' % (diskimage, e.output))
                    else:
                        try:
                            subprocess.check_output(['tsk_recover', '-a', diskimage, disk_files_dir])
                        except subprocess.CalledProcessError as e:
                           LOGGER.error('tsk_recover could not carve allocated files from disk %s. STDERR: %s' % (diskimage, e.output))

                    # rewrite last modified dates of carved files based on values in DFXML
                    for (event, obj) in Objects.iterparse(fiwalk_file):
                        
                        # only work on FileObjects
                        if not isinstance(obj, Objects.FileObject):
                            continue

                        # skip directories and links
                        if obj.name_type:
                            if obj.name_type != "r":
                                continue

                        # record filename
                        dfxml_filename = obj.filename
                        dfxml_filedate = int(time.time()) # default to current time

                        # record last modified or last created date
                        try:
                            mtime = obj.mtime
                            mtime = str(mtime)
                        except:
                            pass

                        try:
                            crtime = obj.crtime
                            crtime = str(crtime)
                        except:
                            pass

                        # fallback to created date if last modified doesn't exist
                        if mtime and (mtime != 'None'):
                            mtime = time_to_int(mtime[:19])
                            dfxml_filedate = mtime
                        elif crtime and (crtime != 'None'):
                            crtime = time_to_int(crtime[:19])
                            dfxml_filedate = crtime
                        else:
                            continue

                        # rewrite last modified date of corresponding file in objects/files
                        exported_filepath = os.path.join(disk_files_dir, dfxml_filename)
                        if os.path.isfile(exported_filepath):
                            os.utime(exported_filepath, (dfxml_filedate, dfxml_filedate))

                    # run brunnhilde
                    subprocess.call("brunnhilde.py -zwb '%s' '%s' brunnhilde" % (disk_files_dir, disk_dir), shell=True)

                    # remove disk_files_dir unless keepfiles option selected
                    if args.keepfiles == False:
                        shutil.rmtree(disk_files_dir)

                elif ('hfs' in disk_fs.lower()) and ('hfs+' not in disk_fs.lower()):
                    # mount disk image
                    subprocess.call("sudo mount -t hfs -o loop,ro,noexec '%s' /mnt/diskid/" % (diskimage), shell=True)

                    # use walk_to_dfxml.py to make dfxml
                    dfxml_file = os.path.abspath(os.path.join(disk_dir, 'dfxml.xml'))
                    try:
                        subprocess.call("cd /mnt/diskid/ && python3 /usr/share/ccatools/diskimageprocessor/walk_to_dfxml.py > '%s'" % (dfxml_file), shell=True)
                    except:
                       LOGGER.error('walk_to_dfxml.py unable to generate DFXML for disk %s' % (diskimage))
                    
                    # run brunnhilde
                    subprocess.call("brunnhilde.py -zwb /mnt/diskid/ '%s' brunnhilde" % (disk_dir), shell=True)

                    # unmount disk image
                    subprocess.call('sudo umount /mnt/diskid', shell=True)

                    # export files to disk_files_dir if keepfiles selected
                    if args.keepfiles == True:
                        disk_files_dir = os.path.join(files_dir, file)
                        if not os.path.exists(disk_files_dir):
                            os.makedirs(disk_files_dir)
                        # carve with or without resource forks depending on option selected
                        if args.resforks == True:
                            try:
                                subprocess.check_output(['bash', '/usr/share/hfsexplorer/bin/unhfs', '-v', '-resforks', 'APPLEDOUBLE', '-o', disk_files_dir, diskimage])
                            except subprocess.CalledProcessError as e:
                               LOGGER.error('HFS Explorer could not carve the following files from disk %s. Error output: %s' % (diskimage, e.output))
                        else:
                            try:
                                subprocess.check_output(['bash', '/usr/share/hfsexplorer/bin/unhfs', '-v', '-o', disk_files_dir, diskimage])
                            except subprocess.CalledProcessError as e:
                               LOGGER.error('HFS Explorer could not carve the following files from disk %s. Error output: %s' % (diskimage, e.output))


                elif 'udf' in disk_fs.lower():
                    # mount image
                    subprocess.call("sudo mount -t udf -o loop '%s' /mnt/diskid/" % (diskimage), shell=True)

                    # use walk_to_dfxml.py to create dfxml
                    dfxml_file = os.path.abspath(os.path.join(disk_dir, 'dfxml.xml'))
                    try:
                        subprocess.call("cd /mnt/diskid/ && python3 /usr/share/ccatools/diskimageprocessor/walk_to_dfxml.py > '%s'" % (dfxml_file), shell=True)
                    except:
                       LOGGER.error('walk_to_dfxml.py unable to generate DFXML for disk %s' % (diskimage))
                    
                    # write files to tempdir
                    disk_files_dir = os.path.join(files_dir, file)
                    shutil.copytree('/mnt/diskid/', disk_files_dir, symlinks=False, ignore=None)

                    # change file permissions in disk_files_dir
                    subprocess.call("find '%s' -type d -exec chmod 755 {} \;" % (disk_files_dir), shell=True)
                    subprocess.call("find '%s' -type f -exec chmod 644 {} \;" % (disk_files_dir), shell=True)

                    # unmount disk image
                    subprocess.call('sudo umount /mnt/diskid', shell=True)

                    # run brunnhilde
                    subprocess.call("brunnhilde.py -zwb '%s' '%s' brunnhilde" % (disk_files_dir, disk_dir), shell=True)
                    
                    # remove disk_files_dir unless keepfiles option selected
                    if args.keepfiles == False:
                        shutil.rmtree(disk_files_dir)
                
                else:
                    # add disk to unanalyzed list
                    LOGGER.info('Skipping processing of unknown disk type.')
                    unanalyzed.append(diskimage)    

            # no raw disk image
            else:
                LOGGER.info('No raw disk image. Skipping disk.')
                unprocessed.append(file)  

        else:
            # write skipped file to log
            LOGGER.info('File is not a disk image. Skipping file.')    

    # delete temp directories
    shutil.rmtree(diskimages_dir)
    if args.keepfiles == False:
        shutil.rmtree(files_dir)

    # create analysis csv, write header, and close file
    spreadsheet = open(os.path.join(destination, 'analysis.csv'), 'w')
    writer = csv.writer(spreadsheet, quoting=csv.QUOTE_NONNUMERIC)
    header_list = ['Disk image', 'File system', 'Date type', 'Date statement', 'Date begin', 'Date end', 'Extent', 'Virus found', 'File formats']
    writer.writerow(header_list)
    spreadsheet.close()

    # add info to analysis csv for each SIP
    for item in sorted(os.listdir(results_dir)):
        disk_result = os.path.join(results_dir, item)
        write_to_spreadsheet(disk_result, os.path.join(destination, 'analysis.csv'), args.exportall, LOGGER)

    # write closing message
    if unanalyzed:
        skipped_disks = ', '.join(unanalyzed)
        LOGGER.info('Analysis complete. Skipped disks: %s.' % (skipped_disks))
    else:
        LOGGER.info('Analysis complete. All disk images analyzed. Results in %s.' % (destination))

if __name__ == '__main__':
    main()