# Disk Image Processor  

Analyze disk images and/or create ready-to-ingest SIPs from a directory of disk images and related files.  

Version: 1.3.0

## Breaking Changes

In v1.2.0, diskimageprocessor.py and the Processing mode of the GUI were changed to populate an ArchivesSpace description import XLSX instead of the previous ISAD-based CSV.

In v1.3.0+, this change is reverted and the option to create an ArchivesSpace description XLSX removed.

## Usage

Disk Image Processor has two modes: Analysis and Processing. Each mode can be run from the GUI interface or as a separate CLI utility by calling the underlying Python 3 script.

### Analysis

Underlying script: `diskimageanalyzer.py`  

In Analysis mode, each disk image is scanned and reported on. When complete, an "analysis.csv" file is created containing the following information for each disk image:  

* Disk image name  
* Volumes  
* File systems  
* Date statement  
* Date begin  
* Date end  
* Extent  
* Virus found (Boolean value)  
* File formats  

The destination directory also contains a "reports" directory containing a sub-directory for each disk image scanned. Each of these disk image sub-directories contains:  

* A DFXML file  
* Text output from "disktype"  
* Brunnhilde reports (including logs and reports from ClamAV and bulk_extractor)  

Optionally, the destination directory may also contain a "files" directory, containing exported logical files from each recognized disk image in the source.

Because "Analysis" mode runs bulk_extractor against each disk, this process can take a while.  

### Processing

Underlying script: `diskimageprocessor.py`  

In Processing mode, each disk image is turned into a SIP, packaged as an ideal transfer to Archivematica's Automation tools, and reported on.

From v1.1.0, Disk Image Processor will export files from multiple volumes if they are present on the disk image. In v1.0.0 and earlier, only one volume was exported depending on the first file system volume found by disktype.

For most file systems, `fiwalk` is used to generate DFXML and The Sleuth Kit's `tsk_recover` utility is used to carve allocated files from each disk image. Modified dates for the carved files are then restored from their recorded values in the fiwalk-generated DFXML file.

For HFS file systems, files are exported from the disk image using CLI version of HFSExplorer and DFXML is generated using the `walk_to_dfxml.py` script from the DFXML Python bindings.

For UDF file systems, files are copied from the mounted disk image and `walk_to_dfxml.py` is used to generate DFXML.

Disk Image Processor will create a description.csv file containing the following columns:

* Date statement  
* Date begin  
* Date end  
* Extent  
* Scope and content (containing information about the tool used to carve logical files and the most common file formats)

(*Note in Disk Image Processor 1.2.0, this CSV file was replaced by an ArchivesSpace Excel spreadsheet by default. This change has been reverted in 1.3.0.*)

The destination directory also contains a log file and a "SIPs" directory containing a SIP created from each input disk image. 

Each SIP directory contains a metadata/checksum.md5 manifest by default, but may optionally be bagged instead. 

By default, the "objects" directory in each SIP contains both a copy of a raw disk image (regardless of whether the input was raw or E01) and logical files carved from the image by unhfs or a mount-and-copy routine, depending on the disk's file system. The user can choose to instead have SIPs include only logical files.

The "metadata/submissionDocumentation" directory in each SIP contains:  

* One or more DFXML files  
* Text output from "disktype"  
* Brunnhilde reports (including logs and reports from ClamAV and, optionally, bulk_extractor)  

### Process a single disk image, providing options to tsk_recover (CLI only)  

Also included is a Python 3 script `process_with_tsk_options.py`. This script allows the user to create a SIP and corresponding description for a single disk image (and accompanying files) while specifying the file system type, image type, and sector offset as needed for `tsk_recover`. This script may be useful for certain disks for which tsk_recover is unable to extract files using its autodetection methods.

## Supported file systems

* NTFS  
* FAT  
* ext2/3  
* ISO9660  
* UDF
* HFS  
* HFS+  
* UFS  
* RAW  
* SWAP  
* YAFFS2  

For disks with exfat file systems you may need to use the `process_with_tsk_options.py` script and explicitly specify the file system type. This is due to disktype's inability to recognize exfat file systems.

## Supported disk image types  

* raw (dd, iso, img, etc.)  
* EnCase/EWF (E01)  

*Note: EnCase disk images are converted to raw disk images for processing using [libewf](https://github.com/libyal/libewf)'s `ewf_export` utility. In Processing mode, the converted raw image is retained in the SIP unless the user selects to retain only logical files.*

## Disk image extensions recognized

Disk Image Processor recognizes which files are disk images by their file extensions. Currently, it looks for the following extensions (case-insensitive):  

* .e01  
* .000  
* .001  
* .raw  
* .img  
* .dd  
* .iso  

## Installation and dependencies

This utility is designed for easy use in BitCurator 4.

Installation outside of BitCurator is possible but difficult, with many dependencies, including Python 3.7+, PyQt5, TSK, HFS Explorer, md5deep, and Bulk Extractor.

### Install as part of CCA Tools  

Install all of the CCA Tools together using the installation script included in the [CCA Tools repo](https://github.com/CCA-Public/cca-tools).  

### Install as a separate utility

* Install [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5):  
`sudo pip3 install pyqt5`
* Clone this repo to your local machine.  
* Run the install script with sudo privileges (assuming BitCurator 4; for BitCurator 2-3 run `./install-bc2-ubuntu18.sh` instead):  
`sudo ./install.sh`

## Credit  

Inspired by [Jess Whyte's work at the University of Toronto's Fisher Rare Book Library](https://saaers.wordpress.com/2016/04/12/clearing-the-digital-backlog-at-the-thomas-fisher-rare-book-library/comment-page-1/), especially the [Disk-ID-md5deep script](https://github.com/jesswhyte/Disk-ID-md5deep/).  
