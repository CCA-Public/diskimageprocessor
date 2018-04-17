#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creates a SIP from any single disk image using options for
tsk_recover provided by the user.

Will only work for disk images containing a file system
able to be parsed by TSK.

Python 3

Tim Walsh
https://bitarchivist.net
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
import time

#import Objects.py from python dfxml tools
import Objects

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

def time_to_int(str_time):
    dt = time.mktime(datetime.datetime.strptime(str_time, 
        "%Y-%m-%dT%H:%M:%S").timetuple())
    return dt

def create_spreadsheet(args, destination, sip_dir, filename):
    # open description spreadsheet and write header
    with open(os.path.join(destination,'description.csv'), 'w') as spreadsheet:
        
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

        # add info for SIP in new line
        current = os.path.abspath(sip_dir)
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
                        scopecontent = 'File includes digital files carved from a disk image using tsk_recover. Most common file formats: %s' % (formatlist)
                    else:
                        scopecontent = 'File includes both a disk image and digital files carved from the disk image using tsk_recover. Most common file formats: %s' % (formatlist)

                # write csv row
                writer.writerow(['', filename, '', '', date_statement, date_earliest, date_latest, 'File', extent, 
                    scopecontent, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                
                print('Described %s successfully.' % (current))

            # if error reading DFXML file, report that
            except:
                # write error to csv
                writer.writerow(['', filename, '', '', 'Error', 'Error', 'Error', 'File', 'Error', 
                    'Error reading DFXML file.', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

                print('ERROR: DFXML file for %s not well-formed.' % (current))

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

def _make_parser():

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bagfiles", help="Bag files instead of writing checksum.md5", action="store_true")
    parser.add_argument("-e", "--exportall", help="Export all (not only allocated) with tsk_recover", action="store_true")
    parser.add_argument("-f", "--filesonly", help="Include digital files only (not disk images) in SIPs", action="store_true")
    parser.add_argument("-p", "--piiscan", help="Run bulk_extractor in Brunnhilde scan", action="store_true")
    parser.add_argument("--imgtype", help="Disk image type (see tsk_recover man page for values)", action="store")
    parser.add_argument("--fstype", help="File system type (see tsk_recover man page for values)", action="store")
    parser.add_argument("--sector_offset", help="Sector offset of partition to parse (see tsk-recover man page for details)", action="store")
    parser.add_argument("source", help="Source directory containing disk image (and related files)")
    parser.add_argument("destination", help="Output destination")
    
    return parser

def main():
    # parse args
    parser = _make_parser()
    args = parser.parse_args()
    source = os.path.abspath(args.source)
    destination = os.path.abspath(args.destination)

    # create output directories
    if not os.path.exists(destination):
        os.makedirs(destination)

    # iterate through files in source directory
    for file in sorted(os.listdir(source)):

        # record filename in log
        print('>>> NEW FILE: %s' % (file))

        # determine if disk image
        if file.endswith((".E01", ".000", ".001", ".raw", ".img", ".dd", ".iso")):

            # save info about file
            image_path = os.path.join(source, file)
            image_id = os.path.splitext(file)[0]
            image_ext = os.path.splitext(file)[1]

            # create new folders
            sip_dir = os.path.join(args.destination, file)
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
                    print('ERROR: Disk image could not be converted to raw image format. Skipping disk.')

            else:
                raw_image = True
                for movefile in os.listdir(source):
                    # if filename starts with disk image basename (this will also capture info and log files, multi-part disk images, etc.)
                    if movefile.startswith(image_id):
                        # copy file to objects/diskimage
                        try:
                            shutil.copyfile(os.path.join(source, movefile), os.path.join(diskimage_dir, movefile))
                        except:
                            print('ERROR: File %s not successfully copied to %s' % (movefile, diskimage_dir))
                diskimage = os.path.join(diskimage_dir, file) # use disk image in objects/diskimage moving forward

            # if raw disk image, process
            if raw_image == True:

                # use fiwalk to make dfxml
                fiwalk_file = os.path.join(subdoc_dir, 'dfxml.xml')
                try:
                    subprocess.check_output(['fiwalk', '-X', fiwalk_file, diskimage])
                except subprocess.CalledProcessError as e:
                    print('ERROR: Fiwalk could not create DFXML for disk. STDERR: %s' % (e.output))
                
                # carve images using tsk_recover with user-supplied options
                if args.exportall == True:
                    carvefiles = ['tsk_recover', '-e', diskimage, files_dir]
                else:
                    carvefiles = ['tsk_recover', '-a', diskimage, files_dir]

                if args.fstype:
                    carvefiles.insert(2, '-f')
                    carvefiles.insert(3, args.fstype)
                if args.imgtype:
                    carvefiles.insert(2, '-i')
                    carvefiles.insert(3, args.imgtype)
                if args.sector_offset:
                    carvefiles.insert(2, '-o')
                    carvefiles.insert(3, args.sector_offset)

                try:
                    subprocess.check_output(carvefiles)
                except subprocess.CalledProcessError as e:
                    print('ERROR: tsk_recover could not carve files from disk. STDERR: %s' % (e.output))    

                # modify file permissions
                subprocess.call("sudo find '%s' -type d -exec chmod 755 {} \;" % (sip_dir), shell=True)
                subprocess.call("sudo find '%s' -type f -exec chmod 644 {} \;" % (sip_dir), shell=True)

                # rewrite last modified dates of files based on values in DFXML
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

                # write description spreadsheet
                print('Generating description spreadsheet for file %s...' % (file))
                create_spreadsheet(args, destination, sip_dir, file)

            # no raw disk image
            else:
                print('NOTICE: No raw disk image. Skipping disk.')

        else:
            # write skipped file to log
            print('NOTICE: File is not a disk image. Skipping file.')

if __name__ == '__main__':
    main()