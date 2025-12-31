# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import zipfile
import tarfile
import gzip
import os
from typing import List, Optional
from .core import FileHandler, FolderHandler


class FileCompressor:
    """File compression and decompression utilities"""

    @staticmethod
    def create_zip(
        source_path: str, output_path: str, include_base_dir: bool = True
    ) -> bool:
        """Create ZIP archive"""
        source_handler = (
            FileHandler(source_path)
            if os.path.isfile(source_path)
            else FolderHandler(source_path)
        )

        if not source_handler.exists():
            raise FileNotFoundError(f'Source not found: {source_path}')

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if isinstance(source_handler, FileHandler):
                # Single file
                if include_base_dir:
                    arcname = source_handler.get_name()
                else:
                    arcname = os.path.basename(source_path)
                zipf.write(source_path, arcname)
            else:
                # Directory
                for file_path in source_handler.list_files(recursive=True):
                    if include_base_dir:
                        # Use relative path from the source folder's parent
                        arcname = os.path.relpath(
                            file_path, source_handler.get_parent_dir()
                        )
                    else:
                        # Use relative path from the source folder itself
                        arcname = os.path.relpath(file_path, source_path)
                    zipf.write(file_path, arcname)

        return FileHandler(output_path).exists()

    @staticmethod
    def extract_zip(
        zip_path: str, extract_path: str, overwrite: bool = True
    ) -> bool:
        """Extract ZIP archive"""
        zip_handler = FileHandler(zip_path)

        if not zip_handler.exists():
            raise FileNotFoundError(f'ZIP file not found: {zip_path}')

        extract_handler = FolderHandler(extract_path)
        extract_handler.create()

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            if overwrite:
                zipf.extractall(extract_path)
            else:
                # Extract only if files don't exist
                for member in zipf.namelist():
                    target_path = os.path.join(extract_path, member)
                    if not os.path.exists(target_path):
                        zipf.extract(member, extract_path)

        return True

    @staticmethod
    def create_tar(
        source_path: str, output_path: str, compression: Optional[str] = None
    ) -> bool:
        """Create TAR archive (optionally compressed)"""
        source_handler = (
            FileHandler(source_path)
            if os.path.isfile(source_path)
            else FolderHandler(source_path)
        )

        if not source_handler.exists():
            raise FileNotFoundError(f'Source not found: {source_path}')

        mode = 'w'
        if compression == 'gz':
            mode = 'w:gz'
        elif compression == 'bz2':
            mode = 'w:bz2'
        elif compression == 'xz':
            mode = 'w:xz'

        with tarfile.open(output_path, mode) as tar:
            if isinstance(source_handler, FileHandler):
                arcname = source_handler.get_name()
                tar.add(source_path, arcname=arcname)
            else:
                arcname = (
                    os.path.basename(source_path)
                    if os.path.isdir(source_path)
                    else ''
                )
                tar.add(source_path, arcname=arcname)

        return FileHandler(output_path).exists()

    @staticmethod
    def extract_tar(
        tar_path: str, extract_path: str, overwrite: bool = True
    ) -> bool:
        """Extract TAR archive"""
        tar_handler = FileHandler(tar_path)

        if not tar_handler.exists():
            raise FileNotFoundError(f'TAR file not found: {tar_path}')

        extract_handler = FolderHandler(extract_path)
        extract_handler.create()

        with tarfile.open(tar_path, 'r') as tar:
            if overwrite:
                tar.extractall(extract_path)
            else:
                # Extract only if files don't exist
                for member in tar.getmembers():
                    target_path = os.path.join(extract_path, member.name)
                    if not os.path.exists(target_path):
                        tar.extract(member, extract_path)

        return True

    @staticmethod
    def compress_gzip(
        source_path: str, output_path: Optional[str] = None
    ) -> str:
        """Compress file using GZIP"""
        file_handler = FileHandler(source_path)

        if not file_handler.exists():
            raise FileNotFoundError(f'File not found: {source_path}')

        if output_path is None:
            output_path = source_path + '.gz'

        with open(source_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                f_out.writelines(f_in)

        return output_path

    @staticmethod
    def decompress_gzip(
        gzip_path: str, output_path: Optional[str] = None
    ) -> str:
        """Decompress GZIP file"""
        gzip_handler = FileHandler(gzip_path)

        if not gzip_handler.exists():
            raise FileNotFoundError(f'GZIP file not found: {gzip_path}')

        if output_path is None:
            if gzip_path.endswith('.gz'):
                output_path = gzip_path[:-3]
            else:
                output_path = gzip_path + '.decompressed'

        with gzip.open(gzip_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())

        return output_path

    @staticmethod
    def list_archive_contents(archive_path: str) -> List[str]:
        """List contents of archive file"""
        archive_handler = FileHandler(archive_path)

        if not archive_handler.exists():
            raise FileNotFoundError(f'Archive not found: {archive_path}')

        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                return zipf.namelist()
        elif tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, 'r') as tar:
                return [member.name for member in tar.getmembers()]
        else:
            raise ValueError(f'Unsupported archive format: {archive_path}')

    @staticmethod
    def get_archive_info(archive_path: str) -> dict:
        """Get information about archive file"""
        archive_handler = FileHandler(archive_path)

        if not archive_handler.exists():
            raise FileNotFoundError(f'Archive not found: {archive_path}')

        info = {
            'path': archive_path,
            'size': archive_handler.get_size(human_readable=True),
            'format': 'unknown',
            'file_count': 0,
            'compressed_size': archive_handler.get_size(),
            'contents': [],
        }

        if zipfile.is_zipfile(archive_path):
            info['format'] = 'zip'
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                info['file_count'] = len(zipf.namelist())
                info['contents'] = zipf.namelist()
                # Get uncompressed size
                total_size = sum(f.file_size for f in zipf.filelist)
                info['uncompressed_size'] = total_size
                info['compression_ratio'] = (
                    total_size / info['compressed_size']
                    if info['compressed_size'] > 0
                    else 0
                )

        elif tarfile.is_tarfile(archive_path):
            info['format'] = 'tar'
            with tarfile.open(archive_path, 'r') as tar:
                members = tar.getmembers()
                info['file_count'] = len(members)
                info['contents'] = [member.name for member in members]
                total_size = sum(member.size for member in members)
                info['uncompressed_size'] = total_size
                info['compression_ratio'] = (
                    total_size / info['compressed_size']
                    if info['compressed_size'] > 0
                    else 0
                )

        return info
