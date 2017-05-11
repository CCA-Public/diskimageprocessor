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
* Virus found (Boolean value)  
* File formats  

The destination directory also contains a "reports" directory containing a sub-directory for each disk image scanned. Each of these disk image sub-directories contains:  

* A DFXML file  
* Text output from "disktype"  
* Brunnhilde reports (including logs and reports from clamAV and bulk_extractor)  

Because "Analysis" mode runs bulk_extractor against each disk, this process can take a while.  

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

## Details

### Dates

CCA Disk Image Processor gathers dates from the DFXML files it generates, **not** from the file system. In practice, this means the dates reported in the CCA Disk Image Processor-generated spreadsheets and the dates shown in the file system for carved files may differ. 

The underlying logic is that files carved by tsk_recover may not retain their original MAC dates, but it is dates of creation and use prior to digital files' arrival at a collecting institution that we want to convey to end users of our archival description.

The utility compares dates created, modified, and accessed, and uses the set of dates with the earliest start date to populate the analysis/description spreadsheets. In "Analysis" mode, which set of dates is being used to generate date statements is made explicit. In "Processing" mode, it is not. The same logic applies for dates in both modes, so if you want to verify which set of dates are being used, simply run the same set of disk images in "Analysis" mode and refer to the resulting analysis.csv file.

## Installation

This utility is designed for easy use in BitCurator v1.8.0+. It requires Python 2.7 (to run the GUI) and Python 3.4+ (to run the scripts that analyze and process disk images), both of which are already included in BitCurator.    

### Install as part of CCA Tools  

Install all of the CCA Tools (and PyQT4) together using the install bash script in the [CCA Tools repo](https://github.com/timothyryanwalsh/cca-tools).  

### Install as a separate utility
* Clone this repo to your local machine.  
* Make install script executable (may need to be run with sudo privileges):  
`chmod u+x install.sh` 
* Run the install script with sudo privileges:  
`sudo ./install.sh`  

## Credit  

Inspired by [Jess Whyte's work at the University of Toronto's Fisher Rare Book Library](https://saaers.wordpress.com/2016/04/12/clearing-the-digital-backlog-at-the-thomas-fisher-rare-book-library/comment-page-1/), especially the [Disk-ID-md5deep script](https://github.com/jesswhyte/Disk-ID-md5deep/).
