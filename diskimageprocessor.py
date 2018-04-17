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
    dt = time.mktime(datetime.datetime.strptime(str_time, 
        "%Y-%m-%dT%H:%M:%S").timetuple())
    return dt

def create_spreadsheet(args, sips, LOGGER):
    """ Create csv describing created SIPs """

    # open description spreadsheet
    csv_path = os.path.abspath(os.path.join(args.destination, 'description.csv'))
    with open(csv_path, 'w') as description_csv:
        writer = csv.writer(description_csv, quoting=csv.QUOTE_NONNUMERIC)
        
        # write header
        header_list = ['Parent ID', 'Identifier', 'Title', 'Archive Creator', 'Date expression', 'Date start', 'Date end', 
            'Level of description', 'Extent and medium', 'Scope and content', 'Arrangement (optional)', 'Accession number', 
            'Appraisal, destruction, and scheduling information (optional)', 'Name access points (optional)', 
            'Geographic access points (optional)', 'Conditions governing access (optional)', 'Conditions governing reproduction (optional)', 
            'Language of material (optional)', 'Physical characteristics & technical requirements affecting use (optional)', 
            'Finding aids (optional)', 'Related units of description (optional)', 'Archival history (optional)', 
            'Immediate source of acquisition or transfer (optional)', "Archivists' note (optional)", 'General note (optional)', 
            'Description status']
        writer.writerow(header_list)

        # process each SIP
        for item in sorted(os.listdir(sips)):
            current = os.path.join(sips, item)
            # test if entry if directory
            if os.path.isdir(current):
                
                # intialize values
                number_files = 0
                total_bytes = 0
                mtimes = []
                ctimes = []
                crtimes = []

                # parse dfxml file
                if args.bagfiles == True:
                    dfxml_file = os.path.abspath(os.path.join(current, 
                        'data', 'metadata', 'submissionDocumentation', 'dfxml.xml'))
                else:
                    dfxml_file = os.path.abspath(os.path.join(current, 
                        'metadata', 'submissionDocumentation', 'dfxml.xml'))

                # try to read DFXML file
                try:
                    # gather info for each FileObject
                    for (event, obj) in Objects.iterparse(dfxml_file):
                        
                        # only work on FileObjects
                        if not isinstance(obj, Objects.FileObject):
                            continue

                        # skip directories and links
                        if obj.name_type:
                            if obj.name_type != "r":
                                continue

                        # skip unallocated if args.exportall is False
                        if args.exportall == False:
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
                        extent = "1 digital file (%s)" % size_readable
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

                    # store date_earliest and date_latest values based on datetype used
                    if use_ctimes == True:
                        date_earliest = date_earliest_c[:10]
                        date_latest = date_latest_c[:10]
                    elif use_crtimes == True:
                        date_earliest = date_earliest_cr[:10]
                        date_latest = date_latest_cr[:10]
                    else:
                        date_earliest = date_earliest_m[:10]
                        date_latest = date_latest_m[:10]

                    # write date statement
                    if date_earliest[:4] == date_latest[:4]:
                        date_statement = '%s' % date_earliest[:4]
                    else:
                        date_statement = '%s - %s' % (date_earliest[:4], date_latest[:4])

                    # gather file system info, discern tool used
                    if args.bagfiles == True:
                        disktype = os.path.join(current, 'data', 'metadata', 
                            'submissionDocumentation', 'disktype.txt')
                    else:
                        disktype = os.path.join(current, 'metadata', 
                            'submissionDocumentation', 'disktype.txt')
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

                    # save tool used to carve files
                    if any(x in disk_fs.lower() for x in ('ntfs', 'fat', 'ext', 'iso9660', 'hfs+', 'ufs', 'raw', 'swap', 'yaffs2')):
                        tool = "carved from the disk image using the Sleuth Kit command line utility tsk_recover"
                    elif ('hfs' in disk_fs.lower()) and ('hfs+' not in disk_fs.lower()):
                        tool = "carved from disk image using the HFSExplorer command line utility"
                    elif 'udf' in disk_fs.lower():
                        tool = "copied from the mounted disk image"
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
                            fileformat_csv = os.path.join(current, 'data', 'metadata', 'submissionDocumentation', 
                                'brunnhilde', 'csv_reports', 'formats.csv')
                        else:
                            fileformat_csv = os.path.join(current, 'metadata', 'submissionDocumentation', 
                                'brunnhilde', 'csv_reports', 'formats.csv')
                        try: 
                            with open(fileformat_csv, 'r') as f:
                                reader = csv.reader(f)
                                next(reader)
                                for row in itertools.islice(reader, 5):
                                    fileformats.append(row[0])
                        except:
                            fileformats.append("ERROR! No formats.csv file to pull formats from.")
                        # replace empty elements with 'Unidentified
                        fileformats = [element or 'Unidentified' for element in fileformats]
                        formatlist = ', '.join(fileformats)
                        
                        
                        # create scope and content note
                        if args.filesonly == True:
                            scopecontent = 'File includes digital files %s. Most common file formats: %s' % (tool, formatlist)
                        else:
                            scopecontent = 'File includes both a disk image and digital files %s. Most common file formats: %s' % (tool, formatlist)

                    # write csv row
                    writer.writerow(['', item, '', '', date_statement, date_earliest, date_latest, 'File', extent, 
                        scopecontent, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                    
                    LOGGER.info('Described %s successfully.' % (current))

                # if error reading DFXML file, report that
                except:
                    # write error to csv
                    writer.writerow(['', item, '', '', 'Error', 'Error', 'Error', 'File', 'Error', 
                        'Error reading DFXML file.', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                    LOGGER.error('DFXML file for %s not well-formed.' % (current))

    LOGGER.info('Description CSV created.')

def keep_logical_files_only(objects_dir):
    """ Remove disk image from SIP and repackage """

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

def _make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bagfiles", help="Bag files instead of writing checksum.md5", action="store_true")
    parser.add_argument("-e", "--exportall", help="Export all (not only allocated) with tsk_recover", action="store_true")
    parser.add_argument("-f", "--filesonly", help="Include digital files only (not disk images) in SIPs", action="store_true")
    parser.add_argument("-p", "--piiscan", help="Run bulk_extractor in Brunnhilde scan", action="store_true")
    parser.add_argument("-r", "--resforks", help="Export AppleDouble resource forks from HFS-formatted disks", action="store_true")
    parser.add_argument("--quiet", action="store_true", help="Write only errors to log")
    parser.add_argument("source", help="Source directory containing disk images (and related files)")
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

    # parse args
    parser = _make_parser()
    args = parser.parse_args()

    # create output directories
    destination = os.path.abspath(args.destination)
    if not os.path.exists(destination):
        os.makedirs(destination)
    else: # delete and replace if exists
        shutil.rmtree(destination)
        os.makedirs(destination)

    sips = os.path.join(destination, 'SIPs')
    os.makedirs(sips)

    # open log file
    LOGGER = logging.getLogger()
    log_file = os.path.join(destination, 'diskimageprocessor.log')
    _configure_logging(args, log_file)

    # make list for unprocessed disks
    unprocessed = []

    # iterate through files in source directory
    for file in sorted(os.listdir(args.source)):

        # record filename in log
        LOGGER.info('NEW FILE: %s' % (file))
        
        # determine if disk image
        if file.lower().endswith((".e01", ".000", ".001", ".raw", ".img", ".dd", ".iso")):

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
                    LOGGER.error('Disk image %s could not be converted to raw image format. Skipping disk.' % (file))

            else:
                raw_image = True
                for movefile in os.listdir(args.source):
                    # if filename starts with disk image basename (this will also capture info and log files, multi-part disk images, etc.)
                    if movefile.startswith(image_id):
                        # copy file to objects/diskimage
                        try:
                            shutil.copyfile(os.path.join(args.source, movefile), os.path.join(diskimage_dir, movefile))
                        except:
                            LOGGER.error('ERROR: File %s not successfully copied to %s' % (movefile, diskimage_dir))
                diskimage = os.path.join(diskimage_dir, file) # use disk image in objects/diskimage moving forward

            # raw disk image
            if raw_image == True:

                # run disktype on disk image, save output to submissionDocumentation
                disktype = os.path.join(subdoc_dir, 'disktype.txt')
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
                LOGGER.info('File system: %s' % (disk_fs))

                # handle differently by file system
                if any(x in disk_fs.lower() for x in ('ntfs', 'fat', 'ext', 'iso9660', 'hfs+', 'ufs', 'raw', 'swap', 'yaffs2')):
                    # use fiwalk to make dfxml
                    fiwalk_file = os.path.join(subdoc_dir, 'dfxml.xml')
                    try:
                        subprocess.check_output(['fiwalk', '-X', fiwalk_file, diskimage])
                    except subprocess.CalledProcessError as e:
                        LOGGER.error('Fiwalk could not create DFXML for disk %s. STDERR: %s' % (diskimage, e.output))
                    
                    # carve images using tsk_recover
                    carve_flag = '-a' # default to exporting allocated files
                    if args.exportall == True:
                        carve_flag = '-e'
                    try:
                        subprocess.check_output(['tsk_recover', carve_flag, diskimage, files_dir])
                    except subprocess.CalledProcessError as e:
                        LOGGER.error('tsk_recover could not carve allocated files from disk %s. STDERR: %s' % (diskimage, e.output))    

                    # modify file permissions
                    subprocess.call("sudo find '%s' -type d -exec chmod 755 {} \;" % (sip_dir), shell=True)
                    subprocess.call("sudo find '%s' -type f -exec chmod 644 {} \;" % (sip_dir), shell=True)

                    # rewrite last modified dates of files based on values in DFXML
                    try:
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
                            exported_filepath = os.path.join(files_dir, dfxml_filename)
                            if os.path.isfile(exported_filepath):
                                os.utime(exported_filepath, (dfxml_filedate, dfxml_filedate))

                    except ValueError:
                        LOGGER.error("Could not rewrite modified dates for disk %s due to Objects.py ValueError" % (diskimage))

                    # run brunnhilde and write to submissionDocumentation
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


                elif ('hfs' in disk_fs.lower()) and ('hfs+' not in disk_fs.lower()):
                    # mount disk image
                    subprocess.call("sudo mount -t hfs -o loop,ro,noexec '%s' /mnt/diskid/" % (diskimage), shell=True)

                    # use walk_to_dfxml.py to make dfxml
                    dfxml_file = os.path.abspath(os.path.join(subdoc_dir, 'dfxml.xml'))
                    try:
                        subprocess.call("cd /mnt/diskid/ && python3 /usr/share/ccatools/diskimageprocessor/walk_to_dfxml.py > '%s'" % (dfxml_file), shell=True)
                    except:
                        LOGGER.error('walk_to_dfxml.py unable to generate DFXML for disk %s' % (diskimage))

                    # unmount disk image
                    subprocess.call('sudo umount /mnt/diskid', shell=True)

                    # carve files using hfsexplorer
                    if args.resforks == True:
                        try:
                            subprocess.check_output(['bash', '/usr/share/hfsexplorer/bin/unhfs', '-v', '-resforks', 'APPLEDOUBLE', '-o', files_dir, diskimage])
                        except subprocess.CalledProcessError as e:
                            LOGGER.error('HFS Explorer could not carve the following files from disk %s. Error output: %s' % (diskimage, e.output))
                    else:
                        try:
                            subprocess.check_output(['bash', '/usr/share/hfsexplorer/bin/unhfs', '-v', '-o', files_dir, diskimage])
                        except subprocess.CalledProcessError as e:
                            LOGGER.error('HFS Explorer could not carve the following files from disk %s. Error output: %s' % (diskimage, e.output)) 

                    # modify file permissions
                    subprocess.call("sudo find '%s' -type d -exec chmod 755 {} \;" % (sip_dir), shell=True)
                    subprocess.call("sudo find '%s' -type f -exec chmod 644 {} \;" % (sip_dir), shell=True)

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
                

                elif 'udf' in disk_fs.lower():
                    # mount image
                    subprocess.call("sudo mount -t udf -o loop '%s' /mnt/diskid/" % (diskimage), shell=True)

                    # use walk_to_dfxml.py to create dfxml
                    dfxml_file = os.path.abspath(os.path.join(subdoc_dir, 'dfxml.xml'))
                    try:
                        subprocess.call("cd /mnt/diskid/ && python3 /usr/share/dfxml/python/walk_to_dfxml.py > '%s'" % (dfxml_file), shell=True)
                    except:
                        LOGGER.error('walk_to_dfxml.py unable to generate DFXML for disk %s' % (diskimage))
                    
                    # copy files from disk image to files dir
                    shutil.rmtree(files_dir) # delete to enable use of copytree
                    try:
                        shutil.copytree('/mnt/diskid/', files_dir, symlinks=False, ignore=None)
                    except:
                        LOGGER.error("shutil.copytree unable to copy files from disk %s" % (diskimage))

                    # unmount disk image
                    subprocess.call('sudo umount /mnt/diskid', shell=True) # unmount

                    # modify file permissions
                    subprocess.call("sudo find '%s' -type d -exec chmod 755 {} \;" % (sip_dir), shell=True)
                    subprocess.call("sudo find '%s' -type f -exec chmod 644 {} \;" % (sip_dir), shell=True)

                    # run brunnhilde and write to submissionDocumentation
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

                else:
                    LOGGER.info('Skipping processing of unknown disk type.')
                    unprocessed.append(file)

            # no raw disk image
            else:
                LOGGER.info('No raw disk image. Skipping disk.')
                unprocessed.append(file)

        else:
            # write skipped file to log
            LOGGER.info('File is not a disk image. Skipping file.')

    # write description CSV
    create_spreadsheet(args, sips, LOGGER)

    # print unprocessed list
    if unprocessed:
        skipped_disks = ', '.join(unprocessed)
        LOGGER.info('Processing complete. Skipped disks: %s' % (skipped_disks))
    else:
        LOGGER.info('Processing complete. All disk images processed. Results in %s.' % (destination))

if __name__ == '__main__':
    main()