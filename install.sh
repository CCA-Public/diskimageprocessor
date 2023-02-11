#!/bin/bash

### Install script for CCA Disk Image Processor in Bitcurator

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

# Make "CCA Tools" folder on Desktop if doesn't already exist
if [ ! -d "/home/bcadmin/Desktop/CCA Tools" ]; then
  sudo mkdir "/home/bcadmin/Desktop/CCA Tools"
fi

# Create launch.desktop file
sudo touch '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo '[Desktop Entry]' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo 'Type=Application' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo 'Name=Disk Image Processor' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo 'Exec=/usr/share/ccatools/diskimageprocessor/launch' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo 'Icon=/usr/share/ccatools/diskimageprocessor/icon.png' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'

# Change permissions, ownership for CCA Tools
sudo chown -R bcadmin:bcadmin '/home/bcadmin/Desktop/CCA Tools'
sudo chown -R bcadmin:bcadmin '/usr/share/ccatools/diskimageprocessor'
sudo find '/home/bcadmin/Desktop/CCA Tools' -type d -exec chmod 755 {} \;
sudo find '/home/bcadmin/Desktop/CCA Tools' -type f -exec chmod 644 {} \;

# Make files executable
sudo chmod u+x '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
sudo chmod u+x /usr/share/ccatools/diskimageprocessor/launch
