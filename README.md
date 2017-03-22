Creates ready-to-ingest SIPs from a directory of disk images and related files.  

**NOTE: This tool is in dev and should not be considered production-ready without testing**

![flowchart](https://github.com/timothyryanwalsh/cca-diskimageprocessor/blob/master/media/di_flowchart.png)  

**GUI:**  

![gui](https://github.com/timothyryanwalsh/cca-diskimageprocessor/blob/master/media/diskimageprocessor_gui.png)  

**Outputs:**  

*Top-level output*:  

![all_sips](https://github.com/timothyryanwalsh/cca-diskimageprocessor/blob/master/media/diskimageprocessor_output1.png)  

*Spreadsheet*:  

![spreadsheet](https://github.com/timothyryanwalsh/cca-diskimageprocessor/blob/master/media/desc_spreadsheet.png)  

*Each processed SIP (default behavior, not bagged)*:  

![one_sip](https://github.com/timothyryanwalsh/cca-diskimageprocessor/blob/master/media/diskimageprocessor_output.png)  

Inspired by [Jess Whyte's work at the University of Toronto's Fisher Rare Book Library](https://saaers.wordpress.com/2016/04/12/clearing-the-digital-backlog-at-the-thomas-fisher-rare-book-library/comment-page-1/), especially the [Disk-ID-md5deep script](https://github.com/jesswhyte/Disk-ID-md5deep/).

### Installation  

This utility is designed for easy use in Bitcurator, and in v1.8.0+ requires installation of only [PyQT4](https://www.riverbankcomputing.com/software/pyqt/download): 
`sudo apt-get install python-qt4`  

Alternatively, install all of the CCA Tools (and PyQT4) using the install script in the [CCA Tools repo](https://github.com/timothyryanwalsh/cca-tools).  

After running the install script, either select "Disk Image Processor" from the "CCA Tools" directory on the Bitcurator desktop or use the CLI:  
`python /usr/share/ccatools/diskimageprocessor/diskimageprocessor.py` . 
