# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09
"""
Usage examples for FileUtils package - Fixed version
"""

import os
import tempfile
from datetime import datetime, timedelta

try:
    from pyfileutilz import (
        FileHandler,
        FolderHandler,
        FileOperations,
        FileSearch,
        FileCompressor,
        FileValidator,
    )

    print('✓ Successfully imported pyfileutilz package')
except ImportError as e:
    print(f'✗ Failed to import pyfileutilz: {e}')
    exit(1)


def main():
    # Create temporary directory for examples
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'Working in temporary directory: {temp_dir}')

        # Example 1: FileHandler examples
        print('\n=== FileHandler Examples ===')

        # Create and write to a file
        test_file = os.path.join(temp_dir, 'test.txt')
        file_handler = FileHandler(test_file)
        file_handler.write_text('Hello, World!\nThis is a test file.')
        print('✓ Created and wrote to test file')

        # Read file content
        content = file_handler.read_text()
        print(f'✓ File content: {content[:20]}...')

        # Get file info
        print(f'✓ File size: {file_handler.get_size(human_readable=True)}')
        print(f'✓ File extension: {file_handler.get_extension()}')
        print(f'✓ File name: {file_handler.get_name()}')
        print(f'✓ Parent directory: {file_handler.get_parent_dir()}')

        # Example 2: FolderHandler examples
        print('\n=== FolderHandler Examples ===')

        # Create a folder
        test_folder = os.path.join(temp_dir, 'test_folder')
        folder_handler = FolderHandler(test_folder)
        folder_handler.create()
        print('✓ Created test folder')

        # Create some files in the folder
        for i in range(3):
            file_path = os.path.join(test_folder, f'file_{i}.txt')
            FileHandler(file_path).write_text(f'Content of file {i}')
        print('✓ Created test files in folder')

        # List folder contents
        files = folder_handler.list_files()
        print(f'✓ Files in folder: {[os.path.basename(f) for f in files]}')
        print(f'✓ Folder size: {folder_handler.get_size(human_readable=True)}')
        print(f'✓ Parent directory: {folder_handler.get_parent_dir()}')

        # Example 3: FileOperations examples
        print('\n=== FileOperations Examples ===')

        # Get file information
        file_info = FileOperations.get_file_info(test_file)
        print(f'✓ File info: {file_info["name"]} - {file_info["size_human"]}')

        # Create backup
        backup_path = FileOperations.create_backup(
            test_file, os.path.join(temp_dir, 'backups')
        )
        print(f'✓ Backup created: {os.path.basename(backup_path)}')

        # Example 4: FileSearch examples
        print('\n=== FileSearch Examples ===')

        # Search for files
        txt_files = FileSearch.find_files_by_extension(
            temp_dir, '.txt', recursive=True
        )
        print(f'✓ Found {len(txt_files)} text files')

        # Advanced search
        recent_files = FileSearch.find_files_by_date(
            temp_dir,
            start_date=datetime.now() - timedelta(hours=1),
            recursive=True,
        )
        print(f'✓ Found {len(recent_files)} files modified in the last hour')

        # Example 5: FileCompressor examples
        print('\n=== FileCompressor Examples ===')

        # Create ZIP archive
        zip_path = os.path.join(temp_dir, 'test_folder.zip')
        try:
            FileCompressor.create_zip(test_folder, zip_path)
            print(f'✓ ZIP archive created: {os.path.basename(zip_path)}')

            # List archive contents
            contents = FileCompressor.list_archive_contents(zip_path)
            print(
                f'✓ ZIP contents: {[os.path.basename(f) for f in contents[:3]]}...'
            )

            # Get archive info
            archive_info = FileCompressor.get_archive_info(zip_path)
            print(
                f'✓ Archive info: {archive_info["format"]} with {archive_info["file_count"]} files'
            )

        except Exception as e:
            print(f'✗ Compression failed: {e}')

        # Example 6: FileValidator examples
        print('\n=== FileValidator Examples ===')

        # Validate file
        validation = FileValidator.comprehensive_validation(
            test_file,
            rules={
                'min_size': 1,
                'max_size': 1024,
                'allowed_extensions': ['.txt'],
                'expected_type': 'text',
            },
        )
        print(f'✓ File validation results: {validation["all_valid"]}')

        # Test file type detection
        file_type = FileValidator.detect_file_type(test_file)
        print(f'✓ Detected file type: {file_type}')

        print('\n🎉 All examples completed successfully!')


def test_compression_methods():
    """Test different compression methods"""
    print('\n=== Testing Compression Methods ===')

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_file = os.path.join(temp_dir, 'test_compress.txt')
        FileHandler(test_file).write_text(
            'This is a test file for compression.' * 100
        )

        # Test GZIP compression
        try:
            gzip_path = FileCompressor.compress_gzip(test_file)
            print(f'✓ GZIP compression: {os.path.basename(gzip_path)}')

            # Decompress
            decompressed_path = FileCompressor.decompress_gzip(gzip_path)
            print(
                f'✓ GZIP decompression: {os.path.basename(decompressed_path)}'
            )
        except Exception as e:
            print(f'✗ GZIP failed: {e}')

        # Test TAR compression
        try:
            tar_path = os.path.join(temp_dir, 'test.tar')
            FileCompressor.create_tar(test_file, tar_path)
            print(f'✓ TAR creation: {os.path.basename(tar_path)}')
        except Exception as e:
            print(f'✗ TAR failed: {e}')


if __name__ == '__main__':
    main()
    test_compression_methods()
