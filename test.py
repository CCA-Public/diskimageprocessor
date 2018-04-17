# encoding: utf-8

import bagit
import datetime
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from os.path import join as j


logging.basicConfig(filename='test.log', level=logging.DEBUG)
stderr = logging.StreamHandler()
stderr.setLevel(logging.WARNING)
logging.getLogger().addHandler(stderr)

def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


class SelfCleaningTestCase(unittest.TestCase):
    """TestCase subclass which cleans up self.tmpdir after each test"""

    def setUp(self):
        super(SelfCleaningTestCase, self).setUp()

        # tempdir for brunnhilde outputs
        self.dest_tmpdir = tempfile.mkdtemp()
        if not os.path.isdir(self.dest_tmpdir):
            os.mkdirs(self.dest_tmpdir)

    def tearDown(self):
        if os.path.isdir(self.dest_tmpdir):
            shutil.rmtree(self.dest_tmpdir)

        super(SelfCleaningTestCase, self).tearDown()


class TestDiskImageProcessorIntegration(SelfCleaningTestCase):
    """
    Integration tests for diskimageprocessor.py.
    """

    def test_integration_processing_tsk(self):
        # run diskimageprocessor.py
        script = '/usr/share/ccatools/diskimageprocessor/diskimageprocessor.py'
        img_source = './test-data/tsk'
        out_dir = j(self.dest_tmpdir, 'test')
        subprocess.call("python {} {} {}".format(script, img_source, out_dir), 
            shell=True)

        # outputs
        self.assertTrue(is_non_zero_file(j(out_dir, 
            'description.csv')))
        self.assertTrue(is_non_zero_file(j(out_dir, 
            'diskimageprocessor.log')))
        
        # SIP dir
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs')))
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd')))

        # objects
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'objects')))
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'objects', 'diskimage')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'objects', 'diskimage', 
            'practical.floppy.dd')))
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'objects', 'files')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'objects', 'files', 'ARP.EXE')))

        # verify deleted file not exported
        self.assertFalse(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'objects', 'files', 
            'Docs', 'Private', 'ReyHalif.doc')))

        # metadata
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 'checksum.md5')))
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation')))
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation', 'brunnhilde')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation', 'brunnhilde', 
            'brunnhilde.html')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation', 'dfxml.xml')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation', 'disktype.txt')))

    def test_integration_processing_bag(self):
        # run diskimageprocessor.py
        script = '/usr/share/ccatools/diskimageprocessor/diskimageprocessor.py'
        img_source = './test-data/tsk'
        out_dir = j(self.dest_tmpdir, 'test')
        subprocess.call("python {} -b {} {}".format(script, img_source, out_dir), 
            shell=True)

        # validate bag
        bag = bagit.Bag(j(out_dir, 'SIPs', 'practical.floppy.dd'))
        self.assertTrue(bag.validate())

    def test_integration_processing_bulk_extractor(self):
        # run diskimageprocessor.py
        script = '/usr/share/ccatools/diskimageprocessor/diskimageprocessor.py'
        img_source = './test-data/tsk'
        out_dir = j(self.dest_tmpdir, 'test')
        subprocess.call("python {} -p {} {}".format(script, img_source, out_dir), 
            shell=True)

        # check for bulk_extractor outputs
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation', 'brunnhilde', 
            'bulk_extractor')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation', 'brunnhilde', 
            'bulk_extractor', 'report.xml')))

    def test_integration_processing_filesonly(self):
        # run diskimageprocessor.py
        script = '/usr/share/ccatools/diskimageprocessor/diskimageprocessor.py'
        img_source = './test-data/tsk'
        out_dir = j(self.dest_tmpdir, 'test')
        subprocess.call("python {} -f {} {}".format(script, img_source, out_dir), 
            shell=True)

        # verify diskimage dir doesn't exist
        self.assertFalse(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'objects', 'diskimage')))

        # verify files exist in objects dir
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'objects', 'ARP.EXE')))

    def test_integration_processing_exportall(self):
        # run diskimageprocessor.py
        script = '/usr/share/ccatools/diskimageprocessor/diskimageprocessor.py'
        img_source = './test-data/tsk'
        out_dir = j(self.dest_tmpdir, 'test')
        subprocess.call("python {} -e {} {}".format(script, img_source, out_dir), 
            shell=True)

        # verify deleted file exported from disk image
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'objects', 'files', 
            'Docs', 'Private', 'ReyHalif.doc')))

    def test_integration_analysis_tsk(self):
        # run diskimageprocessor.py
        script = '/usr/share/ccatools/diskimageprocessor/diskimageanalyzer.py'
        img_source = './test-data/tsk'
        out_dir = j(self.dest_tmpdir, 'test')
        subprocess.call("python {} {} {}".format(script, img_source, out_dir), 
            shell=True)

        # analysis csv
        self.assertTrue(is_non_zero_file(j(out_dir, 
            'analysis.csv')))
        
        # directories
        self.assertTrue(os.path.isdir(j(out_dir, 'reports')))
        self.assertFalse(os.path.isdir(j(out_dir, 'files')))

        # reports
        self.assertTrue(is_non_zero_file(j(out_dir, 'reports', 
            'practical.floppy.dd', 'dfxml.xml')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'reports', 
            'practical.floppy.dd', 'disktype.txt')))
        self.assertTrue(os.path.isdir(j(out_dir, 'reports', 
            'practical.floppy.dd', 'brunnhilde')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'reports', 
            'practical.floppy.dd', 'brunnhilde', 'brunnhilde.html')))

    def test_integration_analysis_keepfiles(self):
        # run diskimageprocessor.py
        script = '/usr/share/ccatools/diskimageprocessor/diskimageanalyzer.py'
        img_source = './test-data/tsk'
        out_dir = j(self.dest_tmpdir, 'test')
        subprocess.call("python {} -k {} {}".format(script, img_source, out_dir), 
            shell=True)

        # outputs
        self.assertTrue(os.path.isdir(j(out_dir, 'files')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'files', 
            'practical.floppy.dd', 'ARP.EXE')))

        # verify deleted file not exported
        self.assertFalse(is_non_zero_file(j(out_dir, 'files', 
            'practical.floppy.dd', 'Docs', 'Private', 
            'ReyHalif.doc')))

    def test_integration_analysis_exportall(self):
        # run diskimageprocessor.py
        script = '/usr/share/ccatools/diskimageprocessor/diskimageanalyzer.py'
        img_source = './test-data/tsk'
        out_dir = j(self.dest_tmpdir, 'test')
        subprocess.call("python {} -ek {} {}".format(script, img_source, out_dir), 
            shell=True)

        # verify deleted file exported
        self.assertTrue(is_non_zero_file(j(out_dir, 'files', 
            'practical.floppy.dd', 'Docs', 'Private', 
            'ReyHalif.doc')))


if __name__ == '__main__':
    unittest.main()