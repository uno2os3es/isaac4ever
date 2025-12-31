# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import hashlib
import timeit
from stringzilla import Sha256, File


# Function to compute SHA256 using hashlib for a single file
def compute_hashlib_sha256(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):  # Read in chunks
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


# Function to compute SHA256 using stringzilla for a single file
def compute_stringzilla_sha256(file_path):
    mapped_file = File(file_path)
    checksum = Sha256().update(mapped_file).hexdigest()
    return checksum


# Function to compare both methods and print the time difference
def compare_hashes_in_folder(folder_path):
    # Get all the files in the folder
    files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    # Start measuring the time for hashlib
    hashlib_times = []
    stringzilla_times = []

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        # Measure the time for hashlib
        start_time = timeit.default_timer()
        hashlib_checksum = compute_hashlib_sha256(file_path)
        hashlib_times.append(timeit.default_timer() - start_time)

        # Measure the time for stringzilla
        start_time = timeit.default_timer()
        stringzilla_checksum = compute_stringzilla_sha256(file_path)
        stringzilla_times.append(timeit.default_timer() - start_time)

        # Print the results for each file
        print(f'File: {file_name}')
        print(f'  Hashlib SHA256: {hashlib_checksum}')
        print(f'  Stringzilla SHA256: {stringzilla_checksum}')
        print(f'  Time (hashlib): {hashlib_times[-1]:.6f} seconds')
        print(f'  Time (stringzilla): {stringzilla_times[-1]:.6f} seconds')
        print(
            f'  Difference in time: {abs(hashlib_times[-1] - stringzilla_times[-1]):.6f} seconds\n'
        )

    # Print overall time comparison
    total_hashlib_time = sum(hashlib_times)
    total_stringzilla_time = sum(stringzilla_times)

    print('Summary of Time Comparison:')
    print(f'Total time for Hashlib: {total_hashlib_time:.6f} seconds')
    print(f'Total time for Stringzilla: {total_stringzilla_time:.6f} seconds')
    print(
        f'Total time difference: {abs(total_hashlib_time - total_stringzilla_time):.6f} seconds'
    )


# Specify the folder path
folder_path = '/sdcard'
# Replace with the path to your folder

# Run the comparison for all files in the folder
compare_hashes_in_folder(folder_path)
