import datetime
import io
import os
import string
import subprocess
from pathlib import Path
import chardet
import magic
from importlib_metadata import files


def detect_encoding(filename, limit_byte_check=-1):
    encoding = _detect_encoding_from_file(filename)
    if encoding == 'utf-8-sig':
        return encoding
    try:
        with open_with_encoding(filename, encoding=encoding) as test_file:
            test_file.read(limit_byte_check)
        return encoding
    except (LookupError, SyntaxError, UnicodeDecodeError):
        return 'latin-1'


# ***********************************************


def open_with_encoding(filename, mode='r', encoding=None, limit_byte_check=-1):
    if not encoding:
        encoding = detect_encoding(filename, limit_byte_check=limit_byte_check)
    return io.open(filename, mode=mode, encoding=encoding, newline='')


# ***********************************************


def readlines_from_file(filename):
    with open_with_encoding(filename) as input_file:
        return input_file.readlines()


# ***********************************************


def read_text_file(fpath):
    """
    Read text file contents with automatic encoding detection
    Returns: str - file contents
    """
    try:
        # First try to detect encoding
        with open(fpath, 'rb') as file:
            raw_data = file.read()
            encoding = chardet.detect(raw_data)['encoding']

        # Read with detected encoding, fallback to utf-8
        with open(
            fpath, 'r', encoding=encoding or 'utf-8', errors='replace'
        ) as file:
            return file.read()
    except Exception as e:
        raise Exception(f'Error reading text file {fpath}: {str(e)}')


# ***********************************************


def read_binary_file(fpath):
    """
    Read binary file contents
    Returns: bytes - binary file contents
    """
    try:
        with open(fpath, 'rb') as file:
            return file.read()
    except Exception as e:
        raise Exception(f'Error reading binary file {fpath}: {str(e)}')


# ***********************************************


def get_dirs(fpath):
    """
    Get all dirs in a given path recursively
    Returns: list - list of dir paths
    """
    try:
        path = Path(fpath)
        if not path.exists():
            raise FileNotFoundError(f'Path does not exist: {fpath}')

        if path.is_file():
            return []

        dirz = []
        for item in path.rglob('*'):
            if item.is_dir():
                dirz.append(str(item))
        return dirz

    except Exception as e:
        raise Exception(f'Error getting dirs from {fpath}: {str(e)}')


# ***********************************************


def get_files(fpath):
    """
    Get all files in a given path recursively
    Returns: list - list of file paths
    """
    try:
        path = Path(fpath)
        if not path.exists():
            raise FileNotFoundError(f'Path does not exist: {fpath}')

        if path.is_file():
            return [str(path)]

        files = []
        for item in path.rglob('*'):
            if item.is_file():
                files.append(str(item))
        return files
    except Exception as e:
        raise Exception(f'Error getting files from {fpath}: {str(e)}')


# ***********************************************


def get_ext(fpath):
    """
    Get extension of a file path
    Returns: str - file extension (including .tar.gz, .txt.gz, etc.)
    """
    try:
        path = Path(fpath)
        if not path.is_file():
            return ''
        suffix = path.suffix
        return suffix.lower()
    except Exception as e:
        raise Exception(f'Error getting extension for {fpath}: {str(e)}')


# ***********************************************


def get_fname(fpath):
    """
    Get file name from path
    Returns: str - file name
    """
    return Path(fpath).name


# ***********************************************


def get_files_by_type(dir_path, ext):
    """
    Get files by extension in directory recursively
    Returns: list - list of matching file paths
    """
    try:
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f'Directory does not exist: {dir_path}')

        # Normalize extension
        ext = ext.lower()
        if not ext.startswith('.'):
            ext = '.' + ext

        matching_files = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = get_ext(file_path)

                # Handle compound extensions
                if file_ext == ext:
                    matching_files.append(file_path)
                # Handle case where we might want just the last part of compound extension
                elif '.' in file_ext and file_ext != ext:
                    parts = file_ext.split('.')
                    if '.' + parts[-1] == ext:
                        matching_files.append(file_path)

        return matching_files
    except Exception as e:
        raise Exception(
            f'Error getting files by type from {dir_path}: {str(e)}'
        )


# ***********************************************


def is_image(fpath):
    """
    Check if file is an image
    Returns: bool - True if file is an image
    """
    try:
        if not os.path.isfile(fpath):
            return False

        # Common image extensions
        image_extensions = {
            '.jpg',
            '.jpeg',
            '.png',
            '.gif',
            '.bmp',
            '.tiff',
            '.tif',
            '.webp',
            '.svg',
            '.ico',
            '.raw',
            '.heic',
        }

        file_ext = get_ext(fpath)
        return file_ext in image_extensions
    except Exception as e:
        print(f'Error checking if {fpath} is image: {str(e)}')
        return False


# ***********************************************


def read_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


# ***********************************************


def is_text_file(fpath):
    """
    Check if file is a text file
    Returns: bool - True if file is a text file
    """
    try:
        if not os.path.isfile(fpath):
            return False

        # Common text file extensions
        text_extensions = {
            '.txt',
            '.csv',
            '.json',
            '.xml',
            '.html',
            '.htm',
            '.css',
            '.js',
            '.py',
            '.java',
            '.c',
            '.cpp',
            '.h',
            '.md',
            '.rst',
            '.log',
            '.conf',
            '.config',
            '.ini',
            '.yml',
            '.yaml',
        }

        file_ext = get_ext(fpath)
        if file_ext in text_extensions:
            return True

        # Try to read first few bytes to check if it's text
        try:
            with open(fpath, 'rb') as file:
                sample = file.read(1024)
                # Check if sample contains null bytes (binary indicator)
                if b'\x00' in sample:
                    return False
                # Try to decode as UTF-8
                sample.decode('utf-8', errors='ignore')
                return True
        except:
            return False

    except Exception as e:
        print(f'Error checking if {fpath} is text file: {str(e)}')
        return False


# ***********************************************


def is_none_english(fpath):
    """
    Check if file contains any non-English content
    Returns: bool - True if file contains non-English characters
    """
    try:
        if not os.path.isfile(fpath):
            return False

        # Skip binary files
        if not is_text_file(fpath):
            return False

        content = read_text_file(fpath)

        # Basic English character set (ASCII printable + some common symbols)
        english_chars = set(
            string.printable + '£€¥¢§©®°±µ¶·¿®™´¨ˆ˜¯˘˙˚¸˝˛ˇ—–•†‡…‰′″‾⁄ℵℑℜ℘ℑ'
        )

        for char in content:
            if char not in english_chars and not char.isspace():
                return True

        return False

    except Exception as e:
        print(f'Error checking non-English content in {fpath}: {str(e)}')
        return False


# ***********************************************


def get_file_size(fpath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(fpath)
    except:
        return 0


# ***********************************************


def get_file_info(fpath):
    """Get comprehensive file information"""
    try:
        path = Path(fpath)
        stat = path.stat()

        return {
            'path': str(path),
            'name': get_fname(fpath),
            'extension': get_ext(fpath),
            'size': get_file_size(fpath),
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'exists': path.exists(),
            'is_image': is_image(fpath),
            'is_text': is_text_file(fpath),
            'has_non_english': is_none_english(fpath),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
        }
    except Exception as e:
        return {'error': str(e)}
    finally:
        return 0


# ***********************************************


def which(exe):
    path = os.getenv('PATH')
    for folder in path.split(os.path.pathsep):
        candidate = os.path.join(folder, exe)
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return os.path.abspath(candidate)
    return None


# ***********************************************


def get_script(fname):
    for file in files(fname):
        if not file.stem == fname:
            continue
        if file.parent.name != 'bin':
            continue
        return str(file.locate().resolve(strict=True))
    raise LookupError(f"Can't find {fname} script")


# ***********************************************


def test_script(fn):
    script = get_script(fn)
    subprocess.check_call([script, '--version'])
    assert script == which(fn)


# ***********************************************


def gregorian_to_jalali(gy, gm, gd):
    g_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1

    g_day_no = (
        365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    )
    g_day_no += g_days[gm2] + gd2

    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    # calculate jm and jd
    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        j_day_no -= 186
        jm = 7 + j_day_no // 30
        jd = 1 + j_day_no % 30

    return jy, jm, jd


# ***********************************************


def to_persian_digits(s):
    return s.translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))


# ***********************************************


def georgian_to_hijri(year, month, day):
    jy, jm, jd = gregorian_to_jalali(year, month, day)

    # weekday
    weekday_index = datetime.date(year, month, day).weekday()
    weekday = weekdays[weekday_index]

    # build result in Persian
    result = f'{weekday} {to_persian_digits(str(jd))} {months[jm - 1]} {to_persian_digits(str(jy))}'
    return result
