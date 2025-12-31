# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09
"""
PyFileUtilz - A comprehensive file and folder handling package
"""

from .core import FileHandler, FolderHandler
from .operations import FileOperations
from .search import FileSearch
from .compress import FileCompressor
from .validator import FileValidator

# Import hashutil if available
try:
    from .hashutil import (
        FileHasher,
        FolderHasher,
        HashComparator,
        ProgressiveFileHasher,
        HashAlgorithm,
        quick_hash,
        quick_folder_hash,
        get_available_algorithms,
    )

    HASH_AVAILABLE = True
except ImportError:
    HASH_AVAILABLE = False

    # Create stub classes to avoid import errors
    class FileHasher:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                'hashutil module not available. Install Cython to use hashing features.'
            )

    class FolderHasher:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                'hashutil module not available. Install Cython to use hashing features.'
            )


__version__ = '1.1.0'
__author__ = 'Issac Onagh'
__all__ = [
    'FileHandler',
    'FolderHandler',
    'FileOperations',
    'FileSearch',
    'FileCompressor',
    'FileValidator',
    'FileHasher',
    'FolderHasher',
    'HashComparator',
    'ProgressiveFileHasher',
    'HashAlgorithm',
    'quick_hash',
    'quick_folder_hash',
    'get_available_algorithms',
    'HASH_AVAILABLE',
]
