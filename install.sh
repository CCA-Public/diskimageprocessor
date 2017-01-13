#!/bin/bash

### Install script for CCA Disk Image Processor in Bitcurator

# Make /usr/share/cca-diskimageprocessor if doesn't already exist
if [ ! -d /usr/share/cca-diskimageprocessor ]; then
  sudo mkdir /usr/share/cca-diskimageprocessor
fi

# Move files into /usr/share/cca-diskimageprocessor
sudo mv diskimageprocessor.py /usr/share/cca-diskimageprocessor
sudo mv main.py /usr/share/cca-diskimageprocessor
sudo mv launch /usr/share/cca-diskimageprocessor
sudo mv design.py /usr/share/cca-diskimageprocessor
sudo mv design.ui /usr/share/cca-diskimageprocessor
sudo mv icon.png /usr/share/cca-diskimageprocessor
sudo mv LICENSE /usr/share/cca-diskimageprocessor
sudo mv README.md /usr/share/cca-diskimageprocessor

# Make "CCA Tools" folder on Desktop if doesn't already exist
if [ ! -d "/home/bcadmin/Desktop/CCA Tools" ]; then
  sudo mkdir "/home/bcadmin/Desktop/CCA Tools"
fi

# Create launch.desktop file
sudo touch '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo '[Desktop Entry]' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo 'Type=Application' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo 'Name=Disk Image Processor' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo 'Exec=/usr/share/cca-tools/diskimageprocessor/launch' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
echo 'Icon=/usr/share/cca-tools/diskimageprocessor/icon.png' | sudo tee --append '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'

# Change permissions, ownership for CCA Tools
sudo chown -R bcadmin:bcadmin '/home/bcadmin/Desktop/CCA Tools'
sudo chown -R bcadmin:bcadmin '/usr/share/cca-diskimageprocessor'
sudo find '/home/bcadmin/Desktop/CCA Tools' -type d -exec chmod 755 {} \;
sudo find '/home/bcadmin/Desktop/CCA Tools' -type f -exec chmod 644 {} \;

# Make files executable
sudo chmod u+x '/home/bcadmin/Desktop/CCA Tools/Disk Image Processor.desktop'
sudo chmod u+x /usr/share/cca-diskimageprocessor/launch
