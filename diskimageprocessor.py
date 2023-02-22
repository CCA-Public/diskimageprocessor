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

Tessa Walsh
https://bitarchivist.net
"""

import argparse
import csv
import datetime
import itertools
import logging
import os
import shutil
import subprocess
import sys
import time

from disk_image_toolkit import DiskImage
from disk_image_toolkit.dfxml import objects
from disk_image_toolkit.util import human_readable_size


THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


def create_spreadsheet(args, sips, volumes, logger):
    """Create csv describing created SIPs"""

    # open description spreadsheet
    csv_path = os.path.abspath(os.path.join(args.destination, "description.csv"))
    with open(csv_path, "w") as description_csv:
        writer = csv.writer(description_csv, quoting=csv.QUOTE_NONNUMERIC)

        # write header
        header_list = [
            "Parent ID",
            "Identifier",
            "Title",
            "Archive Creator",
            "Date expression",
            "Date start",
            "Date end",
            "Level of description",
            "Extent and medium",
            "Scope and content",
            "Arrangement (optional)",
            "Accession number",
            "Appraisal, destruction, and scheduling information (optional)",
            "Name access points (optional)",
            "Geographic access points (optional)",
            "Conditions governing access (optional)",
            "Conditions governing reproduction (optional)",
            "Language of material (optional)",
            "Physical characteristics & technical requirements affecting use (optional)",
            "Finding aids (optional)",
            "Related units of description (optional)",
            "Archival history (optional)",
            "Immediate source of acquisition or transfer (optional)",
            "Archivists' note (optional)",
            "General note (optional)",
            "Description status",
        ]
        writer.writerow(header_list)

        # process each SIP
        for item in sorted(os.listdir(sips)):
            sip_path = os.path.join(sips, item)

            if not os.path.isdir(sip_path):
                continue

            disk_volumes = volumes[item]
            number_volumes = len(disk_volumes)

            date_earliest = ""
            date_latest = ""

            # Get and sum information from all DFXML files generated
            dfxml_files = []
            subdoc_dir = os.path.join(sip_path, "metadata", "submissionDocumentation")
            if args.bagfiles:
                subdoc_dir = os.path.join(
                    sip_path, "data", "metadata", "submissionDocumentation"
                )
            for root, _, files in os.walk(subdoc_dir):
                for file in files:
                    if file.startswith("dfxml"):
                        dfxml_files.append(os.path.join(root, file))

            dfxml_files_info = []
            for dfxml_file in dfxml_files:
                dfxml_info = _parse_dfxml(dfxml_file)
                if not dfxml_info:
                    logger.warning(
                        "No fileobjects in DFXML file {} - possibly file system fiwalk doesn't recognize".format(
                            dfxml_file
                        )
                    )
                    continue
                dfxml_files_info.append(dfxml_info)

            file_count = sum([dfxml_info["files"] for dfxml_info in dfxml_files_info])
            total_bytes = sum([dfxml_info["bytes"] for dfxml_info in dfxml_files_info])
            file_systems = [volume["file_system"] for volume in disk_volumes]
            # Deduplicate list
            file_systems = list(dict.fromkeys(file_systems))
            file_systems_str = ", ".join(file_systems)

            for dfxml_info in dfxml_files_info:
                if not date_earliest or dfxml_info["date_earliest"] < date_earliest:
                    date_earliest = dfxml_info["date_earliest"]
                if not date_latest or dfxml_info["date_latest"] > date_latest:
                    date_latest = dfxml_info["date_latest"]

            if file_count == 0:
                writer.writerow(
                    [
                        "",
                        item,
                        "",
                        "",
                        "Error",
                        "Error",
                        "Error",
                        "File",
                        "Error",
                        "Error gathering statistics from SIP directory.",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )
                logger.error("Unable to read DFXML files for {}".format(sip_path))
                continue

            # Get file formats from Brunnhilde
            file_formats = []
            file_format_csv = os.path.join(
                sip_path,
                "metadata",
                "submissionDocumentation",
                "brunnhilde",
                "csv_reports",
                "formats.csv",
            )
            if args.bagfiles:
                file_format_csv = os.path.join(
                    sip_path,
                    "data",
                    "metadata",
                    "submissionDocumentation",
                    "brunnhilde",
                    "csv_reports",
                    "formats.csv",
                )

            try:
                with open(file_format_csv, "r") as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in itertools.islice(reader, 5):
                        file_formats.append(row[0])
            except:
                file_formats.append(
                    "ERROR! No Brunnhilde formats.csv file to pull formats from."
                )

            file_formats = [element or "Unidentified" for element in file_formats]
            file_formats_str = ", ".join(file_formats)

            if date_earliest[:4] == date_latest[:4]:
                date_statement = date_earliest[:4]
            else:
                date_statement = "{}-{}".format(date_earliest[:4], date_latest[:4])

            extent = "{} digital files ({})".format(
                file_count, human_readable_size(total_bytes)
            )

            if number_volumes > 1:
                scope_content = "Files exported from {} volumes with file systems: {}. File formats: {}".format(
                    number_volumes, file_systems_str, file_formats_str
                )
            else:
                scope_content = "Files exported from {} file system volume. File formats: {}".format(
                    disk_volumes[0]["file_system"], file_formats_str
                )

            # write csv row
            writer.writerow(
                [
                    "",
                    item,
                    "",
                    "",
                    date_statement,
                    date_earliest,
                    date_latest,
                    "File",
                    extent,
                    scope_content,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )

            logger.info("Described %s successfully." % (sip_path))

    logger.info("Description CSV created.")


def _parse_dfxml(dfxml_path, export_all=False):
    """Parse DFXML and return dict of information for spreadsheet."""
    volume_info = {
        "files": 0,
        "bytes": 0,
        "date_earliest": "",
        "date_latest": "",
    }

    mtimes = []
    ctimes = []
    crtimes = []

    try:
        for event, obj in objects.iterparse(dfxml_path):
            if not isinstance(obj, objects.FileObject):
                continue

            # skip directories and links
            if obj.name_type:
                if obj.name_type != "r":
                    continue

            # skip unallocated unless we exported all files
            if not export_all:
                if obj.unalloc:
                    if obj.unalloc == 1:
                        continue

            volume_info["files"] += 1

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

            volume_info["bytes"] += obj.filesize

        # filter "None" values from date lists
        for date_list in mtimes, ctimes, crtimes:
            while "None" in date_list:
                date_list.remove("None")

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

        # determine which set of dates to use (logic: use set with earliest start date,
        # default to date modified)
        use_ctimes = False
        use_crtimes = False

        if not date_earliest_m:
            date_earliest_m = datetime.datetime.now().year
            date_latest_m = datetime.datetime.now().year
        date_to_use = date_earliest_m

        if date_earliest_c:
            if date_earliest_c < date_to_use:
                date_to_use = date_earliest_c
                use_ctimes = True
        if date_earliest_cr:
            if date_earliest_cr < date_to_use:
                date_to_use = date_earliest_cr
                use_ctimes = False
                use_crtimes = True

        if use_ctimes:
            date_earliest = date_earliest_c[:10]
            date_latest = date_latest_c[:10]
        elif use_crtimes:
            date_earliest = date_earliest_cr[:10]
            date_latest = date_latest_cr[:10]
        else:
            date_earliest = date_earliest_m[:10]
            date_latest = date_latest_m[:10]

        volume_info["date_earliest"] = date_earliest
        volume_info["date_latest"] = date_latest

    except Exception:
        return

    return volume_info


def keep_logical_files_only(objects_dir):
    """Remove disk image from SIP and repackage"""

    # get list of files in files dir
    files_dir = os.path.join(objects_dir, "files")
    files = os.listdir(files_dir)
    files = [os.path.join(files_dir, filename) for filename in files]

    # move files up one directory
    for f in files:
        shutil.move(f, objects_dir)

    # delete file and diskimage dirs
    shutil.rmtree(files_dir)
    shutil.rmtree(os.path.join(objects_dir, "diskimage"))


def _make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--bagfiles",
        help="Bag files instead of writing checksum.md5",
        action="store_true",
    )
    parser.add_argument(
        "-e",
        "--exportall",
        help="Export all (not only allocated) with tsk_recover",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--filesonly",
        help="Include digital files only (not disk images) in SIPs",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--piiscan",
        help="Run bulk_extractor in Brunnhilde scan",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--resforks",
        help="Export AppleDouble resource forks from HFS-formatted disks",
        action="store_true",
    )
    parser.add_argument("--quiet", action="store_true", help="Write only errors to log")
    parser.add_argument(
        "source", help="Source directory containing disk images (and related files)"
    )
    parser.add_argument("destination", help="Output destination")

    return parser


def _configure_logging(log_path, args):
    from importlib import reload

    reload(logging)

    log_level = logging.ERROR if args.quiet else logging.INFO
    logging.basicConfig(
        filename=log_path,
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger()

    return logger


def main():
    parser = _make_parser()
    args = parser.parse_args()

    # create output directories
    destination = os.path.abspath(args.destination)
    sips = os.path.abspath(os.path.join(destination, "SIPs"))
    if os.path.exists(destination):
        shutil.rmtree(destination)
    for dir_ in (destination, sips):
        os.makedirs(dir_)

    logger = _configure_logging(
        os.path.join(destination, "diskimageprocessor.log"), args
    )

    unprocessed = []
    volumes = {}

    for file in sorted(os.listdir(args.source)):
        logger.info("Found disk image: {}".format(file))

        if not file.lower().endswith(
            (".e01", ".000", ".ewf", ".001", ".raw", ".img", ".dd", ".iso")
        ):
            logger.info("File is not a disk image. Skipping file.")
            continue

        image_path = os.path.join(args.source, file)
        image_id = os.path.splitext(file)[0]
        image_ext = os.path.splitext(file)[1]

        # create new folders
        sip_dir = os.path.join(sips, file)
        object_dir = os.path.join(sip_dir, "objects")
        diskimage_dir = os.path.join(object_dir, "diskimage")
        files_dir = os.path.join(object_dir, "files")
        metadata_dir = os.path.join(sip_dir, "metadata")
        subdoc_dir = os.path.join(metadata_dir, "submissionDocumentation")

        for folder in (
            sip_dir,
            object_dir,
            diskimage_dir,
            files_dir,
            metadata_dir,
            subdoc_dir,
        ):
            os.makedirs(folder)

        # copy disk image and its subsequent parts and sidecars to objects dir
        # and used copied image moving forward
        for file_ in os.listdir(args.source):
            if file_.startswith(image_id):
                try:
                    shutil.copyfile(
                        os.path.join(args.source, file_),
                        os.path.join(diskimage_dir, file_),
                    )
                except:
                    logger.error(
                        "ERROR: File {} not successfully copied to {}".format(
                            file_, diskimage_dir
                        )
                    )
        image_path = os.path.join(diskimage_dir, file)

        disk_image = DiskImage(image_path)
        disk_image.run_disktype(os.path.join(subdoc_dir, "disktype.txt"))
        disk_volumes = disk_image.carve_files_from_all_volumes(
            destination_path=files_dir,
            export_unallocated=args.exportall,
            appledouble_resforks=args.resforks,
            dfxml_directory=subdoc_dir,
        )

        volumes[file] = disk_volumes

        if not os.path.isdir(files_dir) or not os.listdir(files_dir):
            logger.error("No files carved from disk image {} - skipping")
            unprocessed.append(os.path.basename(image_path))

        if args.piiscan:
            subprocess.call(
                'brunnhilde.py -zb "{}" "{}"'.format(
                    files_dir, os.path.join(subdoc_dir, "brunnhilde")
                ),
                shell=True,
            )
        else:
            subprocess.call(
                'brunnhilde.py -z "{}" "{}"'.format(
                    files_dir, os.path.join(subdoc_dir, "brunnhilde")
                ),
                shell=True,
            )

        if args.filesonly:
            keep_logical_files_only(object_dir)

        # write checksums
        if args.bagfiles:
            # TODO: Multithread bagging via --processes when bug described at
            # https://github.com/LibraryOfCongress/bagit-python/issues/130 is
            # resolved.
            subprocess.call(
                'cd {} && bagit.py "{}"'.format(THIS_DIR, sip_dir),
                shell=True,
            )
        else:
            subprocess.call(
                'cd "{}" && md5deep -rl ../objects > checksum.md5'.format(metadata_dir),
                shell=True,
            )

    # write description CSV
    create_spreadsheet(args, sips, volumes, logger)

    # print unprocessed list
    if unprocessed:
        skipped_disks = ", ".join(unprocessed)
        logger.info("Processing complete. Skipped disks: %s" % (skipped_disks))
    else:
        logger.info(
            "Processing complete. All disk images processed. Results in %s."
            % (destination)
        )


if __name__ == "__main__":
    main()
