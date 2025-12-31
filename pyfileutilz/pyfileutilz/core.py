# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import shutil
import pathlib
from typing import List, Union, Dict, Any
import json
import csv
from datetime import datetime


class FileHandler:
    """Handler for file operations"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.path_obj = pathlib.Path(file_path)

    def exists(self) -> bool:
        """Check if file exists"""
        return self.path_obj.exists() and self.path_obj.is_file()

    def get_size(self, human_readable: bool = False) -> Union[int, str]:
        """Get file size in bytes or human readable format"""
        if not self.exists():
            raise FileNotFoundError(f'File not found: {self.file_path}')

        size = self.path_obj.stat().st_size

        if human_readable:
            return self._bytes_to_human(size)
        return size

    def get_extension(self) -> str:
        """Get file extension"""
        return self.path_obj.suffix.lower()

    def get_name(self, with_extension: bool = True) -> str:
        """Get file name"""
        if with_extension:
            return self.path_obj.name
        return self.path_obj.stem

    def get_parent_dir(self) -> str:
        """Get parent directory"""
        return str(self.path_obj.parent)

    def get_modified_time(self) -> datetime:
        """Get last modified time"""
        if not self.exists():
            raise FileNotFoundError(f'File not found: {self.file_path}')
        return datetime.fromtimestamp(self.path_obj.stat().st_mtime)

    def read_text(self, encoding: str = 'utf-8') -> str:
        """Read file as text"""
        if not self.exists():
            raise FileNotFoundError(f'File not found: {self.file_path}')
        return self.path_obj.read_text(encoding=encoding)

    def read_bytes(self) -> bytes:
        """Read file as bytes"""
        if not self.exists():
            raise FileNotFoundError(f'File not found: {self.file_path}')
        return self.path_obj.read_bytes()

    def read_json(self, encoding: str = 'utf-8') -> Any:
        """Read JSON file"""
        content = self.read_text(encoding)
        return json.loads(content)

    def read_csv(
        self, delimiter: str = ',', encoding: str = 'utf-8'
    ) -> List[Dict]:
        """Read CSV file"""
        if not self.exists():
            raise FileNotFoundError(f'File not found: {self.file_path}')

        with open(self.file_path, 'r', encoding=encoding) as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            return list(reader)

    def write_text(
        self, content: str, encoding: str = 'utf-8', overwrite: bool = True
    ) -> bool:
        """Write text to file"""
        if self.exists() and not overwrite:
            raise FileExistsError(f'File already exists: {self.file_path}')

        self.path_obj.parent.mkdir(parents=True, exist_ok=True)
        self.path_obj.write_text(content, encoding=encoding)
        return True

    def write_bytes(self, content: bytes, overwrite: bool = True) -> bool:
        """Write bytes to file"""
        if self.exists() and not overwrite:
            raise FileExistsError(f'File already exists: {self.file_path}')

        self.path_obj.parent.mkdir(parents=True, exist_ok=True)
        self.path_obj.write_bytes(content)
        return True

    def write_json(
        self,
        data: Any,
        indent: int = 2,
        encoding: str = 'utf-8',
        overwrite: bool = True,
    ) -> bool:
        """Write JSON to file"""
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        return self.write_text(content, encoding, overwrite)

    def append_text(self, content: str, encoding: str = 'utf-8') -> bool:
        """Append text to file"""
        self.path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file_path, 'a', encoding=encoding) as file:
            file.write(content)
        return True

    def copy(self, destination: str, overwrite: bool = True) -> bool:
        """Copy file to destination"""
        if not self.exists():
            raise FileNotFoundError(f'File not found: {self.file_path}')

        dest_path = pathlib.Path(destination)
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f'Destination file exists: {destination}')

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.file_path, destination)
        return True

    def move(self, destination: str, overwrite: bool = True) -> bool:
        """Move file to destination"""
        if not self.exists():
            raise FileNotFoundError(f'File not found: {self.file_path}')

        dest_path = pathlib.Path(destination)
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f'Destination file exists: {destination}')

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(self.file_path, destination)
        self.file_path = destination
        self.path_obj = pathlib.Path(destination)
        return True

    def delete(self) -> bool:
        """Delete file"""
        if not self.exists():
            raise FileNotFoundError(f'File not found: {self.file_path}')

        self.path_obj.unlink()
        return True

    def rename(self, new_name: str, overwrite: bool = True) -> bool:
        """Rename file"""
        new_path = self.path_obj.parent / new_name
        return self.move(str(new_path), overwrite)

    @staticmethod
    def _bytes_to_human(size: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f'{size:.2f} {unit}'
            size /= 1024.0
        return f'{size:.2f} PB'


class FolderHandler:
    """Handler for folder operations"""

    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.path_obj = pathlib.Path(folder_path)

    def exists(self) -> bool:
        """Check if folder exists"""
        return self.path_obj.exists() and self.path_obj.is_dir()

    def get_parent_dir(self) -> str:
        """Get parent directory"""
        return str(self.path_obj.parent)

    def create(self, parents: bool = True, exist_ok: bool = True) -> bool:
        """Create folder"""
        self.path_obj.mkdir(parents=parents, exist_ok=exist_ok)
        return self.exists()

    def delete(self, recursive: bool = False) -> bool:
        """Delete folder"""
        if not self.exists():
            raise FileNotFoundError(f'Folder not found: {self.folder_path}')

        if recursive:
            shutil.rmtree(self.folder_path)
        else:
            self.path_obj.rmdir()
        return not self.exists()

    def get_size(self, human_readable: bool = False) -> Union[int, str]:
        """Get total size of folder contents"""
        if not self.exists():
            raise FileNotFoundError(f'Folder not found: {self.folder_path}')

        total_size = 0
        for file_path in self.path_obj.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        if human_readable:
            return FileHandler._bytes_to_human(total_size)
        return total_size

    def list_contents(
        self, pattern: str = '*', recursive: bool = False
    ) -> List[str]:
        """List folder contents"""
        if not self.exists():
            raise FileNotFoundError(f'Folder not found: {self.folder_path}')

        if recursive:
            files = self.path_obj.rglob(pattern)
        else:
            files = self.path_obj.glob(pattern)

        return [str(item) for item in files]

    def list_files(
        self, pattern: str = '*', recursive: bool = False
    ) -> List[str]:
        """List only files in folder"""
        contents = self.list_contents(pattern, recursive)
        return [item for item in contents if pathlib.Path(item).is_file()]

    def list_folders(
        self, pattern: str = '*', recursive: bool = False
    ) -> List[str]:
        """List only folders in directory"""
        contents = self.list_contents(pattern, recursive)
        return [item for item in contents if pathlib.Path(item).is_dir()]

    def get_file_count(self, recursive: bool = False) -> int:
        """Get count of files in folder"""
        return len(self.list_files(recursive=recursive))

    def get_folder_count(self, recursive: bool = False) -> int:
        """Get count of folders in directory"""
        return len(self.list_folders(recursive=recursive))

    def copy(self, destination: str, overwrite: bool = True) -> bool:
        """Copy folder to destination"""
        if not self.exists():
            raise FileNotFoundError(f'Folder not found: {self.folder_path}')

        dest_path = pathlib.Path(destination)
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f'Destination folder exists: {destination}')

        if dest_path.exists():
            shutil.rmtree(destination)

        shutil.copytree(self.folder_path, destination)
        return True

    def move(self, destination: str, overwrite: bool = True) -> bool:
        """Move folder to destination"""
        if not self.exists():
            raise FileNotFoundError(f'Folder not found: {self.folder_path}')

        dest_path = pathlib.Path(destination)
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f'Destination folder exists: {destination}')

        if dest_path.exists():
            shutil.rmtree(destination)

        shutil.move(self.folder_path, destination)
        self.folder_path = destination
        self.path_obj = pathlib.Path(destination)
        return True

    def clean(self, confirm: bool = True) -> bool:
        """Clean folder (remove all contents)"""
        if not self.exists():
            raise FileNotFoundError(f'Folder not found: {self.folder_path}')

        if confirm:
            file_count = self.get_file_count(recursive=True)
            folder_count = self.get_folder_count(recursive=True)
            response = input(
                f'This will delete {file_count} files and {folder_count} folders. Continue? (y/N): '
            )
            if response.lower() != 'y':
                return False

        for item in self.path_obj.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        return True
