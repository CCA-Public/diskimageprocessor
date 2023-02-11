import bagit
import os
import shutil
import subprocess
import tempfile
import unittest
from os.path import join as j

TEST_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
TSK_FIXTURE_PATH = j(TEST_FILE_DIR, "fixtures", "fat12")
TSK_VOLUME_NAME = "volume-1-fat12"

# TODO: Add tests with new HFS and ISO-HFS fixtures


def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


class SelfCleaningTestCase(unittest.TestCase):
    """TestCase subclass which cleans up self.tmpdir after each test"""

    def setUp(self):
        super(SelfCleaningTestCase, self).setUp()

        self.dest_tmpdir = tempfile.mkdtemp()
        if not os.path.isdir(self.dest_tmpdir):
            os.mkdirs(self.dest_tmpdir)

    def tearDown(self):
        if os.path.isdir(self.dest_tmpdir):
            shutil.rmtree(self.dest_tmpdir)

        super(SelfCleaningTestCase, self).tearDown()


class TestDiskImageProcessorIntegration(SelfCleaningTestCase):
    """Integration tests for diskimageprocessor.py."""

    def setUp(self):
        super(TestDiskImageProcessorIntegration, self).setUp()

        self.SCRIPT_PATH = j(TEST_FILE_DIR, "..", "diskimageprocessor.py")
        self.OUTPUT_DIR = j(self.dest_tmpdir, "test")
        self.DISK_IMAGE_NAME = "practical.floppy.dd"

        self.DESCRIPTION_CSV = j(self.OUTPUT_DIR, "description.csv")
        self.LOG_FILE = j(self.OUTPUT_DIR, "diskimageprocessor.log")
        self.SIPS_DIR = j(self.OUTPUT_DIR, "SIPs")
        self.SIP_DIR = j(self.SIPS_DIR, self.DISK_IMAGE_NAME)
        self.OBJECTS_DIR = j(self.SIP_DIR, "objects")
        self.DISK_IMAGE_DIR = j(self.OBJECTS_DIR, "diskimage")
        self.FILES_DIR = j(self.OBJECTS_DIR, "files")
        self.METADATA_DIR = j(self.SIP_DIR, "metadata")
        self.SUBDOC_DIR = j(self.METADATA_DIR, "submissionDocumentation")
        self.BRUNNHILDE_DIR = j(self.SUBDOC_DIR, "brunnhilde")
        self.BULK_EXTRACTOR_DIR = j(self.BRUNNHILDE_DIR, "bulk_extractor")

        self.CHECKSUM_MANIFEST = j(self.METADATA_DIR, "checksum.md5")
        self.BRUNNHILDE_REPORT = j(self.BRUNNHILDE_DIR, "report.html")
        self.DFXML_FILE = j(self.SUBDOC_DIR, "dfxml.xml")
        self.DISKTYPE_FILE = j(self.SUBDOC_DIR, "disktype.txt")
        self.BULK_EXTRACTOR_REPORT = j(self.BULK_EXTRACTOR_DIR, "report.xml")

        self.DISK_IMAGE_IN_SIP = j(self.DISK_IMAGE_DIR, self.DISK_IMAGE_NAME)
        self.ALLOCATED_FILE = j(self.FILES_DIR, TSK_VOLUME_NAME, "ARP.EXE")
        self.UNALLOCATED_FILE = j(
            self.FILES_DIR, TSK_VOLUME_NAME, "Docs", "Private", "ReyHalif.doc"
        )
        self.ALLOCATED_FILE_OBJECTS = j(self.OBJECTS_DIR, TSK_VOLUME_NAME, "ARP.EXE")

    def test_integration_processing_tsk(self):
        """End-to-end test using sleuthkit to process disk image."""
        subprocess.call(
            "python {} {} {}".format(
                self.SCRIPT_PATH, TSK_FIXTURE_PATH, self.OUTPUT_DIR
            ),
            shell=True,
        )

        self.assertTrue(is_non_zero_file(j(TSK_FIXTURE_PATH, "practical.floppy.dd")))

        self.assertTrue(is_non_zero_file(self.DESCRIPTION_CSV))
        self.assertTrue(is_non_zero_file(self.LOG_FILE))

        self.assertTrue(os.path.isdir(self.SIPS_DIR))
        self.assertTrue(os.path.isdir(self.SIP_DIR))

        self.assertTrue(os.path.isdir(self.OBJECTS_DIR))
        self.assertTrue(os.path.isdir(self.DISK_IMAGE_DIR))
        self.assertTrue(is_non_zero_file(self.DISK_IMAGE_IN_SIP))
        self.assertTrue(os.path.isdir(self.FILES_DIR))

        self.assertTrue(is_non_zero_file(self.ALLOCATED_FILE))
        self.assertFalse(is_non_zero_file(self.UNALLOCATED_FILE))

        self.assertTrue(os.path.isdir(self.METADATA_DIR))
        self.assertTrue(is_non_zero_file(self.CHECKSUM_MANIFEST))
        self.assertTrue(os.path.isdir(self.SUBDOC_DIR))

        self.assertTrue(os.path.isdir(self.BRUNNHILDE_DIR))
        self.assertTrue(is_non_zero_file(self.BRUNNHILDE_REPORT))
        self.assertTrue(is_non_zero_file(self.DISKTYPE_FILE))
        self.assertTrue(is_non_zero_file(self.DFXML_FILE))

    def test_integration_processing_bag(self):
        """Test packaging of SIPs as a BagIt bag."""
        subprocess.call(
            "python {} -b {} {}".format(
                self.SCRIPT_PATH, TSK_FIXTURE_PATH, self.OUTPUT_DIR
            ),
            shell=True,
        )
        bag = bagit.Bag(self.SIP_DIR)
        self.assertTrue(bag.validate())

    def test_integration_processing_bulk_extractor(self):
        """Test running of bulk_extractor via brunnhilde."""
        subprocess.call(
            "python {} -p {} {}".format(
                self.SCRIPT_PATH, TSK_FIXTURE_PATH, self.OUTPUT_DIR
            ),
            shell=True,
        )
        self.assertTrue(os.path.isdir(self.BULK_EXTRACTOR_DIR))
        self.assertTrue(is_non_zero_file(self.BULK_EXTRACTOR_REPORT))

    def test_integration_processing_filesonly(self):
        """Test retaining carved logical files only in the SIP."""
        subprocess.call(
            "python {} -f {} {}".format(
                self.SCRIPT_PATH, TSK_FIXTURE_PATH, self.OUTPUT_DIR
            ),
            shell=True,
        )
        self.assertFalse(os.path.isdir(self.DISK_IMAGE_DIR))
        self.assertTrue(is_non_zero_file(self.ALLOCATED_FILE_OBJECTS))

    def test_integration_processing_exportall(self):
        """Test extracting allocated and unallocated files."""
        subprocess.call(
            "python {} -e {} {}".format(
                self.SCRIPT_PATH, TSK_FIXTURE_PATH, self.OUTPUT_DIR
            ),
            shell=True,
        )
        self.assertTrue(is_non_zero_file(self.UNALLOCATED_FILE))


class TestDiskImageAnalyzerIntegration(SelfCleaningTestCase):
    """Integration tests for diskimageanalyzer.py."""

    def setUp(self):
        super(TestDiskImageAnalyzerIntegration, self).setUp()

        self.SCRIPT_PATH = j(TEST_FILE_DIR, "..", "diskimageanalyzer.py")
        self.OUTPUT_DIR = j(self.dest_tmpdir, "test")
        self.DISK_IMAGE_NAME = "practical.floppy.dd"

        self.ANALYSIS_CSV = j(self.OUTPUT_DIR, "analysis.csv")
        self.REPORTS_DIR = j(self.OUTPUT_DIR, "reports")
        self.FILES_DIR = j(self.OUTPUT_DIR, "files")

        self.DISK_IMAGE_REPORTS_DIR = j(self.REPORTS_DIR, self.DISK_IMAGE_NAME)
        self.BRUNNHILDE_DIR = j(self.DISK_IMAGE_REPORTS_DIR, "brunnhilde")
        self.BRUNNHILDE_REPORT = j(self.BRUNNHILDE_DIR, "report.html")
        self.DFXML_FILE = j(self.DISK_IMAGE_REPORTS_DIR, "dfxml.xml")
        self.DISKTYPE_FILE = j(self.DISK_IMAGE_REPORTS_DIR, "disktype.txt")

        self.DISK_IMAGE_FILES_DIR = j(self.FILES_DIR, self.DISK_IMAGE_NAME)
        self.ALLOCATED_FILE = j(self.DISK_IMAGE_FILES_DIR, TSK_VOLUME_NAME, "ARP.EXE")
        self.UNALLOCATED_FILE = j(
            self.DISK_IMAGE_FILES_DIR,
            TSK_VOLUME_NAME,
            "Docs",
            "Private",
            "ReyHalif.doc",
        )

    def test_integration_analysis_tsk(self):
        """End-to-end test using sleuthkit to analyze disk image."""
        subprocess.call(
            "python {} {} {}".format(
                self.SCRIPT_PATH, TSK_FIXTURE_PATH, self.OUTPUT_DIR
            ),
            shell=True,
        )

        self.assertTrue(is_non_zero_file(self.ANALYSIS_CSV))

        self.assertTrue(os.path.isdir(self.REPORTS_DIR))
        self.assertFalse(os.path.isdir(self.FILES_DIR))

        self.assertTrue(os.path.isdir(self.BRUNNHILDE_DIR))
        self.assertTrue(is_non_zero_file(self.BRUNNHILDE_REPORT))

        self.assertTrue(is_non_zero_file(self.DISKTYPE_FILE))
        self.assertTrue(is_non_zero_file(self.DFXML_FILE))

    def test_integration_analysis_keepfiles(self):
        """Test option to retain carved files."""
        subprocess.call(
            "python {} -k {} {}".format(
                self.SCRIPT_PATH, TSK_FIXTURE_PATH, self.OUTPUT_DIR
            ),
            shell=True,
        )

        self.assertTrue(os.path.isdir(self.FILES_DIR))
        self.assertTrue(is_non_zero_file(self.ALLOCATED_FILE))
        self.assertFalse(is_non_zero_file(self.UNALLOCATED_FILE))

    def test_integration_analysis_exportall(self):
        """Test extracting allocated and unallocated files."""
        subprocess.call(
            "python {} -ek {} {}".format(
                self.SCRIPT_PATH, TSK_FIXTURE_PATH, self.OUTPUT_DIR
            ),
            shell=True,
        )

        self.assertTrue(os.path.isdir(self.FILES_DIR))
        self.assertTrue(is_non_zero_file(self.ALLOCATED_FILE))
        self.assertTrue(is_non_zero_file(self.UNALLOCATED_FILE))


if __name__ == "__main__":
    unittest.main()
