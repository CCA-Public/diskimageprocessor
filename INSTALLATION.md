# Installation Instructions

Note: these instructions assume you're installing Disk Image Processor on a fresh install of [BitCurator](https://wiki.bitcurator.net/index.php?title=Main_Page) VM v1.7.102.  

### Prepping to Install:

##### 1. Install an updated version of [SIP](https://riverbankcomputing.com/software/sip/intro)

You can try `pip install SIP` or `pip3 install SIP`, but if those are out of date (you need at least SIP 4.19), you will need to...

* Visit <https://riverbankcomputing.com/software/sip/download>. 
* Copy the download link for the Linux source tar.gz
* `wget <copied link>`
* `tar -xzvf <filename>`
* `cd sip-4.19` 
* `python configure.py`
* `make`
* `make install` (may have to do as sudo)

##### 2. Install [PyQt4](http://pyqt.sourceforge.net/Docs/PyQt4/installation.html) (if you plan on using the GUI)

First, install Qt4: `sudo apt-get install qt4-default`
Then, install PyQt4... 
* Visit <https://riverbankcomputing.com/software/pyqt/download>
* Copy the download link for the Linux source tar.gz
* `wget <copied link>`
* `tar -xzvf <filename>`
* `cd PyQt4_gpl_x11-4.12`
* `python configure-ng.py`
* `make`
* `make install` (may have to do as sudo)
	
##### 3. Install [brunnhilde](https://github.com/timothyryanwalsh/brunnhilde) 
Brunnhilde generates aggregate reports of files in a directory or disk image based on input from Siegfried. Disk Image Processor will run without it, but the reporting capacity will be limited. 
* Get [Siegfried](https://github.com/richardlehane/siegfried/wiki/Getting-started) *(not going to lie, this might be a bit bumpy, but it should work)*
```
wget -qO - https://bintray.com/user/downloadSubjectPublicKey?username=bintray | sudo apt-key add -
echo "deb http://dl.bintray.com/siegfried/debian wheezy main" | sudo tee -a /etc/apt/sources.list
sudo apt-get update && sudo apt-get install siegfried
```

* Install brunnhilde `pip install brunnhilde`
	
##### 4. Create /mnt/diskid

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
The underlying script is `diskimageprocessor.py`. To have diskimageprocessor.py create bagged SIPs instead, pass the "-b" or "--bagfiles" argument. It will only export allocated files from non-HFS disks by default. To export all files, including deleted files and file segments residing in slack space, pass the "-e" or "--exportall" argument. To have Brunnhilde also complete a PII scan using bulk_extractor, pass the "-p" or "-piiscan" argument.

A command to export all files and create bagged SIPS would look like this:
```
python diskimageprocessor.py -b -e <source> <destination>
```

