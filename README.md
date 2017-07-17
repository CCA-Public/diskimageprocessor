# CCA Disk Image Processor  

Analyze disk images and/or create ready-to-ingest SIPs from a directory of disk images and related files.  

**NOTE: This tool is in dev and should not be considered production-ready without testing**  
Version: 0.5.2 (beta)

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

## Supported disk image types  

* raw (dd, iso, img, etc.)  
* EnCase/EWF (E01)  

*Note: EnCase disk images are converted to raw disk images for processing using [libewf](https://github.com/libyal/libewf)'s `ewf_export` utility. In Processing mode, the converted raw image is retained in the SIP unless the user selects to retain only logical files.*

## Disk image extensions recognized

Disk Image Processor recognizes which files are disk images by their file extensions. Currently, it looks for the following extensions:  

* .E01  
* .000  
* .001  
* .raw  
* .img  
* .dd  
* .iso  

*To add extensions to this list, add them as elements in the tuple inside `file.endswith((".E01", ".000", ".001", ".raw", ".img", ".dd", ".iso"))` on line 369 of `diskimageprocessor.py` and/or line 276 of `diskimageanalyzer.py`.*

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

### Brunnhilde version  

Disk Image Processor will work with all versions of [Brunnhilde](https://github.com/timothyryanwalsh/brunnhilde); however, changes to Brunnhilde 1.5.1's default pattern matching for SSNs with bulk_extractor help in minimizing the number of false positives reported and keeping the Brunnhilde HTML report size reasonable. For best results, it is recommended to upgrade the version of Brunnhilde on your machine to 1.5.1+.  

## Credit  

Inspired by [Jess Whyte's work at the University of Toronto's Fisher Rare Book Library](https://saaers.wordpress.com/2016/04/12/clearing-the-digital-backlog-at-the-thomas-fisher-rare-book-library/comment-page-1/), especially the [Disk-ID-md5deep script](https://github.com/jesswhyte/Disk-ID-md5deep/).
