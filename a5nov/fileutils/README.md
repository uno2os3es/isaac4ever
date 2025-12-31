# FileUtils

A comprehensive Python package for handling files and folders with common file operations.

## Features

- **File Handling**: Read, write, copy, move, delete files
- **Folder Management**: Create, delete, list, manage folders
- **File Search**: Advanced search capabilities
- **Compression**: ZIP, TAR, GZIP support
- **Validation**: File type, size, permission validation
- **Utilities**: Path operations, file information, backups

## Installation

```bash
pip install fileutils
from fileutils import FileHandler, FolderHandler, FileOperations

# File operations
file_handler = FileHandler("path/to/file.txt")
content = file_handler.read_text()
file_handler.write_text("New content")

# Folder operations
folder_handler = FolderHandler("path/to/folder")
files = folder_handler.list_files()

# File information
file_info = FileOperations.get_file_info("path/to/file.txt")
```
