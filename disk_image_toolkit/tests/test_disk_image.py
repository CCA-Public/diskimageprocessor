"""DiskImage class unit tests."""
import os
import pytest
import subprocess

from disk_image_toolkit.dfxml import objects

from disk_image_toolkit import DiskImage
from disk_image_toolkit.exception import DiskImageError

TEST_FIXTURES_DIR = os.path.abspath(os.path.join(__file__, "../../../tests/fixtures"))

DISK_IMAGE_FAT_12 = os.path.join(TEST_FIXTURES_DIR, "fat12", "practical.floppy.dd")
DISK_IMAGE_HFS = os.path.join(TEST_FIXTURES_DIR, "hfs", "hfs-example.dd")
DISK_IMAGE_ISO_HFS_DUAL = os.path.join(
    TEST_FIXTURES_DIR, "iso-hfs-dual", "iso9660_hfs.iso"
)
DISK_IMAGE = DISK_IMAGE_FAT_12

DFXML_FIXTURE = os.path.join(TEST_FIXTURES_DIR, "dfxml", "fat12.xml")


def test_call_subprocess(mocker):
    check_output = mocker.patch("subprocess.check_output")
    TEST_COMMAND = ["test-command", "--arg", "value"]

    disk_image = DiskImage(DISK_IMAGE)
    disk_image._call_subprocess(TEST_COMMAND, "error message", cwd="some/dir")
    check_output.assert_called_with(TEST_COMMAND, cwd="some/dir")


def test_call_subprocess_raises(mocker):
    disk_image = DiskImage(DISK_IMAGE)

    with pytest.raises(Exception):
        subprocess_call = mocker.patch("subprocess.check_output")
        subprocess_call.side_effect = Exception("subprocess.CalledProcessError")
        disk_image._call_subprocess(["test-command"])


def test_convert_to_raw_ewf(mocker):
    """Test method calls to convert EWF disk image."""
    is_ewf = mocker.patch("disk_image_toolkit.disk_image.DiskImage.is_ewf")
    is_ewf.return_value = True

    ewfexport = mocker.patch("disk_image_toolkit.disk_image.DiskImage._call_subprocess")
    rename = mocker.patch("os.rename")

    DESTINATION_PATH = "/path/to/practical.floppy.dd"
    disk_image_path = os.path.join(TEST_FIXTURES_DIR, "fat12", "practical.floppy.ewf")
    disk_image = DiskImage(disk_image_path)
    return_value = disk_image.convert_to_raw(destination_path=DESTINATION_PATH)

    assert ewfexport.call_count == 1
    assert rename.call_count == 2
    assert return_value == DESTINATION_PATH


def test_convert_to_raw_already_raw():
    """Test method returns input path if disk image is already raw."""
    disk_image = DiskImage(DISK_IMAGE)
    return_value = disk_image.convert_to_raw()
    assert return_value == DISK_IMAGE
    assert disk_image.raw_disk_image == DISK_IMAGE


def test_run_disktype(mocker, tmp_path):
    """Test method calls subprocess and returns as expected."""
    DISKTYPE_OUTPUT = b"fake disktype output\n"
    disktype_call = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage._call_subprocess"
    )
    disktype_call.return_value = DISKTYPE_OUTPUT

    tmp_output_file = tmp_path / "disktype.txt"

    disk_image = DiskImage(DISK_IMAGE)
    return_value = disk_image.run_disktype(output_file=tmp_output_file)

    assert return_value == DISKTYPE_OUTPUT
    assert disk_image.disktype == DISKTYPE_OUTPUT

    # Test output was written identically to file.
    with open(tmp_output_file, "rb") as f:
        disk_image.disktype == f.read()


@pytest.mark.parametrize(
    "disk_image_path, disktype_path, expected_volumes_return",
    [
        # HFS formatted disk image
        (
            DISK_IMAGE_HFS,
            os.path.join(TEST_FIXTURES_DIR, "hfs/disktype.txt"),
            [
                {
                    "id": 1,
                    "file_system": "HFS",
                    "name": "ok_images + rome2",
                    "formatted_name": "ok_images__rome2",
                    "output_directory_name": "volume-1-hfs-ok_images__rome2",
                    "size": "95.74 MiB (100392960 bytes, 65360 blocks of 1536 bytes)",
                }
            ],
        ),
        # ISO 9660-HFS dual formatted disk image
        (
            DISK_IMAGE_ISO_HFS_DUAL,
            os.path.join(TEST_FIXTURES_DIR, "iso-hfs-dual/disktype.txt"),
            [
                {
                    "id": 1,
                    "file_system": "HFS",
                    "name": "ISO9660/HFS",
                    "formatted_name": "ISO9660HFS",
                    "output_directory_name": "volume-1-hfs-ISO9660HFS",
                    "size": "880 KiB (901120 bytes, 440 blocks of 2 KiB)",
                },
                {
                    "id": 2,
                    "file_system": "ISO9660",
                    "name": "ISO9660/HFS",
                    "formatted_name": "ISO9660HFS",
                    "output_directory_name": "volume-2-iso9660-ISO9660HFS",
                },
            ],
        ),
        # FAT12 formatted disk image
        (
            DISK_IMAGE,
            os.path.join(TEST_FIXTURES_DIR, "fat12/disktype.txt"),
            [
                {
                    "id": 1,
                    "file_system": "FAT12",
                    "name": "",
                    "formatted_name": "",
                    "output_directory_name": "volume-1-fat12",
                    "size": "1.390 MiB (1457664 bytes, 2847 clusters of 512 bytes)",
                }
            ],
        ),
    ],
)
def test_carve_files_from_all_volumes(
    mocker, disk_image_path, disktype_path, expected_volumes_return
):
    """Confirm disktype.txt parses volumes as expected to carve files."""
    mocker.patch("os.makedirs")
    mocker.patch("disk_image_toolkit.disk_image.DiskImage.write_dfxml_with_fiwalk")
    carve_files = mocker.patch("disk_image_toolkit.disk_image.DiskImage.carve_files")

    disk_image = DiskImage(disk_image_path)
    with open(disktype_path, "r") as disktype_file:
        disk_image.disktype = disktype_file.read()

    return_value = disk_image.carve_files_from_all_volumes()
    assert return_value == expected_volumes_return
    assert carve_files.call_count == len(expected_volumes_return)


@pytest.mark.parametrize(
    "file_system, tsk_call_count, hfs_call_count, mount_copy_call_count",
    [
        # tsk_recover-supported file systems
        ("fat", 1, 0, 0),
        ("fat12", 1, 0, 0),
        ("FAT", 1, 0, 0),
        ("FAT32", 1, 0, 0),
        ("NTFS", 1, 0, 0),
        ("ISO9660", 1, 0, 0),
        ("hfs+", 1, 0, 0),
        # HFS file system
        ("HFS", 0, 1, 0),
        ("hfs", 0, 1, 0),
        # UDF file system
        ("udf", 0, 0, 1),
        ("UDF", 0, 0, 1),
        # unsupported file systems
        ("not-real", 0, 0, 0),
        ("", 0, 0, 0),
    ],
)
def test_carve_files(
    mocker, file_system, tsk_call_count, hfs_call_count, mount_copy_call_count
):
    """Test that correct subfunction is called depending on file system."""
    tsk_recover = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage.carve_files_with_tsk_recover"
    )
    hfs_explorer = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage.carve_files_with_hfs_explorer"
    )
    mount_copy = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage.mount_disk_image_and_copy_files"
    )

    disk_image = DiskImage(DISK_IMAGE)
    disk_image.carve_files(file_system)

    assert tsk_recover.call_count == tsk_call_count
    assert hfs_explorer.call_count == hfs_call_count
    assert mount_copy.call_count == mount_copy_call_count


@pytest.mark.parametrize(
    "raw_image, disk_dfxml_path, export_unallocated",
    [
        # No raw image, convert_to_raw should be called
        (None, "path/to/dfxml.xml", False),
        # No DFXML path, fiwalk should be called
        ("path/to/image.dd", None, False),
        # Export unallocated False
        ("path/to/image.dd", "path/to/dfxml.xml", False),
        # Export unallocated True
        ("path/to/image.dd", "path/to/dfxml.xml", True),
    ],
)
def test_carve_files_with_tsk_recover(
    mocker, raw_image, disk_dfxml_path, export_unallocated
):
    """Test that tsk_recover subprocess call and related routines are called correctly."""
    call_subprocess = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage._call_subprocess"
    )
    write_dfxml = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage.write_dfxml_with_fiwalk"
    )
    convert_raw = mocker.patch("disk_image_toolkit.disk_image.DiskImage.convert_to_raw")
    set_perms = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage.set_file_permissions"
    )
    restore_dates = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage._restore_file_last_modified_dates"
    )

    disk_image = DiskImage(DISK_IMAGE)

    if raw_image:
        disk_image.raw_disk_image = raw_image

    if disk_dfxml_path:
        disk_image.disk_dfxml_path = disk_dfxml_path

    disk_image.carve_files_with_tsk_recover(export_unallocated=export_unallocated)

    if not raw_image:
        assert convert_raw.call_count == 1
    else:
        assert convert_raw.call_count == 0

    if not disk_dfxml_path:
        assert write_dfxml.call_count == 1
    else:
        assert write_dfxml.call_count == 0

    if export_unallocated:
        call_subprocess.assert_called_with(
            ["tsk_recover", "-e", raw_image, "carved_files"],
            "tsk_recover could not carve files",
        )
    else:
        call_subprocess.assert_called_with(
            ["tsk_recover", "-a", raw_image, "carved_files"],
            "tsk_recover could not carve files",
        )

    assert set_perms.call_count == 1
    assert restore_dates.call_count == 1


@pytest.mark.parametrize(
    "raw_image, appledouble_resforks, create_dfxml",
    [
        # No raw image, convert_to_raw should be called
        (None, False, False),
        # Appledouble resforks
        ("path/to/image.dd", True, False),
        # Create DFXML
        ("path/to/image.dd", False, True),
    ],
)
def test_carve_files_with_hfs_explorer(
    mocker, raw_image, appledouble_resforks, create_dfxml
):
    """Test that unhfs subprocess call and related routines called correctly."""
    call_subprocess = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage._call_subprocess"
    )
    convert_raw = mocker.patch("disk_image_toolkit.disk_image.DiskImage.convert_to_raw")
    set_perms = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage.set_file_permissions"
    )
    write_dfxml = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage.write_dfxml_from_path"
    )

    disk_image = DiskImage(DISK_IMAGE_HFS)

    if raw_image:
        disk_image.raw_disk_image = raw_image

    disk_image.carve_files_with_hfs_explorer(
        appledouble_resforks=appledouble_resforks, create_dfxml=create_dfxml
    )

    if not raw_image:
        assert convert_raw.call_count == 1
    else:
        assert convert_raw.call_count == 0

    if appledouble_resforks:
        call_subprocess.assert_called_with(
            [
                "bash",
                "/usr/share/hfsexplorer/bin/unhfs",
                "-v",
                "-resforks",
                "APPLEDOUBLE",
                "-o",
                "carved_files",
                raw_image,
            ],
            "HFS Explorer could not carve files from disk image",
        )
    else:
        call_subprocess.assert_called_with(
            [
                "bash",
                "/usr/share/hfsexplorer/bin/unhfs",
                "-v",
                "-o",
                "carved_files",
                raw_image,
            ],
            "HFS Explorer could not carve files from disk image",
        )

    assert set_perms.call_count == 1

    if create_dfxml:
        write_dfxml.call_count == 1
    else:
        write_dfxml.call_count == 0


@pytest.mark.parametrize(
    "raw_image, create_dfxml",
    [
        # No raw image, convert_to_raw should be called
        (None, False),
        # Create DFXML
        ("path/to/image.dd", True),
    ],
)
def test_mount_image_and_copy_files(mocker, raw_image, create_dfxml):
    """Test that disk image mount, copy, and related routines are called correctly."""
    subprocess_call = mocker.patch("subprocess.call")
    convert_raw = mocker.patch("disk_image_toolkit.disk_image.DiskImage.convert_to_raw")
    set_perms = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage.set_file_permissions"
    )
    write_dfxml = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage.write_dfxml_from_path"
    )
    shutil_copytree = mocker.patch("shutil.copytree")

    temp_dir = mocker.patch("tempfile.TemporaryDirectory.__enter__")
    temp_dir.side_effect = "/path/totmpdir"

    disk_image = DiskImage("udf-example.dd")

    if raw_image:
        disk_image.raw_disk_image = raw_image

    disk_image.mount_disk_image_and_copy_files(create_dfxml=create_dfxml)

    if not raw_image:
        assert convert_raw.call_count == 1
    else:
        assert convert_raw.call_count == 0

    cmd = "sudo mount -t udf -o loop '{}' /".format(raw_image)
    subprocess_call.assert_called_with(cmd, shell=True)

    if create_dfxml:
        write_dfxml.call_count == 1
    else:
        write_dfxml.call_count == 0

    assert shutil_copytree.call_count == 1
    assert set_perms.call_count == 1


def test_write_dfxml_with_fwalk(mocker):
    """Test writing DFXML with fiwalk."""
    call_subprocess = mocker.patch(
        "disk_image_toolkit.disk_image.DiskImage._call_subprocess"
    )

    raw_image = "example.dd"
    disk_image = DiskImage(raw_image)
    disk_image.raw_disk_image = raw_image

    disk_image.write_dfxml_with_fiwalk()

    call_subprocess.assert_called_with(
        ["fiwalk", "-X", "dfxml.xml", raw_image], "Unable to create DFXML with fiwalk"
    )
    assert disk_image.disk_dfxml_path == "dfxml.xml"


def test_restore_file_last_modified_dates(mocker):
    """Test restoring filesystem dates from DFXML file."""
    os_utime = mocker.patch("os.utime")
    disk_image = DiskImage("image.dd")
    disk_image._restore_file_last_modified_dates(
        destination_path=os.path.join(TEST_FIXTURES_DIR, "fat12"),
        dfxml_path=DFXML_FIXTURE,
    )
    assert os_utime.call_count == 2


def test_write_dfxml_from_path(tmp_path):
    """Test DFXML creation from path."""
    dfxml_path = tmp_path / "dfxml.xml"

    disk_image = DiskImage("image.dd")
    disk_image.write_dfxml_from_path(
        target_path=os.path.join(TEST_FIXTURES_DIR, "fat12"), dfxml_path=dfxml_path
    )

    fixture_fileobjects = []
    dfxml_fileobjects = []

    def _get_fileobjects(filepath):
        fileobjects = []
        for event, obj in objects.iterparse(filepath):
            if not isinstance(obj, objects.FileObject):
                continue
            fileobjects.append(obj.filename)
        return fileobjects

    fixture_fileobjects = _get_fileobjects(DFXML_FIXTURE)
    dfxml_fileobjects = _get_fileobjects(str(dfxml_path))

    assert fixture_fileobjects == dfxml_fileobjects


@pytest.mark.parametrize(
    "extension, return_value",
    [
        # EWF extensions
        ("e00", True),
        ("E00", True),
        ("e01", True),
        ("E01", True),
        ("ewf", True),
        ("EWF", True),
        ("ex0", True),
        ("EX0", True),
        # Non-EWF extensions
        ("dd", False),
        ("iso", False),
        ("img", False),
        ("DD", False),
    ],
)
def test_is_ewf(extension, return_value):
    """Test is_ewf attribute."""
    image_name = f"path/to/image.{extension}"
    disk_image = DiskImage(image_name)
    assert disk_image.is_ewf == return_value
