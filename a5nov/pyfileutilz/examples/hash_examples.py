# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09
"""
HashUtil usage examples
"""

import os
import tempfile
from pyfileutilz import (
    FileHasher,
    FolderHasher,
    HashComparator,
    ProgressiveFileHasher,
)
from pyfileutilz import HashAlgorithm, quick_hash, get_available_algorithms


def main():
    print('Available hash algorithms:', get_available_algorithms())

    # Create temporary directory for examples
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f'\nWorking in temporary directory: {temp_dir}')

        # Create test files
        test_files = []
        for i in range(3):
            file_path = os.path.join(temp_dir, f'test_file_{i}.txt')
            with open(file_path, 'w') as f:
                f.write(f'Content of test file {i}\n' * 100)
            test_files.append(file_path)

        # Create a duplicate file
        duplicate_file = os.path.join(temp_dir, 'duplicate_file.txt')
        with (
            open(test_files[0], 'rb') as src,
            open(duplicate_file, 'wb') as dst,
        ):
            dst.write(src.read())
        test_files.append(duplicate_file)

        # Example 1: File hashing
        print('\n=== File Hashing Examples ===')

        file_hasher = FileHasher(HashAlgorithm.SHA256)

        for file_path in test_files:
            file_hash = file_hasher.hash_file(file_path)
            print(f'{os.path.basename(file_path)}: {file_hash[:16]}...')

        # Verify file integrity
        original_hash = file_hasher.hash_file(test_files[0])
        duplicate_hash = file_hasher.hash_file(duplicate_file)
        print(
            f'\nOriginal and duplicate have same hash: {original_hash == duplicate_hash}'
        )

        # Example 2: Quick hash utility
        print('\n=== Quick Hash Utilities ===')

        quick_md5 = quick_hash(test_files[0], 'md5')
        print(f'Quick MD5 of {os.path.basename(test_files[0])}: {quick_md5}')

        # Example 3: Folder hashing
        print('\n=== Folder Hashing Examples ===')

        folder_hasher = FolderHasher(HashAlgorithm.SHA256)

        # Hash all files in folder
        folder_hashes = folder_hasher.hash_folder(temp_dir)
        print(f'Found {len(folder_hashes)} files in folder:')
        for rel_path, file_hash in folder_hashes.items():
            print(f'  {rel_path}: {file_hash[:16]}...')

        # Get folder signature
        folder_signature = folder_hasher.get_folder_signature(temp_dir)
        print(f'\nFolder signature: {folder_signature}')

        # Find duplicate files
        duplicates = folder_hasher.find_duplicate_files(temp_dir)
        print(f'\nDuplicate files found: {len(duplicates)} groups')
        for hash_val, files in duplicates.items():
            print(f'  Hash {hash_val[:16]}...: {files}')

        # Example 4: Hash comparison
        print('\n=== Hash Comparison Examples ===')

        comparator = HashComparator()

        # Compare files
        are_same = comparator.compare_files(test_files[0], duplicate_file)
        print(f'File 0 and duplicate are identical: {are_same}')

        are_different = comparator.compare_files(test_files[0], test_files[1])
        print(f'File 0 and file 1 are identical: {are_different}')

        # Example 5: Progressive hashing for large files
        print('\n=== Progressive Hashing Examples ===')

        def progress_callback(progress, bytes_processed, total_size):
            print(
                f'  Progress: {progress:.1f}% ({bytes_processed}/{total_size} bytes)',
                end='\r',
            )

        progressive_hasher = ProgressiveFileHasher()

        # Create a larger file for demonstration
        large_file = os.path.join(temp_dir, 'large_file.bin')
        with open(large_file, 'wb') as f:
            f.write(os.urandom(1024 * 1024))  # 1MB random data

        print('Hashing large file with progress updates:')
        large_file_hash = progressive_hasher.hash_file_progressive(
            large_file, progress_callback
        )
        print(f'\nLarge file hash: {large_file_hash}')

        # Example 6: Sync operations
        print('\n=== Folder Sync Operations ===')

        # Create a second folder with some differences
        target_dir = os.path.join(temp_dir, 'target_folder')
        os.makedirs(target_dir)

        # Copy some files
        import shutil

        shutil.copy(test_files[0], os.path.join(target_dir, 'test_file_0.txt'))
        shutil.copy(test_files[1], os.path.join(target_dir, 'test_file_1.txt'))

        # Create an extra file in target
        extra_file = os.path.join(target_dir, 'extra_file.txt')
        with open(extra_file, 'w') as f:
            f.write('This file only exists in target')

        sync_ops = comparator.get_sync_operations(temp_dir, target_dir)

        print('Sync operations needed:')
        for op_type, files in sync_ops.items():
            print(f'  {op_type.upper()}: {len(files)} files')
            for file in files[:3]:  # Show first 3 files
                print(f'    - {file}')
            if len(files) > 3:
                print(f'    ... and {len(files) - 3} more')


if __name__ == '__main__':
    main()
