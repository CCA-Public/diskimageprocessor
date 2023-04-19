#!/bin/bash

### Install script for CCA Disk Image Processor in Bitcurator 4/Ubuntu 22

if [ ! -d /usr/share/ccatools ]; then
  sudo mkdir /usr/share/ccatools
fi

dip_dir="/usr/share/ccatools/diskimageprocessor/"

if [ -d $dip_dir ]; then
  sudo rm -rf $dip_dir
fi

sudo mkdir $dip_dir

if [ ! -d /mnt/diskid ]; then
  sudo mkdir /mnt/diskid
fi

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

sudo cp disk_image_toolkit/dfxml/dfxml.py $dip_dir/disk_image_toolkit/dfxml/dfxml.py
sudo cp disk_image_toolkit/dfxml/objects.py $dip_dir/disk_image_toolkit/dfxml/objects.py
sudo cp disk_image_toolkit/dfxml/walk_to_dfxml.py $dip_dir/disk_image_toolkit/dfxml/walk_to_dfxml.py

# Create launch.desktop file
launch_file="/usr/share/applications/DiskImageProcessor.desktop"

if [ -f $launch_file ]; then
  sudo rm -rf $launch_file
fi

sudo touch $launch_file
echo '[Desktop Entry]' | sudo tee --append $launch_file
echo 'Type=Application' | sudo tee --append $launch_file
echo 'Name=Disk Image Processor' | sudo tee --append $launch_file
echo 'Exec=sudo /usr/share/ccatools/diskimageprocessor/launch' | sudo tee --append $launch_file
echo 'Icon=/usr/share/ccatools/diskimageprocessor/icon.png' | sudo tee --append $launch_file
echo 'Categories=Forensics and Reporting' | sudo tee --append $launch_file

sudo chown -R bcadmin:bcadmin $dip_dir
sudo chmod u+x /usr/share/ccatools/diskimageprocessor/launch
