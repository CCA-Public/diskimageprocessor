# Installation Instructions

Note: these instructions assume you're installing Disk Image Processor on a fresh install of [BitCurator](https://wiki.bitcurator.net/index.php?title=Main_Page) v1.8.0+ 

### Prepping to Install:

##### 1. Install PyQT4:
`sudo apt-get install python-qt4` 

##### 2. Create /mnt/diskid

To process HFS and UDF disk images, create /mnt/diskid prior to use with `mkdir /mnt/diskid`)  

### Installing:

* ```sudo bash install.sh```
Thanks, install script :-)


### Running CCA Disk Image Processor:

##### GUI:
* Navigate to the Desktop -> CCA Tools folder
* Click the Disk Image Processor
* OR `python /usr/share/cca-diskimageprocessor/main.py`

##### CL:
The underlying script is `diskimageprocessor.py`. To have diskimageprocessor.py create bagged SIPs instead, pass the "-b" or "--bagfiles" argument. It will only export allocated files from non-HFS disks by default. To export all files, including deleted files and file segments residing in slack space, pass the "-e" or "--exportall" argument. To have Brunnhilde also complete a PII scan using bulk_extractor, pass the "-p" or "--piiscan" argument.

A command to export all files and create bagged SIPS would look like this:
```
python diskimageprocessor.py -b -e <source> <destination>
```

