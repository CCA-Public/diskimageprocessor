# Disk Image Processor  

Analyze disk images and/or create ready-to-ingest SIPs from a directory of disk images and related files.  
Version: 1.0.0

## Usage

Disk Image Processor has two modes: Analysis and Processing. Each mode can be run from the GUI interface or as a separate CLI utility by calling the underlying Python 3 script.  

### Analysis

Underlying script: `diskimageanalyzer.py`  

In Analysis mode, each disk image is scanned and reported on. When complete, an "analysis.csv" file is created containing the following information for each disk image:  

* Disk image name  
* File system  
* Date statement  
* Date begin  
* Date end  
* Extent  
* Virus found (Boolean value)  
* File formats  

The destination directory also contains a "reports" directory containing a sub-directory for each disk image scanned. Each of these disk image sub-directories contains:  

* A DFXML file  
* Text output from "disktype"  
* Brunnhilde reports (including logs and reports from clamAV and bulk_extractor)  

Optionally, the destination directory may also contain a "files" directory, containing exported logical files from each recognized disk image in the source.

Because "Analysis" mode runs bulk_extractor against each disk, this process can take a while.  

### Processing

Underlying script: `diskimageprocessor.py`  

In Processing mode, each disk image is turned into a SIP, packaged as an ideal transfer to Archivematica's Automation tools, and reported on.

For disks with most file systems, `fiwalk` is used to generate DFXML and The Sleuth Kit's `tsk_recover` utility is used to carve allocated files from each disk image. Modified dates for the carved files are then restored from their recorded values in the fiwalk-generated DFXML file.

For disks with an HFS file system, files are exported from the disk image using CLI version of HFSExplorer and DFXML is generated using the `walk_to_dfxml.py` script from the DFXML Python bindings.

For disks with a UDF file system, files are copied from the mounted disk image and `walk_to_dfxml.py` is used to generate DFXML.

When complete, a "description.csv" spreadsheet is created containing some pre-populated archival description:  
* Date statement  
* Date begin  
* Date end  
* Extent  
* Scope and content (containing information about the tool used to carve logical files and the most common file formats)

The destination directory also contains a log file and a "SIPs" directory containing a SIP created from each input disk image. 

Each SIP directory contains a metadata/checksum.md5 manifest by default, but may optionally be bagged instead. 

By default, the "objects" directory in each SIP contains both a copy of a raw disk image (regardless of whether the input was raw or E01) and logical files carved from the image by unhfs or a mount-and-copy routine, depending on the disk's file system. The user can choose to instead have SIPs include only logical files.

The "metadata/submissionDocumentation" directory in each SIP contains:  

* A DFXML file  
* Text output from "disktype"  
* Brunnhilde reports (including logs and reports from clamAV and, optionally, bulk_extractor)  

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

This utility is designed for easy use in BitCurator v1.8.0+. All dependencies should already be installed in new releases of BitCurator. Installation outside of BitCurator is possible but difficult, with many dependencies, including Python3, PyQt5, TSK, Bulk Extractor, and the DFXML Python bindings. You will likely also need to modify some hardcoded paths in `main.py` and the processing scripts.

### Install as part of CCA Tools  

Install all of the CCA Tools together using the installation script included in the [CCA Tools repo](https://github.com/CCA-Public/cca-tools).  

### Install as a separate utility
* Install [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5):  
`sudo pip3 install pyqt5`  
* Clone this repo to your local machine.  
* Make install script executable (may need to be run with sudo privileges):  
`chmod u+x install.sh` 
* Run the install script with sudo privileges:  
`sudo ./install.sh`   

### PyQt4 version

Please note that Disk Image Processor v1.0.0 uses PyQt5. Installation of PyQt5 may cause issues with existing PyQt4 programs in BitCurator. For the a PyQt4 version of the Disk Image Processor that will not affect the functionality of other tools, see the [0.7.3 release](https://github.com/CCA-Public/diskimageprocessor/releases/tag/v0.7.3).

## Credit  

Inspired by [Jess Whyte's work at the University of Toronto's Fisher Rare Book Library](https://saaers.wordpress.com/2016/04/12/clearing-the-digital-backlog-at-the-thomas-fisher-rare-book-library/comment-page-1/), especially the [Disk-ID-md5deep script](https://github.com/jesswhyte/Disk-ID-md5deep/).  
