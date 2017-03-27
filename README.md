# CCA Disk Image Processor  

Analyze disk images and/or create ready-to-ingest SIPs from a directory of disk images and related files.  

**NOTE: This tool is in dev and should not be considered production-ready without testing**

## Usage

Disk Image Processor has two modes: Analysis and Processing. Each mode can be run from the GUI interface or as a separate CLI utility by calling the underlying Python 3 script.  

### Analysis

Underlying script: `diskimageanalyzer.py`  

In Analysis mode, each disk image is scanned and reported on. When complete, an "analysis.csv" file is created containing the following information for each disk image:  

* Disk image name  
* File system  
* Date type used (modified, accessed, or created -- the tool uses the date set with the earliest "Date begin" date found in the DFXML file)  
* Date statement  
* Date begin  
* Date end  
* Extent  
* Virus found? (Boolean value)  
* File formats  

The destination directory also contains a "reports" directory containing a sub-directory for each disk image scanned. Each of these disk image sub-directories contains:  

* A DFXML file  
* Text output from "disktype"  
* Brunnhilde reports (including logs and reports from clamAV and bulk_extractor)  

### Processing

Underlying script: `diskimageprocessor.py`  

In Processing mode, each disk image is turned into a SIP, packaged as an ideal transfer to Archivematica's Automation tools, and reported on. When complete a "description.csv" spreadsheet is created, containing some pre-populated archival description:  
* Date statement  
* Date begin  
* Date end  
* Extent  
* Scope and content (containing information about the tool used to carve logical files and the most common file formats)

The destination directory also contains a log file and a "SIPs" directory containing a SIP created from each input disk image. Each SIP directory contains a metadata/checksum.md5 manifest by default, but may optionally be bagged instead. By default, the "objects" directory in each SIP contains both a copy of a raw disk image (regardless of whether the input was raw or E01) and logical files carved from the image by tsk_recover, unhfs, or a mount-and-copy routine, depending on the disk's file system. The user can choose to instead have SIPs include only logical files. The "metadata/submissionDocumentation" directory in each SIP contains:  

* A DFXML file  
* Text output from "disktype"  
* Brunnhilde reports (including logs and reports from clamAV and, optionally, bulk_extractor)  

## Installation

This utility is designed for easy use in Bitcurator v1.8.0+.  

### Install as part of CCA Tools  

Install all of the CCA Tools (and PyQT4) together using the install bash script in the [CCA Tools repo](https://github.com/timothyryanwalsh/cca-tools).  

### Install as a separate utlity
* Install [PyQt4](https://www.riverbankcomputing.com/software/pyqt/download):  
`sudo apt-get install python-qt4`  
* Clone this repo to your local machine.  
* Run the install script with sudo privileges:  
`sudo bash install.sh`  

After running the install script, either select "Disk Image Processor" from the "CCA Tools" directory on the Bitcurator desktop or use the CLI:  
`python /usr/share/ccatools/diskimageprocessor/diskimageprocessor.py` . 

## Credit  

Inspired by [Jess Whyte's work at the University of Toronto's Fisher Rare Book Library](https://saaers.wordpress.com/2016/04/12/clearing-the-digital-backlog-at-the-thomas-fisher-rare-book-library/comment-page-1/), especially the [Disk-ID-md5deep script](https://github.com/jesswhyte/Disk-ID-md5deep/).
