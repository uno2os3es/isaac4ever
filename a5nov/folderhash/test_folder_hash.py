# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import time
import tempfile
from folder_hash import hash_folder, hash_folder_contents, get_folder_stats


def create_test_data():
    """Create test folder structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create subdirectories
        subdir1 = os.path.join(tmpdir, 'subdir1')
        subdir2 = os.path.join(tmpdir, 'subdir2', 'nested')
        os.makedirs(subdir2)

        # Create test files
        test_files = {
            'file1.txt': b'Hello, World!',
            'file2.dat': b'Binary data here',
            'subdir1/file3.txt': b'Content in subdirectory',
            'subdir2/nested/file4.bin': b'Deeply nested file',
        }

        for path, content in test_files.items():
            full_path = os.path.join(tmpdir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb') as f:
                f.write(content)

        return tmpdir


def main():
    print('Testing folder_hash extension...')

    # Create test data
    test_dir = create_test_data()
    print(f'Created test folder: {test_dir}')

    # Test basic hashing
    print('\n1. Testing basic folder hashing:')
    start = time.time()
    hash1 = hash_folder(test_dir)
    end = time.time()
    print(f'   Hash: {hash1}')
    print(f'   Time: {end - start:.4f}s')

    # Test content-only hashing
    print('\n2. Testing content-only hashing:')
    start = time.time()
    hash2 = hash_folder_contents(test_dir)
    end = time.time()
    print(f'   Hash: {hash2}')
    print(f'   Time: {end - start:.4f}s')

    # Test different algorithms
    print('\n3. Testing different algorithms:')
    for algo in ['md5', 'sha1', 'sha256']:
        start = time.time()
        h = hash_folder(test_dir, hash_algorithm=algo)
        end = time.time()
        print(f'   {algo.upper()}: {h} ({end - start:.4f}s)')

    # Test consistency
    print('\n4. Testing consistency:')
    hashes = [hash_folder(test_dir) for _ in range(3)]
    if all(h == hashes[0] for h in hashes):
        print('   ✓ Hashes are consistent')
    else:
        print('   ✗ Hashes are inconsistent!')

    # Get stats
    print('\n5. Folder statistics:')
    stats = get_folder_stats(test_dir)
    for key, value in stats.items():
        print(f'   {key}: {value}')

    print('\n✅ All tests completed successfully!')


if __name__ == '__main__':
    main()
