# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from .core import FileHandler, FolderHandler


class FileOperations:
    """Common file operations utility class"""

    @staticmethod
    def join_paths(*paths: str) -> str:
        """Join multiple paths"""
        return os.path.join(*paths)

    @staticmethod
    def get_absolute_path(path: str) -> str:
        """Get absolute path"""
        return os.path.abspath(path)

    @staticmethod
    def get_relative_path(path: str, start: Optional[str] = None) -> str:
        """Get relative path"""
        if start:
            return os.path.relpath(path, start)
        return os.path.relpath(path)

    @staticmethod
    def split_path(path: str) -> tuple:
        """Split path into directory and filename"""
        return os.path.split(path)

    @staticmethod
    def split_extension(path: str) -> tuple:
        """Split path into root and extension"""
        return os.path.splitext(path)

    @staticmethod
    def change_extension(file_path: str, new_extension: str) -> str:
        """Change file extension"""
        root, _ = FileOperations.split_extension(file_path)
        if not new_extension.startswith('.'):
            new_extension = '.' + new_extension
        return root + new_extension

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information"""
        handler = FileHandler(file_path)

        if not handler.exists():
            raise FileNotFoundError(f'File not found: {file_path}')

        stat = handler.path_obj.stat()
        return {
            'path': file_path,
            'name': handler.get_name(),
            'name_without_extension': handler.get_name(False),
            'extension': handler.get_extension(),
            'size_bytes': handler.get_size(),
            'size_human': handler.get_size(human_readable=True),
            'parent_directory': handler.get_parent_dir(),
            'absolute_path': str(handler.path_obj.absolute()),
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'accessed_time': datetime.fromtimestamp(stat.st_atime),
            'is_file': True,
            'is_directory': False,
        }

    @staticmethod
    def get_folder_info(folder_path: str) -> Dict[str, Any]:
        """Get comprehensive folder information"""
        handler = FolderHandler(folder_path)

        if not handler.exists():
            raise FileNotFoundError(f'Folder not found: {folder_path}')

        stat = handler.path_obj.stat()
        return {
            'path': folder_path,
            'name': handler.path_obj.name,
            'size_bytes': handler.get_size(),
            'size_human': handler.get_size(human_readable=True),
            'file_count': handler.get_file_count(recursive=False),
            'folder_count': handler.get_folder_count(recursive=False),
            'total_file_count': handler.get_file_count(recursive=True),
            'total_folder_count': handler.get_folder_count(recursive=True),
            'absolute_path': str(handler.path_obj.absolute()),
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'accessed_time': datetime.fromtimestamp(stat.st_atime),
            'is_file': False,
            'is_directory': True,
        }

    @staticmethod
    def find_duplicate_files(
        folder_path: str, recursive: bool = True
    ) -> Dict[str, List[str]]:
        """Find duplicate files by size and content"""
        handler = FolderHandler(folder_path)

        if not handler.exists():
            raise FileNotFoundError(f'Folder not found: {folder_path}')

        # Group files by size first
        size_groups = {}
        for file_path in handler.list_files(recursive=recursive):
            size = FileHandler(file_path).get_size()
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(file_path)

        # Check files with same size by content
        duplicates = {}
        for size, files in size_groups.items():
            if len(files) > 1:
                content_groups = {}
                for file_path in files:
                    file_handler = FileHandler(file_path)
                    # For large files, you might want to use hash of first few bytes
                    # For simplicity, we'll use the entire content hash
                    content_hash = hash(file_handler.read_bytes())

                    if content_hash not in content_groups:
                        content_groups[content_hash] = []
                    content_groups[content_hash].append(file_path)

                for content_hash, duplicate_files in content_groups.items():
                    if len(duplicate_files) > 1:
                        duplicates[content_hash] = duplicate_files

        return duplicates

    @staticmethod
    def create_backup(file_path: str, backup_dir: str = 'backups') -> str:
        """Create a backup of a file"""
        file_handler = FileHandler(file_path)

        if not file_handler.exists():
            raise FileNotFoundError(f'File not found: {file_path}')

        # Create backup directory
        backup_handler = FolderHandler(backup_dir)
        backup_handler.create()

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name_without_ext = file_handler.get_name(False)
        extension = file_handler.get_extension()
        backup_filename = f'{name_without_ext}_{timestamp}{extension}'
        backup_path = FileOperations.join_paths(backup_dir, backup_filename)

        # Copy file to backup location
        file_handler.copy(backup_path)
        return backup_path
