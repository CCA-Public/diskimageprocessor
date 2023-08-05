#!/bin/bash

### Test install script for CCA Disk Image Processor

# Make /usr/share/ccatools if doesn't already exist
if [ ! -d /usr/share/ccatools ]; then
  sudo mkdir /usr/share/ccatools
fi

# Delete /usr/share directory for Disk Image Processor if it already exists
if [ -d /usr/share/ccatools/diskimageprocessor ]; then
  sudo rm -rf /usr/share/ccatools/diskimageprocessor
fi

# Make /usr/share directory for Disk Image Processor
sudo mkdir /usr/share/ccatools/diskimageprocessor

# Make /mnt/diskid/ if doesn't already exist
if [ ! -d /mnt/diskid ]; then
  sudo mkdir /mnt/diskid
fi

# Move files into /usr/share/ccatools/diskimageprocessor
sudo cp diskimageprocessor.py /usr/share/ccatools/diskimageprocessor
sudo cp diskimageanalyzer.py /usr/share/ccatools/diskimageprocessor
sudo cp process_with_tsk_options.py /usr/share/ccatools/diskimageprocessor
sudo cp main.py /usr/share/ccatools/diskimageprocessor
sudo cp launch /usr/share/ccatools/diskimageprocessor
sudo cp design.py /usr/share/ccatools/diskimageprocessor
sudo cp design.ui /usr/share/ccatools/diskimageprocessor
sudo cp icon.png /usr/share/ccatools/diskimageprocessor
sudo cp LICENSE /usr/share/ccatools/diskimageprocessor
sudo cp README.md /usr/share/ccatools/diskimageprocessor
sudo cp disk_image_toolkit/dfxml/dfxml.py /usr/share/ccatools/diskimageprocessor
sudo cp disk_image_toolkit/dfxml/objects.py /usr/share/ccatools/diskimageprocessor
sudo cp disk_image_toolkit/dfxml/walk_to_dfxml.py /usr/share/ccatools/diskimageprocessor

if [ ! -d /usr/share/ccatools/diskimageprocessor/aspace_template ]; then
  sudo mkdir /usr/share/ccatools/diskimageprocessor/aspace_template
fi
sudo cp aspace_template/aspace_import_template.xlsx /usr/share/ccatools/diskimageprocessor/aspace_template

sudo cp disk_image_toolkit/dfxml/dfxml.py .
sudo cp disk_image_toolkit/dfxml/objects.py .
sudo cp disk_image_toolkit/dfxml/walk_to_dfxml.py .
