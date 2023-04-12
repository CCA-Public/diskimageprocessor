"""Disk Image Toolkit package

Contains DiskImage class for interacting with disk images in an archival context.
"""
from datetime import datetime
import logging
import os
import shutil
import six
import stat
import subprocess
import sys
import tempfile
import time

from disk_image_toolkit.dfxml import objects
from disk_image_toolkit.dfxml.walk_to_dfxml import filepath_to_fileobject

from disk_image_toolkit.exception import DFXMLError, DiskImageError
from disk_image_toolkit.util import time_to_int


__version__ = "1.0.0"

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

UNHFS_DEFAULT_BIN = "/usr/share/hfsexplorer/bin/unhfs"
UDF_MOUNT = "/mnt/diskid/"


logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class DiskImage:
    """DiskImage class."""

    TSK_FILE_SYSTEMS = (
        "ntfs",
        "fat",
        "ext",
        "iso9660",
        "hfs+",
        "ufs",
        "raw",
        "swap",
        "yaffs2",
    )

    OTHER_FILE_SYSTEMS = ("hfs", "udf")

    ALL_FILE_SYSTEMS = TSK_FILE_SYSTEMS + OTHER_FILE_SYSTEMS

    DEFAULT_RAW_IMAGE = os.path.join(THIS_DIR, "raw_disk_image.img")
    DEFAULT_DISKTYPE_TXT = os.path.join(THIS_DIR, "disktype.txt")

    def __init__(self, path, unhfs_bin=UNHFS_DEFAULT_BIN):
        self.path = os.path.abspath(path)
        self.filename = os.path.basename(path)
        self.identifier, self.extension = os.path.splitext(self.filename)
        self.raw_disk_image = None
        self.disktype: bytes = None
        self.disk_dfxml_path = None
        self.unhfs_bin = unhfs_bin

    @staticmethod
    def _call_subprocess(
        command: list,
        error_msg: str = "Error running subprocess",
        raise_exception: bool = False,
        cwd=THIS_DIR,
    ):
        """Call subprocess and handle exception."""
        try:
            return subprocess.check_output(command, cwd=cwd)
        except subprocess.CalledProcessError as err:
            err_msg = "Subprocess error: {}. Details: {}".format(error_msg, err)
            logger.error(err_msg)
            if raise_exception:
                raise DiskImageError(err_msg)

    def convert_to_raw(self, destination_path=DEFAULT_RAW_IMAGE):
        """Convert disk image from EWF to raw format and return new path.

        If disk image is already raw, return path to existing image.

        :param destination_path: Path of output raw disk image (str)

        :returns: Path to raw disk image (str)
        """
        if not self.is_ewf:
            self.raw_disk_image = self.path
            return self.raw_disk_image

        logger.info("Converting EWF disk image to raw format...")

        with tempfile.TemporaryDirectory() as tempdir:
            temp_raw_image = os.path.join(tempdir, self.identifier)
            self._call_subprocess(
                command=[
                    "ewfexport",
                    "-t",
                    temp_raw_image,
                    "-f",
                    "raw",
                    "-o",
                    "0",
                    "-S",
                    "0",
                    "-u",
                    self.path,
                ],
                error_msg="Error running ewfexport to convert disk image to raw format",
            )

            # Rename and move raw disk image files to expected path.
            os.rename(
                os.path.join(tempdir, "{}.raw".format(self.identifier)),
                destination_path,
            )
            os.rename(
                os.path.join(tempdir, "{}.raw.info".format(self.identifier)),
                destination_path + ".info",
            )

            self.raw_disk_image = destination_path

        return self.raw_disk_image

    def run_disktype(self, output_file=DEFAULT_DISKTYPE_TXT):
        """Run disktype on disk image and return output.

        :param output_file: Optional path to file to write output to (str)

        :returns: Disktype output (bytes)
        """
        if not self.raw_disk_image:
            self.convert_to_raw()

        self.disktype = self._call_subprocess(
            command=["disktype", self.raw_disk_image],
            error_msg="Error running disktype",
        )

        if self.disktype and output_file:
            with open(output_file, "wb") as disktype_file:
                disktype_file.write(self.disktype)

        return self.disktype

    def get_volumes_from_disktype(self):
        """Return dict of volumes from disktype output."""
        if not self.disktype:
            self.run_disktype()

        volumes = []
        current_volume = {}
        current_volume_index = 0

        for line in self.disktype.splitlines():
            line = six.ensure_text(line, errors="ignore").strip()

            if "file system" in line:
                if current_volume.get("file_system"):
                    # If there's already a populated current volume, add it to volumes
                    # list before intializing new current_volume
                    volumes.append(current_volume)
                    current_volume = {}

                current_volume_index += 1
                current_volume["id"] = current_volume_index
                current_volume["name"] = ""
                current_volume["formatted_name"] = ""

                file_system = line.split(" file system")[0]
                current_volume["file_system"] = file_system
                current_volume[
                    "output_directory_name"
                ] = f"volume-{current_volume_index}-{file_system.lower()}"

            else:
                if "Volume name" in line:
                    volume_name = (
                        line.strip().replace("Volume name ", "").replace('"', "")
                    )
                    current_volume["name"] = volume_name
                    current_volume["formatted_name"] = self._format_volume_name(
                        volume_name
                    )
                    current_volume["output_directory_name"] = "{}-{}".format(
                        current_volume["output_directory_name"],
                        current_volume["formatted_name"],
                    )

                elif "Volume size" in line:
                    volume_size = line.strip().replace("Volume size ", "")
                    current_volume["size"] = volume_size

                elif "Disk size" in line:
                    disk_size = line.strip().replace("Disk size ", "")
                    current_volume["size"] = disk_size

        volumes.append(current_volume)

        return volumes

    @staticmethod
    def _format_volume_name(line):
        """Return volume name or None."""
        output = [
            char
            for char in line
            if char.isalnum() or char.isspace() or char in ("-", "_")
        ]
        output_string = "".join(output)
        return output_string.replace(" ", "_").rstrip("/")

    def carve_files_from_all_volumes(
        self,
        destination_path=os.path.join(THIS_DIR, "carved_files"),
        export_unallocated=False,
        appledouble_resforks=True,
        dfxml_directory=THIS_DIR,
    ):
        """Attempt to carve files from each volume identified by disktype.

        :param destination_path: Path to write carved files to (str)
        :param export_unallocated: Flag of whether to carve unallocated (e.g.
            deleted) files in addition to allocated ones (bool)
        :param appledouble_resforks: Flag of whether to carve AppleDouble
            resource forks from HFS disk images (bool)
        :param dfxml_directory: Optional directory to write DFXML files to (str)
        """
        if not self.disktype:
            self.run_disktype()

        dfxml_path = os.path.join(THIS_DIR, "dfxml.xml")
        if dfxml_directory:
            dfxml_path = os.path.join(dfxml_directory, "dfxml.xml")

        self.write_dfxml_with_fiwalk(dfxml_path)

        if not self.disktype:
            logger.error("No disktype output - skipping")
            sys.exit(1)

        volumes = self.get_volumes_from_disktype()

        for volume in volumes:
            output_dir_name = volume["output_directory_name"]
            output_dir = os.path.join(destination_path, output_dir_name)
            os.makedirs(output_dir)

            volume_dfxml_path = os.path.join(
                dfxml_directory, "dfxml_{}.xml".format(volume["output_directory_name"])
            )

            self.carve_files(
                volume["file_system"],
                destination_path=output_dir,
                export_unallocated=export_unallocated,
                disk_dfxml_path=dfxml_path,
                volume_dfxml_path=volume_dfxml_path,
            )

        num_volumes = len(volumes)
        msg = f"File export attempted from {num_volumes} volume"
        if num_volumes != 1:
            msg = f"{msg}s"
        logger.info(msg)

        return volumes

    def carve_files(
        self,
        file_system,
        destination_path=os.path.join(THIS_DIR, "carved_files"),
        export_unallocated=False,
        appledouble_resforks=False,
        disk_dfxml_path="dfxml.xml",
        volume_dfxml_path=os.path.join(THIS_DIR, "volume_dfxml.xml"),
    ):
        """Carve files from disk image, choosing method based on file system
            information produced by disktype.

        :param destination_path: Path to write carved files to (str)
        :param file_system: volume file system (str)
        :param export_unallocated: Flag of whether to carve unallocated (e.g.
            deleted) files in addition to allocated ones (bool)
        :param appledouble_resforks: Flag of whether to carve AppleDouble
            resource forks from HFS disk images (bool)
        :param dfxml_path: Path to write DFXML to (str)
        """
        file_system = file_system.lower()

        if not os.path.isdir(destination_path):
            os.makedirs(destination_path)

        if "fat" in file_system or file_system in self.TSK_FILE_SYSTEMS:
            self.carve_files_with_tsk_recover(
                destination_path, export_unallocated, disk_dfxml_path
            )
        elif file_system == "hfs":
            self.carve_files_with_hfs_explorer(
                destination_path, appledouble_resforks, dfxml_path=volume_dfxml_path
            )
        elif file_system == "udf":
            self.mount_disk_image_and_copy_files(
                destination_path, dfxml_path=volume_dfxml_path
            )
        else:
            logger.error(
                "Unable to carve files from volume {} with unknown file system {}".format(
                    os.path.basename(destination_path), file_system
                )
            )

        files_in_dest_dir = os.listdir(destination_path)
        if not files_in_dest_dir:
            logger.error(
                "Files not exported to {} from file system {}. Cleaning up empty directory".format(
                    os.path.basename(destination_path), file_system
                )
            )
            try:
                shutil.rmtree(destination_path)
            except OSError:
                pass

    def carve_files_with_tsk_recover(
        self,
        destination_path="carved_files",
        export_unallocated=False,
        dfxml_path="dfxml.py",
    ):
        """Carve files from disk image using tsk_recover.

        :param destination_path: Path to write carved files to (str)
        :param export_unallocated: Flag of whether to carve unallocated (e.g.
            deleted) files in addition to allocated ones (bool)
        :param dfxml_path: Path to write DFXML to (str)
        """
        if not self.raw_disk_image:
            self.convert_to_raw()

        if not self.disk_dfxml_path:
            self.write_dfxml_with_fiwalk(dfxml_path)

        carve_flag = "-a"
        if export_unallocated:
            carve_flag = "-e"

        self._call_subprocess(
            ["tsk_recover", carve_flag, self.raw_disk_image, destination_path],
            "tsk_recover could not carve files",
        )

        self.set_file_permissions(destination_path)

        try:
            self._restore_file_last_modified_dates(
                destination_path, self.disk_dfxml_path
            )
        except DFXMLError as err:
            logger.error(
                f"Error restoring file last modified dates from DFXML values: {err}"
            )

    def write_dfxml_with_fiwalk(self, dfxml_path="dfxml.xml"):
        """Write DFXML of disk image with fiwalk.

        :param dfxml_path: Path to write DFXML to (str)
        """
        self._call_subprocess(
            ["fiwalk", "-X", dfxml_path, self.raw_disk_image],
            "Unable to create DFXML with fiwalk",
        )
        self.disk_dfxml_path = dfxml_path
        logger.info("DFXML written to {}".format(self.disk_dfxml_path))

    def _restore_file_last_modified_dates(self, destination_path, dfxml_path):
        """Restore file last modified dates from values in DFXML."""
        try:
            for event, obj in objects.iterparse(dfxml_path):
                if not isinstance(obj, objects.FileObject):
                    continue

                # Skip directories and links.
                if obj.name_type and obj.name_type != "r":
                    continue

                dfxml_filename = obj.filename
                dfxml_filedate = int(time.time())

                modified_time = None
                if obj.mtime:
                    modified_time = str(obj.mtime)

                created_time = None
                if obj.crtime:
                    created_time = str(obj.crtime)

                if modified_time and modified_time != "None":
                    modified_time = time_to_int(modified_time[:19])
                    dfxml_filedate = modified_time
                elif created_time and created_time != "None":
                    created_time = time_to_int(created_time[:19])
                    dfxml_filedate = created_time

                carved_filepath = os.path.join(destination_path, dfxml_filename)
                if os.path.isfile(carved_filepath):
                    os.utime(carved_filepath, (dfxml_filedate, dfxml_filedate))
                elif os.path.isfile(dfxml_filename):
                    os.utime(dfxml_filename, (dfxml_filedate, dfxml_filedate))
        except OSError as err:
            error_msg = "Error restoring modified dates for files carved from disk {}: {}".format(
                self.raw_disk_image, err
            )
            raise DFXMLError(error_msg)

    def carve_files_with_hfs_explorer(
        self,
        destination_path="carved_files",
        appledouble_resforks=False,
        create_dfxml=True,
        dfxml_path="dfxml.xml",
    ):
        """Carve files from HFS disk image using HFS Explorer.

        :param destination_path: Path to write carved files to (str)
        :param export_unallocated: Flag of whether to carve unallocated (e.g.
            deleted) files in addition to allocated ones (bool)
        :param dfxml_path: Path to write DFXML to (str)
        """
        if not self.raw_disk_image:
            self.convert_to_raw()

        cmd = [
            "bash",
            self.unhfs_bin,
            "-v",
            "-o",
            destination_path,
            self.raw_disk_image,
        ]
        if appledouble_resforks:
            cmd.insert(3, "-resforks")
            cmd.insert(4, "APPLEDOUBLE")

        self._call_subprocess(cmd, "HFS Explorer could not carve files from disk image")

        self.set_file_permissions(destination_path)

        if create_dfxml:
            self.write_dfxml_from_path(destination_path, dfxml_path)

    def mount_disk_image_and_copy_files(
        self,
        destination_path="carved_files",
        file_system="udf",
        create_dfxml=True,
        dfxml_path="dfxml.xml",
    ):
        """Mount disk image and copy files to destination_path.

        :param destination_path: Path to write carved files to (str)
        :param dfxml_path: Path to write DFXML to (str)
        """
        if not self.raw_disk_image:
            self.convert_to_raw()

        # Mount disk image.
        subprocess.call(
            "sudo mount -t {} -o loop '{}' {}".format(
                file_system, self.raw_disk_image, UDF_MOUNT
            ),
            shell=True,
        )

        # Copy files.
        try:
            if os.path.isdir(destination_path):
                shutil.rmtree(destination_path)
            shutil.copytree(UDF_MOUNT, destination_path, symlinks=False, ignore=None)
        except OSError as err:
            logger.error(
                "Error copying files from disk image {} mounted at {}: {}".format(
                    self.raw_disk_image, UDF_MOUNT, err
                )
            )

        # Unmount disk image.
        subprocess.call("sudo umount {}".format(UDF_MOUNT), shell=True)

        self.set_file_permissions(destination_path)

        if create_dfxml:
            self.write_dfxml_from_path(destination_path, dfxml_path)

    @staticmethod
    def write_dfxml_from_path(target_path, dfxml_path="dfxml.xml"):
        """Write DFXML of directory.

        :param target_path: Path to source directory (str)
        :param dfxml_path: Path to write DFXML to (str)

        Modified from walk_to_dfxml.py by NIST, Simson Garfinkel, and
        Alex Nelson, public domain:
        https://github.com/dfxml-working-group/dfxml_python/blob/main/
        python/walk_to_dfxml.py
        """
        dobj = objects.DFXMLObject(version="1.1.1")
        dobj.program = "Disk Image Toolkit"
        dobj.program_version = __version__
        dobj.dc["type"] = "File system walk"
        dobj.add_creator_library("objects.py", objects.__version__)
        dobj.add_creator_library("dfxml.py", objects.dfxml.__version__)

        os.chdir(os.path.abspath(target_path))

        filepaths = set()
        filepaths.add(".")
        for dirpath, dirnames, filenames in os.walk(target_path):
            dirent_names = set()
            for dirname in dirnames:
                dirent_names.add(dirname)
            for filename in filenames:
                dirent_names.add(filename)
            for dirent_name in sorted(dirent_names):
                filepath = os.path.relpath(os.path.join(dirpath, dirent_name))
                filepaths.add(filepath)

        fileobjects_by_filepath = dict()

        for filepath in sorted(filepaths):
            fobj = filepath_to_fileobject(filepath)
            rel_filepath = os.path.relpath(filepath, start=target_path)
            fileobjects_by_filepath[rel_filepath] = fobj

        # Build output DFXML tree.
        for filepath in sorted(fileobjects_by_filepath.keys()):
            dobj.append(fileobjects_by_filepath[filepath])
        with open(dfxml_path, "w") as output_fh:
            dobj.print_dfxml(output_fh=output_fh)

        logger.info("DFXML written to {}".format(dfxml_path))

    @staticmethod
    def set_file_permissions(target_dir):
        """Set permissions for files and dirs in target_dir recursively.

        :param target_path: Path to target directory (str)
        """
        for root, dirs, files in os.walk(target_dir):
            for dir_ in dirs:
                path = os.path.join(root, dir_)
                try:
                    os.chmod(
                        path,
                        stat.S_IRUSR
                        | stat.S_IWUSR
                        | stat.S_IXUSR
                        | stat.S_IRGRP
                        | stat.S_IXGRP
                        | stat.S_IROTH
                        | stat.S_IXOTH,
                    )
                except OSError as err:
                    logger.error(f"Error setting permissions: {err}")

            for file_ in files:
                path = os.path.join(root, file_)
                try:
                    os.chmod(
                        path,
                        stat.S_IRUSR
                        | stat.S_IWUSR
                        | stat.S_IRGRP
                        | stat.S_IWGRP
                        | stat.S_IROTH,
                    )
                except OSError as err:
                    logger.error(f"Error setting permissions: {err}")

    @property
    def is_ewf(self):
        """Return boolean indicating if file is an Expert Witness Disk Image."""
        ewf_extensions = ("e00", "e01", "ewf", "ex0")
        for ewf_extension in ewf_extensions:
            if self.extension.lower().endswith(ewf_extension.lower()):
                return True
        return False
