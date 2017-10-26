#!/bin/bash

### Install script for Travis CI

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