#!/bin/bash

### Install script for CCA Disk Image Processor in legacy Bitcurator 2/Ubuntu 18

# Make /usr/share/ccatools if doesn't already exist
if [ ! -d /usr/share/ccatools ]; then
  sudo mkdir /usr/share/ccatools
fi

dip_dir="/usr/share/ccatools/diskimageprocessor/"

# Delete /usr/share directory for Disk Image Processor if it already exists
if [ -d $dip_dir ]; then
  sudo rm -rf $dip_dir
fi

# Make /usr/share directory for Disk Image Processor
sudo mkdir $dip_dir

# Make /mnt/diskid/ if doesn't already exist
if [ ! -d /mnt/diskid ]; then
  sudo mkdir /mnt/diskid
fi

if [ -d $dip_dir/disk_image_toolkit/dfxml ]; then
  sudo rm -rf $dip_dir/disk_image_toolkit/dfxml
fi

sudo mkdir $dip_dir/disk_image_toolkit/
sudo mkdir $dip_dir/disk_image_toolkit/dfxml/

sudo cp diskimageprocessor.py $dip_dir
sudo cp diskimageanalyzer.py $dip_dir
sudo cp process_with_tsk_options.py $dip_dir
sudo cp main.py $dip_dir
sudo cp launch $dip_dir
sudo cp design.py $dip_dir
sudo cp design.ui $dip_dir
sudo cp icon.png $dip_dir
sudo cp LICENSE $dip_dir
sudo cp README.md $dip_dir
sudo cp -r disk_image_toolkit/ $dip_dir

if [ ! -d $dip_dir/disk_image_toolkit/dfxml ]; then
  sudo mkdir $dip_dir/disk_image_toolkit/dfxml/
fi

sudo cp disk_image_toolkit/dfxml/dfxml.py /usr/share/ccatools/diskimageprocessor/disk_image_toolkit/dfxml/
sudo cp disk_image_toolkit/dfxml/objects.py /usr/share/ccatools/diskimageprocessor/disk_image_toolkit/dfxml/
sudo cp disk_image_toolkit/dfxml/walk_to_dfxml.py /usr/share/ccatools/diskimageprocessor/disk_image_toolkit/dfxml/

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
