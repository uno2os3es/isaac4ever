# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from dh import *
import os

# Example usage
if __name__ == '__main__':
    # Test the functions
    test_dir = '/sdcard'

    # Get all files recursively
    all_files = get_files(test_dir)
    print(f'Found {len(all_files)} files')

    # Read text file
    for file in all_files[:5]:  # First 5 files
        if is_text_file(file):
            try:
                content = read_text_file(file)
                print(f'File: {get_fname(file)}')
                print(f'Extension: {get_ext(file)}')
                print(f'Is image: {is_image(file)}')
                print(f'Has non-English: {is_none_english(file)}')
                print(f'First 100 chars: {content[:100]}...')
                print('-' * 50)
            except Exception as e:
                print(f'Error processing {file}: {e}')

    # Get specific file types
    txt_files = get_files_by_type(test_dir, '.txt')
    py_files = get_files_by_type(test_dir, '.py')
    image_files = get_files_by_type(test_dir, '.jpg')

    print(f'Text files: {len(txt_files)}')
    print(f'Python files: {len(py_files)}')
    print(f'Image files: {len(image_files)}')
