# Disk Image Processor  

Analyze disk images and/or create ready-to-ingest SIPs from a directory of disk images and related files.  
Version: 0.7.1 (beta)

[![Build Status](https://travis-ci.org/timothyryanwalsh/cca-diskimageprocessor.svg?branch=master)](https://travis-ci.org/timothyryanwalsh/cca-diskimageprocessor)

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

This utility is designed for easy use in BitCurator v1.8.0+. It requires Python 2.7 (to run the GUI) and Python 3.4+ (to run the scripts that analyze and process disk images), both of which are already included in BitCurator.    

### Install as part of CCA Tools  

Install all of the CCA Tools (and PyQT4) together using the install bash script in the [CCA Tools repo](https://github.com/timothyryanwalsh/cca-tools).  

### Install as a separate utility
* Clone this repo to your local machine.  
* Make install script executable (may need to be run with sudo privileges):  
`chmod u+x install.sh` 
* Run the install script with sudo privileges:  
`sudo ./install.sh`  

### Dependency and verison issues

#### Brunnhilde

Disk Image Processor will work with all versions of [Brunnhilde](https://github.com/timothyryanwalsh/brunnhilde); however, changes to Brunnhilde 1.5.1's default pattern matching for SSNs with bulk_extractor help in minimizing the number of false positives reported and keeping the Brunnhilde HTML report size reasonable. For best results, it is recommended to upgrade the version of Brunnhilde on your machine to 1.5.1+.  

#### HFS Explorer

unhfs, the command-line version of HFSExplorer, until recently had a bug that caused failures when attempting to extract AppleDouble resource forks alongside files. To avoid this issue, be sure that you have the [latest version](https://sourceforge.net/projects/catacombae/files/HFSExplorer/0.23.1%20%28snapshot%202016-09-02%29/) of HFSExplorer installed. In BitCurator 1.7.106+ and 1.8.0+, the patched version of HFS Explorer is already installed. 

In this patched release, unhfs.sh is renamed to unhfs (without a file extension). If file /usr/share/hfsexplorer/bin/unhfs.sh (with file extension) exists in your system, you must update HFSExplorer with the version linked above (recommended) or rename the unhfs.sh file to remove the file extension.

In BitCurator versions before 1.7.106, installation of the latest release of HFSEexplorer must be done manually by replacing the contents of /usr/share/hfsexplorer with the downloaded and extracted source. In order to continue using the HFSExplorer GUI in BitCurator versions before 1.7.106 after updating HFSExplorer, right-click on the HFS Explorer icon in "Additional Tools", select "Properties", and amend the text in "Command" to:  

`/usr/share/hfsexplorer/bin/./hfsexplorer %F`   

## Credit  

Inspired by [Jess Whyte's work at the University of Toronto's Fisher Rare Book Library](https://saaers.wordpress.com/2016/04/12/clearing-the-digital-backlog-at-the-thomas-fisher-rare-book-library/comment-page-1/), especially the [Disk-ID-md5deep script](https://github.com/jesswhyte/Disk-ID-md5deep/).
