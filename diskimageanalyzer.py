#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Disk Image Analyzer

Call from "Analysis" mode in CCA Disk Image Processor
or run as separate script.

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


def write_to_spreadsheet(disk_result, volumes, spreadsheet_path, export_all, logger):
    """Append info for current disk to analysis CSV"""
    spreadsheet = open(spreadsheet_path, "a")
    writer = csv.writer(spreadsheet, quoting=csv.QUOTE_NONNUMERIC)

    item = os.path.basename(disk_result)
    disk_volumes = volumes[item]
    number_volumes = len(disk_volumes)

    date_earliest = ""
    date_latest = ""

    virus_found = False

    # Get and sum information from all DFXML files generated
    dfxml_files = []
    for root, _, files in os.walk(disk_result):
        for file in files:
            if file.startswith("dfxml"):
                dfxml_files.append(os.path.join(root, file))

    dfxml_files_info = []
    for dfxml_file in dfxml_files:
        dfxml_info = _parse_dfxml(dfxml_file, logger)
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
                os.path.basename(disk_result),
                0,
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "Error reading DFXML files.",
            ]
        )
        logger.error("Unable to read DFXML files for {}".format(item))
        spreadsheet.close()
        return

    if date_earliest[:4] == date_latest[:4]:
        date_statement = date_earliest[:4]
    else:
        date_statement = "{}-{}".format(date_earliest[:4], date_latest[:4])

    extent = "{} digital files ({})".format(
        file_count, human_readable_size(total_bytes)
    )

    file_formats = []
    file_format_csv = os.path.join(
        disk_result,
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

    virus_log = os.path.join(disk_result, "brunnhilde", "logs", "viruscheck-log.txt")
    try:
        with open(virus_log, "r") as virus:
            first_line = virus.readline()
            if "FOUND" in first_line:
                virus_found = True
    except:
        logger.error("Unable to read virus log for disk {}".format(item))

    scope_content = "File formats: {}".format(file_formats_str)

    # write csv row
    writer.writerow(
        [
            os.path.basename(disk_result),
            number_volumes,
            file_systems_str,
            date_statement,
            date_earliest,
            date_latest,
            extent,
            virus_found,
            scope_content,
        ]
    )
    logger.info("Described {} successfully.".format(item))

    spreadsheet.close()


def _parse_dfxml(dfxml_path, logger, export_all=False):
    """Parse DFXML and return dict of information for spreadsheet."""
    volume_info = {"files": 0, "bytes": 0, "date_earliest": "", "date_latest": ""}

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

    except Exception as err:
        logger.error("Error reading DFXML file {}: {}".format(dfxml_path, err))
        return

    return volume_info


def _make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--exportall",
        help="Export all (not only allocated) with tsk_recover",
        action="store_true",
    )
    parser.add_argument(
        "-k",
        "--keepfiles",
        help="Retain exported logical files from each disk",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--resforks",
        help="Export AppleDouble resource forks from HFS-formatted disks",
        action="store_true",
    )
    parser.add_argument("--quiet", action="store_true", help="Write only errors to log")
    parser.add_argument("source", help="Path to folder containing disk images")
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

    source = os.path.abspath(args.source)
    destination = os.path.abspath(args.destination)

    # create output directories
    if os.path.exists(destination):
        shutil.rmtree(destination)
    diskimages_dir = os.path.join(destination, "diskimages")
    files_dir = os.path.join(destination, "files")
    results_dir = os.path.join(destination, "reports")
    for dir_ in (destination, diskimages_dir, files_dir, results_dir):
        os.makedirs(dir_)

    logger = _configure_logging(
        os.path.join(destination, "diskimageanalyzer.log"), args
    )

    unanalyzed = []
    volumes = {}

    for file in sorted(os.listdir(source)):
        logger.info("Found disk image: {}".format(file))

        if not file.lower().endswith(
            (".e01", ".000", ".ewf", ".001", ".raw", ".img", ".dd", ".iso")
        ):
            logger.info("File is not a disk image. Skipping file.")
            continue

        image_path = os.path.join(source, file)
        image_id = os.path.splitext(file)[0]
        image_ext = os.path.splitext(file)[1]

        disk_results_dir = os.path.join(results_dir, file)
        os.makedirs(disk_results_dir)

        # copy disk image and its subsequent parts and sidecars to objects dir
        # and used copied image moving forward
        for file_ in os.listdir(args.source):
            if file_.startswith(image_id):
                shutil.copyfile(
                    os.path.join(args.source, file_),
                    os.path.join(diskimages_dir, file_),
                )
        image_path = os.path.join(diskimages_dir, file)

        disk_files_dir = os.path.join(files_dir, file)

        disk_image = DiskImage(image_path)
        disk_image.run_disktype(os.path.join(disk_results_dir, "disktype.txt"))
        disk_volumes = disk_image.carve_files_from_all_volumes(
            destination_path=disk_files_dir,
            export_unallocated=args.exportall,
            appledouble_resforks=args.resforks,
            dfxml_directory=disk_results_dir,
        )

        volumes[file] = disk_volumes

        if not os.path.isdir(disk_files_dir) or not os.listdir(disk_files_dir):
            logger.error("No files carved from disk image {} - skipping")
            unanalyzed.append(os.path.basename(image_path))

        subprocess.call(
            "brunnhilde.py -zwb '{}' '{}'".format(
                disk_files_dir, os.path.join(disk_results_dir, "brunnhilde")
            ),
            shell=True,
        )

        if not args.keepfiles:
            shutil.rmtree(disk_files_dir)

    shutil.rmtree(diskimages_dir)

    if not args.keepfiles:
        shutil.rmtree(files_dir)

    # create analysis csv, write header, and close file
    ANALYSIS_CSV_PATH = os.path.join(destination, "analysis.csv")
    spreadsheet = open(ANALYSIS_CSV_PATH, "w")
    writer = csv.writer(spreadsheet, quoting=csv.QUOTE_NONNUMERIC)
    header_list = [
        "Disk image",
        "Volumes",
        "File systems",
        "Date statement",
        "Date begin",
        "Date end",
        "Extent",
        "Virus found",
        "Content description",
    ]
    writer.writerow(header_list)
    spreadsheet.close()

    # add info to analysis csv for each SIP
    for item in sorted(os.listdir(results_dir)):
        disk_result = os.path.join(results_dir, item)
        write_to_spreadsheet(
            disk_result,
            volumes,
            os.path.join(destination, "analysis.csv"),
            args.exportall,
            logger,
        )

    # write closing message
    if unanalyzed:
        skipped_disks = ", ".join(unanalyzed)
        logger.info("Analysis complete. Skipped disks: %s." % (skipped_disks))
    else:
        logger.info(
            "Analysis complete. All disk images analyzed. Results in %s."
            % (destination)
        )


if __name__ == "__main__":
    main()
