# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import mimetypes
from typing import List, Dict, Any
from .core import FileHandler, FolderHandler


class FileValidator:
    """File validation utilities - No external dependencies"""

    # Common file signatures (magic numbers)
    FILE_SIGNATURES = {
        'png': b'\x89PNG\r\n\x1a\n',
        'jpg': b'\xff\xd8\xff',
        'jpeg': b'\xff\xd8\xff',
        'gif': b'GIF8',
        'pdf': b'%PDF-',
        'zip': b'PK\x03\x04',
        'exe': b'MZ',
        'mp3': b'ID3',
        'mp4': b'\x00\x00\x00\x18ftyp',
        'avi': b'RIFF',
        'wav': b'RIFF',
        'bmp': b'BM',
        'tiff': b'II*\x00' if os.name == 'nt' else b'MM\x00*',
        'ico': b'\x00\x00\x01\x00',
        'psd': b'8BPS',
        'webp': b'RIFF',
        'gz': b'\x1f\x8b',
        'tar': b'ustar',
        'rar': b'Rar!\x1a\x07',
        '7z': b'7z\xbc\xaf\x27\x1c',
        'json': b'{',  # JSON often starts with {
        'xml': b'<?xml',
        'html': b'<!DOCTYPE' if os.name == 'nt' else b'<html',
    }

    # MIME type mappings
    MIME_MAPPINGS = {
        'image': [
            '.jpg',
            '.jpeg',
            '.png',
            '.gif',
            '.bmp',
            '.tiff',
            '.webp',
            '.svg',
            '.ico',
        ],
        'text': [
            '.txt',
            '.csv',
            '.json',
            '.xml',
            '.html',
            '.htm',
            '.css',
            '.js',
            '.py',
            '.cpp',
            '.c',
            '.h',
            '.java',
            '.php',
            '.rb',
            '.pl',
            '.sh',
            '.bat',
            '.md',
        ],
        'audio': ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma'],
        'video': [
            '.mp4',
            '.avi',
            '.mkv',
            '.mov',
            '.wmv',
            '.flv',
            '.webm',
            '.m4v',
        ],
        'application': [
            '.pdf',
            '.doc',
            '.docx',
            '.xls',
            '.xlsx',
            '.ppt',
            '.pptx',
            '.zip',
            '.tar',
            '.gz',
            '.7z',
            '.rar',
            '.exe',
            '.msi',
        ],
        'font': ['.ttf', '.otf', '.woff', '.woff2'],
    }

    @staticmethod
    def validate_file_exists(file_path: str) -> bool:
        """Validate that file exists"""
        return FileHandler(file_path).exists()

    @staticmethod
    def validate_folder_exists(folder_path: str) -> bool:
        """Validate that folder exists"""
        return FolderHandler(folder_path).exists()

    @staticmethod
    def validate_file_size(
        file_path: str, min_size: int = 0, max_size: int = None
    ) -> bool:
        """Validate file size constraints"""
        try:
            file_handler = FileHandler(file_path)
            size = file_handler.get_size()

            if size < min_size:
                return False
            if max_size and size > max_size:
                return False

            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def validate_file_extension(
        file_path: str, allowed_extensions: List[str]
    ) -> bool:
        """Validate file extension"""
        file_handler = FileHandler(file_path)
        extension = file_handler.get_extension()

        # Normalize extensions
        allowed_extensions = [
            ext.lower() if ext.startswith('.') else '.' + ext.lower()
            for ext in allowed_extensions
        ]

        return extension in allowed_extensions

    @staticmethod
    def validate_file_type(file_path: str, expected_type: str = None) -> bool:
        """Validate file type without external dependencies"""
        if not expected_type:
            return True

        # Get file extension
        file_handler = FileHandler(file_path)
        extension = file_handler.get_extension().lower()

        # Check against our MIME mappings
        for category, extensions in FileValidator.MIME_MAPPINGS.items():
            if extension in extensions:
                if expected_type.startswith(category):
                    return True

        # Fallback to mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and expected_type:
            return mime_type.startswith(expected_type)

        return False

    @staticmethod
    def validate_file_signature(
        file_path: str, expected_extensions: List[str] = None
    ) -> bool:
        """Validate file by checking magic bytes (file signatures)"""
        if not expected_extensions:
            return True

        try:
            with open(file_path, 'rb') as f:
                file_header = f.read(
                    16
                )  # Read first 16 bytes for better detection

            for ext in expected_extensions:
                ext = ext.lower().lstrip('.')
                if ext in FileValidator.FILE_SIGNATURES:
                    signature = FileValidator.FILE_SIGNATURES[ext]
                    if file_header.startswith(signature):
                        return True

            # If no specific signature found, check if it's a text file
            if any(
                ext
                in [
                    '.txt',
                    '.csv',
                    '.json',
                    '.xml',
                    '.html',
                    '.js',
                    '.css',
                    '.py',
                ]
                for ext in expected_extensions
            ):
                try:
                    # Try to decode as UTF-8 to check if it's text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read(1024)
                    return True
                except UnicodeDecodeError:
                    pass

            return False
        except Exception:
            return False

    @staticmethod
    def validate_file_permissions(
        file_path: str,
        readable: bool = True,
        writable: bool = False,
        executable: bool = False,
    ) -> bool:
        """Validate file permissions"""
        file_handler = FileHandler(file_path)

        if not file_handler.exists():
            return False

        if readable and not os.access(file_path, os.R_OK):
            return False
        if writable and not os.access(file_path, os.W_OK):
            return False
        if executable and not os.access(file_path, os.X_OK):
            return False

        return True

    @staticmethod
    def validate_folder_permissions(
        folder_path: str,
        readable: bool = True,
        writable: bool = False,
        executable: bool = True,
    ) -> bool:
        """Validate folder permissions"""
        folder_handler = FolderHandler(folder_path)

        if not folder_handler.exists():
            return False

        if readable and not os.access(folder_path, os.R_OK):
            return False
        if writable and not os.access(folder_path, os.W_OK):
            return False
        if executable and not os.access(folder_path, os.X_OK):
            return False

        return True

    @staticmethod
    def validate_path_safety(file_path: str) -> bool:
        """Validate that path is safe (no path traversal attempts)"""
        try:
            absolute_path = os.path.abspath(file_path)
            normalized_path = os.path.normpath(file_path)

            # Check for path traversal patterns
            path_parts = normalized_path.split(os.sep)
            if '..' in path_parts:
                return False

            # Check for absolute paths that might escape
            if os.path.isabs(file_path) and not absolute_path.startswith(
                os.path.abspath(os.sep)
            ):
                return False

            # Check if path is within current directory or allowed paths
            current_dir = os.path.abspath(os.getcwd())
            if not absolute_path.startswith(current_dir):
                # Allow paths in home directory
                home_dir = os.path.expanduser('~')
                if not absolute_path.startswith(os.path.abspath(home_dir)):
                    return False

            return True
        except Exception:
            return False

    @staticmethod
    def validate_filename(
        filename: str,
        max_length: int = 255,
        allow_spaces: bool = True,
        allow_special: bool = True,
    ) -> bool:
        """Validate filename for safety and compatibility"""
        if not filename or len(filename) > max_length:
            return False

        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if not allow_special:
            invalid_chars.extend(
                [
                    '!',
                    '@',
                    '#',
                    '$',
                    '%',
                    '^',
                    '&',
                    '(',
                    ')',
                    '=',
                    '+',
                    '[',
                    ']',
                    '{',
                    '}',
                ]
            )

        if not allow_spaces:
            invalid_chars.append(' ')

        for char in invalid_chars:
            if char in filename:
                return False

        # Check for reserved names (Windows)
        reserved_names = [
            'CON',
            'PRN',
            'AUX',
            'NUL',
            'COM1',
            'COM2',
            'COM3',
            'COM4',
            'COM5',
            'COM6',
            'COM7',
            'COM8',
            'COM9',
            'LPT1',
            'LPT2',
            'LPT3',
            'LPT4',
            'LPT5',
            'LPT6',
            'LPT7',
            'LPT8',
            'LPT9',
        ]
        if (
            os.name == 'nt'
            and filename.upper().split('.')[0] in reserved_names
        ):
            return False

        return True

    @staticmethod
    def get_file_signature(file_path: str) -> str:
        """Get file signature (magic bytes) as string"""
        try:
            with open(file_path, 'rb') as f:
                signature = f.read(8)
            return signature.hex().upper()
        except Exception:
            return ''

    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """Detect file type using signatures and extensions"""
        file_handler = FileHandler(file_path)
        extension = file_handler.get_extension().lower().lstrip('.')

        # Check signature first
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)

            for file_type, signature in FileValidator.FILE_SIGNATURES.items():
                if header.startswith(signature):
                    return file_type
        except Exception:
            pass

        # Fallback to extension-based detection
        for category, extensions in FileValidator.MIME_MAPPINGS.items():
            if extension in [ext.lstrip('.') for ext in extensions]:
                return category

        return 'unknown'

    @staticmethod
    def comprehensive_validation(
        file_path: str, rules: Dict[str, Any] = None
    ) -> Dict[str, bool]:
        """Comprehensive file validation with multiple rules"""
        default_rules = {
            'exists': True,
            'min_size': 0,
            'max_size': None,
            'allowed_extensions': None,
            'expected_type': None,
            'readable': True,
            'writable': False,
            'safe_path': True,
            'validate_signature': False,
            'validate_filename': False,
        }

        if rules:
            default_rules.update(rules)

        rules = default_rules
        results = {}

        # Existence check
        results['exists'] = FileValidator.validate_file_exists(file_path)
        if not results['exists']:
            # If file doesn't exist, other checks are irrelevant
            for key in rules.keys():
                if key not in results:
                    results[key] = False
            return results

        # Size validation
        results['size_valid'] = FileValidator.validate_file_size(
            file_path, rules.get('min_size', 0), rules.get('max_size')
        )

        # Extension validation
        if rules.get('allowed_extensions'):
            results['extension_valid'] = FileValidator.validate_file_extension(
                file_path, rules['allowed_extensions']
            )
        else:
            results['extension_valid'] = True

        # File type validation
        if rules.get('expected_type'):
            results['type_valid'] = FileValidator.validate_file_type(
                file_path, rules['expected_type']
            )
        else:
            results['type_valid'] = True

        # File signature validation
        if rules.get('validate_signature') and rules.get('allowed_extensions'):
            results['signature_valid'] = FileValidator.validate_file_signature(
                file_path, rules['allowed_extensions']
            )
        else:
            results['signature_valid'] = True

        # Permission validation
        results['permissions_valid'] = FileValidator.validate_file_permissions(
            file_path,
            rules.get('readable', True),
            rules.get('writable', False),
        )

        # Path safety validation
        results['path_safe'] = FileValidator.validate_path_safety(file_path)

        # Filename validation
        if rules.get('validate_filename'):
            filename = os.path.basename(file_path)
            results['filename_valid'] = FileValidator.validate_filename(
                filename
            )
        else:
            results['filename_valid'] = True

        # Overall validation
        results['all_valid'] = all(results.values())

        return results

    @staticmethod
    def validate_image_file(
        file_path: str, max_dimensions: tuple = None
    ) -> Dict[str, Any]:
        """Specialized validation for image files"""
        results = {
            'is_image': False,
            'format': 'unknown',
            'dimensions': None,
            'file_size': 0,
        }

        try:
            # Basic validation
            basic_validation = FileValidator.comprehensive_validation(
                file_path,
                {
                    'allowed_extensions': [
                        '.jpg',
                        '.jpeg',
                        '.png',
                        '.gif',
                        '.bmp',
                        '.webp',
                    ],
                    'validate_signature': True,
                },
            )

            if not basic_validation['all_valid']:
                return results

            # Try to get image dimensions using PIL if available
            try:
                from PIL import Image

                with Image.open(file_path) as img:
                    results['is_image'] = True
                    results['format'] = img.format
                    results['dimensions'] = img.size

                    if max_dimensions:
                        width, height = img.size
                        max_width, max_height = max_dimensions
                        results['within_dimensions'] = (
                            width <= max_width and height <= max_height
                        )

            except ImportError:
                # PIL not available, use basic detection
                results['is_image'] = basic_validation['signature_valid']
                results['format'] = FileValidator.detect_file_type(file_path)

            # Get file size
            file_handler = FileHandler(file_path)
            results['file_size'] = file_handler.get_size()

        except Exception as e:
            results['error'] = str(e)

        return results
