#!/bin/bash

### Install script for CCA Disk Image Processor in Bitcurator

# Make /usr/share/ccatools if doesn't already exist
if [ ! -d /usr/share/ccatools ]; then
  sudo mkdir /usr/share/ccatools
fi

# Make disk image processor folder if doesn't already exist
if [ ! -d /usr/share/ccatools/diskimageprocessor ]; then
  sudo mkdir /usr/share/ccatools/diskimageprocessor
fi

# Make /mnt/diskid/ if doesn't already exist
if [ ! -d /mnt/diskid ]; then
  sudo mkdir /mnt/diskid
fi


# Move files into /usr/share/ccatools/diskimageprocessor
sudo mv diskimageprocessor.py /usr/share/ccatools/diskimageprocessor
sudo mv diskimageanalyzer.py /usr/share/ccatools/diskimageprocessor
sudo mv process_with_tsk_options.py /usr/share/ccatools/diskimageprocessor
sudo mv main.py /usr/share/ccatools/diskimageprocessor
sudo mv launch /usr/share/ccatools/diskimageprocessor
sudo mv design.py /usr/share/ccatools/diskimageprocessor
sudo mv design.ui /usr/share/ccatools/diskimageprocessor
sudo mv icon.png /usr/share/ccatools/diskimageprocessor
sudo mv LICENSE /usr/share/ccatools/diskimageprocessor
sudo mv README.md /usr/share/ccatools/diskimageprocessor

# Check for DFXML libraries
if [ ! -d /usr/share/dfxml/python ]; then
  git submodule update --init --recursive
  sudo mv deps/ /usr/share/ccatools/diskimageprocessor
  sudo mv dfxml.py /usr/share/ccatools/diskimageprocessor
  sudo mv Objects.py /usr/share/ccatools/diskimageprocessor
  sudo mv walk_to_dfxml.py /usr/share/ccatools/diskimageprocessor

# Else use existing libraries
else
  sudo ln -s /usr/share/dfxml/python/dfxml.py /usr/share/ccatools/diskimageprocessor/dfxml.py
  sudo ln -s /usr/share/dfxml/python/Objects.py /usr/share/ccatools/diskimageprocessor/Objects.py
  sudo ln -s /usr/share/dfxml/python/walk_to_dfxml.py /usr/share/ccatools/diskimageprocessor/walk_to_dfxml.py
fi


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
