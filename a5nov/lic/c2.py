# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09
"""
Simple version - search current directory for license files and create database.
"""

from time import perf_counter
import os
from pathlib import Path
import dh

EXCLUDED = ['.svg', '.py', '.c', '.h', '.cpp', '.hpp']


def write_list_to_files(string_list, output_dir='output'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    created_files = []

    for i, content in enumerate(string_list):
        # Create filename with numbering
        filename = f'file_{i + 1}.txt'
        filepath = os.path.join(output_dir, filename)

        # Write content to file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        created_files.append(filepath)
        print(f'Created: {filepath}')
    return created_files


def find_and_store_license_files():
    s = perf_counter()
    pth = '/data/data/com.termux/files/usr/share/LICENSES'
    license_files = dh.get_files(pth)
    for file in license_files:
        if os.path.islink(file):
            continue
        if ('license' in file.lower()) and Path(file).suffix not in EXCLUDED:
            license_files.append(file)

    print(f'Found {len(license_files)} license files')
    uniqez = []
    # Process files
    for file_path in license_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content not in uniqz:
                uniqz.append(content)

    write_list_to_files(uniqz, 'output')


if __name__ == '__main__':
    find_and_store_license_files()
