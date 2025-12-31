# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09
"""
Pure Python implementation of hash utilities
"""

import os
import hashlib
from typing import List, Dict, Callable


class FileHasher:
    """File hasher with optimized performance"""

    def __init__(self, algorithm: str = 'sha256', buffer_size: int = 65536):
        self.algorithm = algorithm
        self.buffer_size = buffer_size

    def hash_file(self, file_path: str) -> str:
        """Calculate hash of a single file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')

        if not os.path.isfile(file_path):
            raise ValueError(f'Path is not a file: {file_path}')

        hash_obj = hashlib.new(self.algorithm)

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.buffer_size)
                if not chunk:
                    break
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def hash_files(self, file_paths: List[str]) -> Dict[str, str]:
        """Calculate hashes for multiple files"""
        results = {}

        for file_path in file_paths:
            try:
                results[file_path] = self.hash_file(file_path)
            except (IOError, ValueError) as e:
                results[file_path] = f'Error: {str(e)}'

        return results

    def verify_file_integrity(
        self, file_path: str, expected_hash: str
    ) -> bool:
        """Verify file integrity against expected hash"""
        try:
            actual_hash = self.hash_file(file_path)
            return actual_hash == expected_hash.lower()
        except Exception:
            return False


class FolderHasher:
    """Folder hashing utilities"""

    def __init__(self, algorithm: str = 'sha256', buffer_size: int = 65536):
        self.algorithm = algorithm
        self.buffer_size = buffer_size
        self.file_hasher = FileHasher(algorithm, buffer_size)

    def hash_folder(
        self,
        folder_path: str,
        include_hidden: bool = False,
        follow_symlinks: bool = False,
    ) -> Dict[str, str]:
        """Calculate hashes for all files in a folder"""
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f'Folder not found: {folder_path}')

        if not os.path.isdir(folder_path):
            raise ValueError(f'Path is not a folder: {folder_path}')

        results = {}

        for root, dirs, files in os.walk(
            folder_path, followlinks=follow_symlinks
        ):
            # Filter hidden files and directories if needed
            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    relative_path = os.path.relpath(file_path, folder_path)
                    results[relative_path] = self.file_hasher.hash_file(
                        file_path
                    )
                except (IOError, PermissionError) as e:
                    results[relative_path] = f'Error: {str(e)}'

        return results

    def get_folder_signature(
        self,
        folder_path: str,
        include_hidden: bool = False,
        follow_symlinks: bool = False,
    ) -> str:
        """Get a single hash signature for the entire folder"""
        file_hashes = self.hash_folder(
            folder_path, include_hidden, follow_symlinks
        )

        # Sort by filename to ensure consistent ordering
        sorted_files = sorted(file_hashes.items())

        # Combine all file hashes into one master hash
        combined_hash = hashlib.new(self.algorithm)
        for filename, file_hash in sorted_files:
            if not file_hash.startswith('Error:'):
                combined_hash.update(filename.encode('utf-8'))
                combined_hash.update(file_hash.encode('utf-8'))

        return combined_hash.hexdigest()

    def find_duplicate_files(
        self,
        folder_path: str,
        include_hidden: bool = False,
        follow_symlinks: bool = False,
    ) -> Dict[str, List[str]]:
        """Find duplicate files in a folder by hash"""
        file_hashes = self.hash_folder(
            folder_path, include_hidden, follow_symlinks
        )

        # Group files by their hash
        hash_groups = {}
        for file_path, file_hash in file_hashes.items():
            if not file_hash.startswith('Error:'):
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(file_path)

        # Return only groups with duplicates
        return {
            hash_val: files
            for hash_val, files in hash_groups.items()
            if len(files) > 1
        }

    def verify_folder_integrity(
        self, folder_path: str, expected_signatures: Dict[str, str]
    ) -> Dict[str, bool]:
        """Verify integrity of multiple files in a folder"""
        current_hashes = self.hash_folder(folder_path)
        results = {}

        for relative_path, expected_hash in expected_signatures.items():
            if relative_path in current_hashes:
                current_hash = current_hashes[relative_path]
                if current_hash.startswith('Error:'):
                    results[relative_path] = False
                else:
                    results[relative_path] = (
                        current_hash == expected_hash.lower()
                    )
            else:
                results[relative_path] = False

        return results


class HashComparator:
    """Compare files and folders by hash"""

    def __init__(self, algorithm: str = 'sha256', buffer_size: int = 65536):
        self.algorithm = algorithm
        self.buffer_size = buffer_size
        self.file_hasher = FileHasher(algorithm, buffer_size)
        self.folder_hasher = FolderHasher(algorithm, buffer_size)

    def compare_files(self, file1: str, file2: str) -> bool:
        """Compare two files by hash"""
        try:
            hash1 = self.file_hasher.hash_file(file1)
            hash2 = self.file_hasher.hash_file(file2)
            return hash1 == hash2
        except Exception:
            return False

    def compare_folders(
        self, folder1: str, folder2: str, include_hidden: bool = False
    ) -> Dict[str, str]:
        """Compare two folders and return differences"""
        hashes1 = self.folder_hasher.hash_folder(folder1, include_hidden)
        hashes2 = self.folder_hasher.hash_folder(folder2, include_hidden)

        all_files = set(hashes1.keys()) | set(hashes2.keys())
        differences = {}

        for file_path in sorted(all_files):
            hash1 = hashes1.get(file_path, None)
            hash2 = hashes2.get(file_path, None)

            if hash1 is None:
                differences[file_path] = f'Only in {folder2}'
            elif hash2 is None:
                differences[file_path] = f'Only in {folder1}'
            elif hash1 != hash2:
                differences[file_path] = 'Different content'
            # Files with same hash are not included in differences

        return differences

    def get_sync_operations(
        self,
        source_folder: str,
        target_folder: str,
        include_hidden: bool = False,
    ) -> Dict[str, List[str]]:
        """Get operations needed to sync target folder with source folder"""
        source_hashes = self.folder_hasher.hash_folder(
            source_folder, include_hidden
        )
        target_hashes = self.folder_hasher.hash_folder(
            target_folder, include_hidden
        )

        operations = {
            'copy': [],  # Files to copy from source to target
            'update': [],  # Files that exist in both but have different content
            'delete': [],  # Files in target that don't exist in source
        }

        # Find files to copy and update
        for rel_path, source_hash in source_hashes.items():
            if rel_path not in target_hashes:
                operations['copy'].append(rel_path)
            elif target_hashes[rel_path] != source_hash:
                operations['update'].append(rel_path)

        # Find files to delete
        for rel_path in target_hashes.keys():
            if rel_path not in source_hashes:
                operations['delete'].append(rel_path)

        return operations


class ProgressiveFileHasher:
    """Hash large files progressively with progress tracking"""

    def __init__(self, algorithm: str = 'sha256', buffer_size: int = 65536):
        self.algorithm = algorithm
        self.buffer_size = buffer_size

    def hash_file_progressive(
        self, file_path: str, progress_callback: Callable = None
    ) -> str:
        """Hash a file with progress updates"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')

        file_size = os.path.getsize(file_path)
        hash_obj = hashlib.new(self.algorithm)
        bytes_processed = 0

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.buffer_size)
                if not chunk:
                    break

                hash_obj.update(chunk)
                bytes_processed += len(chunk)

                if progress_callback:
                    progress = (bytes_processed / file_size) * 100
                    progress_callback(progress, bytes_processed, file_size)

        return hash_obj.hexdigest()

    def hash_large_file(
        self, file_path: str, chunk_callback: Callable = None
    ) -> List[str]:
        """Hash a large file in chunks, returning hash for each chunk"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')

        chunk_hashes = []

        with open(file_path, 'rb') as f:
            chunk_index = 0
            while True:
                chunk = f.read(self.buffer_size)
                if not chunk:
                    break

                chunk_hash = hashlib.new(self.algorithm)
                chunk_hash.update(chunk)
                chunk_hashes.append(chunk_hash.hexdigest())

                if chunk_callback:
                    chunk_callback(
                        chunk_index, chunk_hash.hexdigest(), len(chunk)
                    )

                chunk_index += 1

        return chunk_hashes


# Utility functions
def get_available_algorithms() -> List[str]:
    """Get list of available hashing algorithms"""
    return list(hashlib.algorithms_available)


def quick_hash(file_path: str, algorithm: str = 'md5') -> str:
    """Quick hash utility function"""
    return FileHasher(algorithm).hash_file(file_path)


def quick_folder_hash(folder_path: str, algorithm: str = 'sha256') -> str:
    """Quick folder hash utility function"""
    return FolderHasher(algorithm).get_folder_signature(folder_path)


# Constants
class HashAlgorithm:
    MD5 = 'md5'
    SHA1 = 'sha1'
    SHA256 = 'sha256'
    SHA512 = 'sha512'
    BLAKE2B = 'blake2b'
    BLAKE2S = 'blake2s'
