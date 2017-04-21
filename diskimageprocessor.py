#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes folder of disk images (and associated files) as input, and creates
output of packaged SIPs ready for ingest into Archivematica, 
as well as a pre-populated description spreadsheet.

Will create metadata/checksum.md5 file by default. To have diskimageprocessor.py
create bagged SIPs instead, pass the "-b" or "--bagfiles" argument.

Exports only allocated files from non-HFS disks by default. To export all files,
including deleted files and file segments residing in slack space, pass the "-e"
or "--exportall" argument.

To have Brunnhilde also complete a PII scan using bulk_extractor, pass the
"-p" or "-piiscan" argument.

For processing HFS and UDF disk images, make sure /mnt/diskid/ exists prior to use.

Python 3

MIT License
(c) Tim Walsh 2016
http://bitarchivist.net
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
sys.path.append('/usr/share/dfxml/python')
import Objects

def logandprint(message):
    log.write('\n' + (strftime("%H:%M:%S %b %d, %Y - ", localtime())) + message)
    print(message)

def convert_size(size):
    # convert size to human-readable form
    if (size == 0):
        return '0 bytes'
    size_name = ("bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size,1024)))
    p = math.pow(1024,i)
    s = round(size/p)
    s = str(s)
    s = s.replace('.0', '')
    return '%s %s' % (s,size_name[i])

def create_spreadsheet(files_only):
    # process each SIP
    for item in sorted(os.listdir(sips)):
        current = os.path.join(sips, item)
        # test if entry if directory
        if os.path.isdir(current):
            
            # intialize values
            number_files = 0
            total_bytes = 0
            mtimes = []
            atimes = []
            ctimes = []
            crtimes = []

            # parse dfxml file
            if args.bagfiles == True:
                dfxml_file = os.path.abspath(os.path.join(current, 'data', 'metadata', 'submissionDocumentation', 'dfxml.xml'))
            else:
                dfxml_file = os.path.abspath(os.path.join(current, 'metadata', 'submissionDocumentation', 'dfxml.xml'))

            # gather info for each FileObject
            for (event, obj) in Objects.iterparse(dfxml_file):
                
                # only work on FileObjects
                if not isinstance(obj, Objects.FileObject):
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
                extent = "1 digital file (%s)" % size_readable
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

            # store date_earliest and date_latest values based on datetype used
            if use_atimes == True:
                date_earliest = date_earliest_a[:10]
                date_latest = date_latest_a[:10] 
            elif use_ctimes == True:
                date_earliest = date_earliest_c[:10]
                date_latest = date_latest_c[:10]
            elif use_crtimes == True:
                date_earliest = date_earliest_cr[:10]
                date_latest = date_latest_cr[:10]
            else:
                date_earliest = date_earliest_m[:10]
                date_latest = date_latest_m[:10]

            # write date statement
            if date_earliest == date_latest:
                date_statement = '%s' % date_earliest[:4]
            else:
                date_statement = '%s - %s' % (date_earliest[:4], date_latest[:4])

            # gather file system info, discern tool used
            if args.bagfiles == True:
                disktype = os.path.join(current, 'data', 'metadata', 'submissionDocumentation', 'disktype.txt')
            else:
                disktype = os.path.join(current, 'metadata', 'submissionDocumentation', 'disktype.txt')
            # pull filesystem info from disktype.txt
            disk_fs = ''
            try:
                for line in open(disktype, 'r'):
                    if "file system" in line:
                        disk_fs = line
            except: # disktype output contains non-unicode text
                for line in open(disktype, 'rb'):
                    if "file system" in line:
                        disk_fs = line

            # save tool used to carve files
            if any(x in disk_fs.lower() for x in ('ntfs', 'fat', 'ext', 'iso9660', 'hfs+', 'ufs', 'raw', 'swap', 'yaffs2')):
                tool = "using SleuthKit's tsk_recover"
            elif ('hfs' in disk_fs.lower()) and ('hfs+' not in disk_fs.lower()):
                tool = "using the HFSExplorer command line utility unhfs"
            elif ('udf' in disk_fs.lower()):
                tool = "by mounting disk image and copying files with Python's shutil.copytree function"
            else:
                tool = "UNSUCCESSFULLY"

            # gather info from brunnhilde & write scope and content note
            if extent == 'EMPTY':
                scopecontent = ''
                formatlist = ''
            else:
                fileformats = []
                formatlist = ''
                fileformat_csv = ''
                if args.bagfiles == True:
                    fileformat_csv = os.path.join(current, 'data', 'metadata', 'submissionDocumentation', 'brunnhilde', 'csv_reports', 'formats.csv')
                else:
                    fileformat_csv = os.path.join(current, 'metadata', 'submissionDocumentation', 'brunnhilde', 'csv_reports', 'formats.csv')
                try: 
                    with open(fileformat_csv, 'r') as f:
                        reader = csv.reader(f)
                        next(reader)
                        for row in itertools.islice(reader, 5):
                            fileformats.append(row[0])
                except:
                    fileformats.append("ERROR! No formats.csv file to pull formats from.")
                fileformats = [element or 'Unidentified' for element in fileformats] # replace empty elements with 'Unidentified'
                formatlist = ', '.join(fileformats) # format list of top file formats as human-readable
                
                
                # create scope and content note
                if files_only == True:
                    scopecontent = 'File includes logical files carved from a disk image %s. Most common file formats: %s' % (tool, formatlist)
                else:
                    scopecontent = 'File includes both a disk image and logical files carved from the disk image %s. Most common file formats: %s' % (tool, formatlist)

            # write csv row
            writer.writerow(['', item, '', '', date_statement, date_earliest, date_latest, 'File', extent, 
                scopecontent, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
            
            logandprint('Described %s successfully.' % current)

    logandprint('All SIPs described in spreadsheet. Process complete.')

def keep_logical_files_only(objects_dir):
    # get list of files in files dir
    files_dir = os.path.join(objects_dir, 'files')
    fileList = os.listdir(files_dir)
    fileList = [files_dir + '/' + filename for filename in fileList]

    # move files up one directory
    for f in fileList:
        shutil.move(f, objects_dir)

    # delete file and diskimage dirs
    shutil.rmtree(files_dir)
    shutil.rmtree(os.path.join(objects_dir, 'diskimage'))


# MAIN FLOW

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-b", "--bagfiles", help="Bag files instead of writing checksum.md5", action="store_true")
parser.add_argument("-e", "--exportall", help="Export all files from disk images using tsk_recover", action="store_true")
parser.add_argument("-f", "--filesonly", help="Include logical files only (not disk images) in SIPs", action="store_true")
parser.add_argument("-p", "--piiscan", help="Run bulk_extractor in Brunnhilde scan", action="store_true")
parser.add_argument("-r", "--resforks", help="Export AppleDouble resource forks from HFS-formatted disks", action="store_true")
parser.add_argument("source", help="Path to folder containing disk images")
parser.add_argument("destination", help="Output destination")
args = parser.parse_args()

destination = args.destination

# create output directories
if not os.path.exists(destination):
    os.makedirs(destination)

sips = os.path.join(destination, 'SIPs')
os.makedirs(sips)

# open log file
log_file = os.path.join(destination, 'diskimageprocessor-log.txt')
try:
    log = open(log_file, 'w')   # open the log file
    logandprint('Source of disk images: %s' % (args.source))
except:
    sys.exit('There was an error creating the log file.')

# open description spreadsheet
try:
    spreadsheet = open(os.path.join(destination,'description.csv'), 'w')
    writer = csv.writer(spreadsheet, quoting=csv.QUOTE_NONNUMERIC)
    header_list = ['Parent ID', 'Identifier', 'Title', 'Archive Creator', 'Date expression', 'Date start', 'Date end', 
        'Level of description', 'Extent and medium', 'Scope and content', 'Arrangement (optional)', 'Accession number', 
        'Appraisal, destruction, and scheduling information (optional)', 'Name access points (optional)', 
        'Geographic access points (optional)', 'Conditions governing access (optional)', 'Conditions governing reproduction (optional)', 
        'Language of material (optional)', 'Physical characteristics & technical requirements affecting use (optional)', 
        'Finding aids (optional)', 'Related units of description (optional)', 'Archival history (optional)', 
        'Immediate source of acquisition or transfer (optional)', "Archivists' note (optional)", 'General note (optional)', 
        'Description status']
    writer.writerow(header_list)
except:
    logandprint('There was an error creating the processing spreadsheet.')
    sys.exit()

# make list for unprocessed disks
unprocessed = []

# iterate through files in source directory
for file in sorted(os.listdir(args.source)):

    # record filename in log
    logandprint('>>> NEW FILE: %s' % (file))
    
    # determine if disk image
    if file.endswith(".E01") or file.endswith(".000") or file.endswith(".raw") or file.endswith(".img") or file.endswith(".dd") or file.endswith(".iso"):

        # save info about file
        image_path = os.path.join(args.source, file)
        image_id = os.path.splitext(file)[0]
        image_ext = os.path.splitext(file)[1]

        # create new folders
        sip_dir = os.path.join(sips, file)
        object_dir = os.path.join(sip_dir, 'objects')
        diskimage_dir = os.path.join(object_dir, 'diskimage')
        files_dir = os.path.join(object_dir, 'files')
        metadata_dir = os.path.join(sip_dir, 'metadata')
        subdoc_dir = os.path.join(metadata_dir, 'submissionDocumentation')

        for folder in sip_dir, object_dir, diskimage_dir, files_dir, metadata_dir, subdoc_dir:
            os.makedirs(folder)

        # disk image status
        raw_image = False

        # check if disk image is ewf
        if image_ext == ".E01":
            # convert disk image to raw and write to /objects/diskimage
            raw_out = os.path.join(diskimage_dir, image_id)
            try:
                subprocess.check_output(['ewfexport', '-t', raw_out, '-f', 'raw', '-o', '0', '-S', '0', '-u', image_path])
                raw_image = True
                os.rename(os.path.join(diskimage_dir, '%s.raw' % (image_id)), os.path.join(diskimage_dir, '%s.img' % image_id)) # change file extension from .raw to .img
                os.rename(os.path.join(diskimage_dir, '%s.raw.info' % (image_id)), os.path.join(diskimage_dir, '%s.img.info' % image_id)) # rename sidecar md5 file
                diskimage = os.path.join(diskimage_dir, '%s.img' % (image_id)) # use raw disk image in objects/diskimage moving forward
            except subprocess.CalledProcessError:
                logandprint('ERROR: Disk image could not be converted to raw image format. Skipping disk.')

        else:
            raw_image = True
            for movefile in os.listdir(args.source):
                # if filename starts with disk image basename (this will also capture info and log files, multi-part disk images, etc.)
                if movefile.startswith(image_id):
                    # copy file to objects/diskimage
                    try:
                        shutil.copyfile(os.path.join(args.source, movefile), os.path.join(diskimage_dir, movefile))
                    except:
                        logandprint('ERROR: File %s not successfully copied to %s' % (movefile, diskimage_dir))
            diskimage = os.path.join(diskimage_dir, file) # use disk image in objects/diskimage moving forward

        # raw disk image
        if raw_image == True:

            # run disktype on disk image, save output to submissionDocumentation
            disktype_txt = os.path.join(subdoc_dir, 'disktype.txt')
            subprocess.call("disktype '%s' > '%s'" % (diskimage, disktype_txt), shell=True)

            # pull filesystem info from disktype.txt
            disk_fs = ''
            try:
                for line in open(disktype, 'r'):
                    if "file system" in line:
                        disk_fs = line
            except: # disktype output contains non-unicode text
                for line in open(disktype, 'rb'):
                    if "file system" in line:
                        disk_fs = line
            logandprint('File system: %s' % (disk_fs))

            # handle differently by file system
            if any(x in disk_fs.lower() for x in ('ntfs', 'fat', 'ext', 'iso9660', 'hfs+', 'ufs', 'raw', 'swap', 'yaffs2')):
                # use fiwalk to make dfxml
                fiwalk_file = os.path.join(subdoc_dir, 'dfxml.xml')
                try:
                    subprocess.check_output(['fiwalk', '-X', fiwalk_file, diskimage])
                except subprocess.CalledProcessError as e:
                    logandprint('ERROR: Fiwalk could not create DFXML for disk. STDERR: %s' % (e.output))
                
                # carve images using tsk_recover
                if args.exportall == True: # export all files
                    try:
                        subprocess.check_output(['tsk_recover', '-e', diskimage, files_dir])
                    except subprocess.CalledProcessError as e:
                        logandprint('ERROR: tsk_recover could not carve all files from disk. STDERR: %s' % (e.output))
                else: # export only allocated files (default)
                    try:
                        subprocess.check_output(['tsk_recover', '-a', diskimage, files_dir])
                    except subprocess.CalledProcessError as e:
                        logandprint('ERROR: tsk_recover could not carve allocated files from disk. STDERR: %s' % (e.output))    

                # run brunnhilde and write to submissionDocumentation
                files_abs = os.path.abspath(files_dir)
                if args.piiscan == True: # brunnhilde with bulk_extractor
                    subprocess.call("brunnhilde.py -zbw '%s' '%s' '%s'" % (files_abs, subdoc_dir, 'brunnhilde'), shell=True)
                else: # brunnhilde without bulk_extractor
                    subprocess.call("brunnhilde.py -zw '%s' '%s' '%s'" % (files_abs, subdoc_dir, 'brunnhilde'), shell=True)

                # if user selected 'filesonly', remove disk image files and repackage
                if args.filesonly == True:
                    keep_logical_files_only(object_dir)

                # write checksums
                if args.bagfiles == True: # bag entire SIP
                    subprocess.call("bagit.py --processes 4 '%s'" % (sip_dir), shell=True)
                else: # write metadata/checksum.md5
                    subprocess.call("cd '%s' && md5deep -rl ../objects > checksum.md5" % (metadata_dir), shell=True)

                # modify file permissions
                subprocess.call("sudo find '%s' -type d -exec chmod 755 {} \;" % (sip_dir), shell=True)
                subprocess.call("sudo find '%s' -type f -exec chmod 644 {} \;" % (sip_dir), shell=True)

            elif ('hfs' in disk_fs.lower()) and ('hfs+' not in disk_fs.lower()):
                # mount disk image
                subprocess.call("sudo mount -t hfs -o loop,ro,noexec '%s' /mnt/diskid/" % (diskimage), shell=True)

                # use md5deep to make dfxml
                dfxml_file = os.path.abspath(os.path.join(subdoc_dir, 'dfxml.xml'))
                subprocess.call("md5deep -rd /mnt/diskid/ > '%s'" % (dfxml_file), shell=True)

                # unmount disk image
                subprocess.call('sudo umount /mnt/diskid', shell=True)

                # carve files using hfsexplorer
                if args.resforks == True:
                    try:
                        subprocess.check_output(['bash', '/usr/share/hfsexplorer/bin/unhfs', '-v', '-resforks', 'APPLEDOUBLE', '-o', files_dir, diskimage])
                    except subprocess.CalledProcessError as e:
                        logandprint('ERROR: HFS Explorer could not carve the following files from image: %s' % (e.output))
                else:
                    try:
                        subprocess.check_output(['bash', '/usr/share/hfsexplorer/bin/unhfs', '-v', '-o', files_dir, diskimage])
                    except subprocess.CalledProcessError as e:
                        logandprint('ERROR: HFS Explorer could not carve the following files from image: %s' % (e.output)) 

                # run brunnhilde and write to reports directory
                files_abs = os.path.abspath(files_dir)
                if args.piiscan == True: # brunnhilde with bulk_extractor
                    subprocess.call("brunnhilde.py -zb '%s' '%s' '%s'" % (files_abs, subdoc_dir, 'brunnhilde'), shell=True)
                else: # brunnhilde without bulk_extractor
                    subprocess.call("brunnhilde.py -z '%s' '%s' '%s'" % (files_abs, subdoc_dir, 'brunnhilde'), shell=True)
                
                # if user selected 'filesonly', remove disk image files and repackage
                if args.filesonly == True:
                    keep_logical_files_only(object_dir)

                # write checksums
                if args.bagfiles == True: # bag entire SIP
                    subprocess.call("bagit.py --processes 4 '%s'" % (sip_dir), shell=True)
                else: # write metadata/checksum.md5
                    subprocess.call("cd '%s' && md5deep -rl ../objects > checksum.md5" % (metadata_dir), shell=True)

                # modify file permissions
                subprocess.call("sudo find '%s' -type d -exec chmod 755 {} \;" % (sip_dir), shell=True)
                subprocess.call("sudo find '%s' -type f -exec chmod 644 {} \;" % (sip_dir), shell=True)

            elif 'udf' in disk_fs.lower():
                # mount image
                subprocess.call("sudo mount -t udf -o loop '%s' /mnt/diskid/" % (diskimage), shell=True)

                # use fiwalk to create dfxml
                dfxml_file = os.path.abspath(os.path.join(subdoc_dir, 'dfxml.xml'))
                subprocess.call("md5deep -rd /mnt/diskid/ > '%s'" % (dfxml_file), shell=True)
                
                # copy files from disk image to files dir
                shutil.rmtree(files_dir) # delete to enable use of copytree
                shutil.copytree('/mnt/diskid/', files_dir, symlinks=False, ignore=None)

                # unmount disk image
                subprocess.call('sudo umount /mnt/diskid', shell=True) # unmount

                # run brunnhilde and write to submissionDocumentation
                files_abs = os.path.abspath(files_dir)
                if args.piiscan == True: # brunnhilde with bulk_extractor
                    subprocess.call("brunnhilde.py -zbw '%s' '%s' '%s'" % (files_abs, subdoc_dir, 'brunnhilde'), shell=True)
                else: # brunnhilde without bulk_extractor
                    subprocess.call("brunnhilde.py -zw '%s' '%s' '%s'" % (files_abs, subdoc_dir, 'brunnhilde'), shell=True)
                
                # if user selected 'filesonly', remove disk image files and repackage
                if args.filesonly == True:
                    keep_logical_files_only(object_dir)

                # write checksums
                if args.bagfiles == True: # bag entire SIP
                    subprocess.call("bagit.py --processes 4 '%s'" % (sip_dir), shell=True)
                else: # write metadata/checksum.md5
                    subprocess.call("cd '%s' && md5deep -rl ../objects > checksum.md5" % (metadata_dir), shell=True)

                # modify file permissions
                subprocess.call("sudo find '%s' -type d -exec chmod 755 {} \;" % (sip_dir), shell=True)
                subprocess.call("sudo find '%s' -type f -exec chmod 644 {} \;" % (sip_dir), shell=True)
            
            else:
                logandprint('NOTICE: Skipping processing of unknown disk type.')
                unprocessed.append(file)

        # no raw disk image
        else:
            logandprint('NOTICE: No raw disk image. Skipping disk.')
            unprocessed.append(file)

    else:
        # write skipped file to log
        logandprint('NOTICE: File is not a disk image. Skipping file.')

# print unprocessed list
if unprocessed:
    skipped_disks = ', '.join(unprocessed)
    logandprint('Processing complete. Skipped disks: %s' % (skipped_disks))
else:
    logandprint('Processing complete. All disk images processed. Results in %s.' % (destination))

# write description spreadsheet
create_spreadsheet(args.filesonly)

# close files
spreadsheet.close()
log.close()
