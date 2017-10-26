# encoding: utf-8

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

    def test_integration_outputs_created_tsk(self):
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
            'diskimageprocessor-log.txt')))
        
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

        # metadata
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata')))
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation')))
        self.assertTrue(os.path.isdir(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation', 'brunnhilde')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation', 'dfxml.xml')))
        self.assertTrue(is_non_zero_file(j(out_dir, 'SIPs', 
            'practical.floppy.dd', 'metadata', 
            'submissionDocumentation', 'disktype.txt')))


if __name__ == '__main__':
    unittest.main()