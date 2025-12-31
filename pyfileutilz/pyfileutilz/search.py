# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import pathlib
from typing import List, Optional, Callable
import fnmatch
from datetime import datetime
from .core import FileHandler, FolderHandler


class FileSearch:
    """File search utilities"""

    @staticmethod
    def find_files_by_name(
        folder_path: str, pattern: str, recursive: bool = True
    ) -> List[str]:
        """Find files by name pattern"""
        handler = FolderHandler(folder_path)

        if not handler.exists():
            raise FileNotFoundError(f'Folder not found: {folder_path}')

        all_files = handler.list_files(recursive=recursive)
        return [
            f
            for f in all_files
            if fnmatch.fnmatch(pathlib.Path(f).name, pattern)
        ]

    @staticmethod
    def find_files_by_extension(
        folder_path: str, extension: str, recursive: bool = True
    ) -> List[str]:
        """Find files by extension"""
        if not extension.startswith('.'):
            extension = '.' + extension

        handler = FolderHandler(folder_path)

        if not handler.exists():
            raise FileNotFoundError(f'Folder not found: {folder_path}')

        all_files = handler.list_files(recursive=recursive)
        return [
            f
            for f in all_files
            if pathlib.Path(f).suffix.lower() == extension.lower()
        ]

    @staticmethod
    def find_files_by_size(
        folder_path: str,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        recursive: bool = True,
    ) -> List[str]:
        """Find files by size range (in bytes)"""
        handler = FolderHandler(folder_path)

        if not handler.exists():
            raise FileNotFoundError(f'Folder not found: {folder_path}')

        matching_files = []
        for file_path in handler.list_files(recursive=recursive):
            file_handler = FileHandler(file_path)
            size = file_handler.get_size()

            if min_size is not None and size < min_size:
                continue
            if max_size is not None and size > max_size:
                continue

            matching_files.append(file_path)

        return matching_files

    @staticmethod
    def find_files_by_date(
        folder_path: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        recursive: bool = True,
    ) -> List[str]:
        """Find files by modification date range"""
        handler = FolderHandler(folder_path)

        if not handler.exists():
            raise FileNotFoundError(f'Folder not found: {folder_path}')

        matching_files = []
        for file_path in handler.list_files(recursive=recursive):
            file_handler = FileHandler(file_path)
            mod_time = file_handler.get_modified_time()

            if start_date and mod_time < start_date:
                continue
            if end_date and mod_time > end_date:
                continue

            matching_files.append(file_path)

        return matching_files

    @staticmethod
    def find_files_by_content(
        folder_path: str,
        search_text: str,
        case_sensitive: bool = False,
        recursive: bool = True,
    ) -> List[str]:
        """Find files containing specific text"""
        handler = FolderHandler(folder_path)

        if not handler.exists():
            raise FileNotFoundError(f'Folder not found: {folder_path}')

        matching_files = []
        search_text_lower = (
            search_text if case_sensitive else search_text.lower()
        )

        for file_path in handler.list_files(recursive=recursive):
            try:
                file_handler = FileHandler(file_path)
                content = file_handler.read_text()

                if not case_sensitive:
                    content = content.lower()

                if search_text_lower in content:
                    matching_files.append(file_path)
            except (UnicodeDecodeError, PermissionError):
                # Skip binary files or files without read permission
                continue

        return matching_files

    @staticmethod
    def advanced_search(
        folder_path: str,
        name_pattern: Optional[str] = None,
        extension: Optional[str] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        content_text: Optional[str] = None,
        content_case_sensitive: bool = False,
        recursive: bool = True,
    ) -> List[str]:
        """Advanced file search with multiple criteria"""
        handler = FolderHandler(folder_path)

        if not handler.exists():
            raise FileNotFoundError(f'Folder not found: {folder_path}')

        all_files = handler.list_files(recursive=recursive)
        matching_files = []

        for file_path in all_files:
            file_handler = FileHandler(file_path)
            path_obj = pathlib.Path(file_path)

            # Check name pattern
            if name_pattern and not fnmatch.fnmatch(
                path_obj.name, name_pattern
            ):
                continue

            # Check extension
            if extension:
                ext = (
                    extension if extension.startswith('.') else '.' + extension
                )
                if path_obj.suffix.lower() != ext.lower():
                    continue

            # Check size
            if min_size is not None or max_size is not None:
                size = file_handler.get_size()
                if min_size is not None and size < min_size:
                    continue
                if max_size is not None and size > max_size:
                    continue

            # Check date
            if start_date or end_date:
                mod_time = file_handler.get_modified_time()
                if start_date and mod_time < start_date:
                    continue
                if end_date and mod_time > end_date:
                    continue

            # Check content
            if content_text:
                try:
                    file_content = file_handler.read_text()
                    search_content = (
                        content_text
                        if content_case_sensitive
                        else content_text.lower()
                    )
                    content_to_check = (
                        file_content
                        if content_case_sensitive
                        else file_content.lower()
                    )

                    if search_content not in content_to_check:
                        continue
                except (UnicodeDecodeError, PermissionError):
                    continue

            matching_files.append(file_path)

        return matching_files

    @staticmethod
    def find_empty_files(
        folder_path: str, recursive: bool = True
    ) -> List[str]:
        """Find empty files (0 bytes)"""
        return FileSearch.find_files_by_size(folder_path, 0, 0, recursive)

    @staticmethod
    def find_large_files(
        folder_path: str,
        size_threshold: int = 1024 * 1024,
        recursive: bool = True,
    ) -> List[str]:
        """Find files larger than specified threshold (in bytes)"""
        return FileSearch.find_files_by_size(
            folder_path, size_threshold, None, recursive
        )

    @staticmethod
    def find_recent_files(
        folder_path: str, hours: int = 24, recursive: bool = True
    ) -> List[str]:
        """Find files modified in the last N hours"""
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(hours=hours)
        return FileSearch.find_files_by_date(
            folder_path, start_date, None, recursive
        )
