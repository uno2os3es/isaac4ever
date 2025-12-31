# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import stat
import subprocess
import sys

PREFIX = os.getenv('PREFIX', '/data/data/com.termux/files/usr')
HOME = os.path.expanduser('~')

# Directories we will examine and repair
DIRS_TO_CHECK = [
    PREFIX,
    os.path.join(PREFIX, 'bin'),
    os.path.join(PREFIX, 'lib'),
    os.path.join(PREFIX, 'etc'),
    os.path.join(PREFIX, 'share'),
    os.path.join(HOME, '.local'),
    os.path.join(HOME, '.local', 'lib'),
    os.path.join(HOME, '.local', 'bin'),
]


def is_writable(path):
    try:
        test_file = os.path.join(path, '.perm_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception:
        return False


def fix_permissions(path):
    try:
        # Make directory writable by user
        subprocess.run(['chmod', '700', path], check=True)
        print(f'[FIXED] Permissions repaired: {path}')
    except Exception as e:
        print(f'[ERROR] Could not fix {path}: {e}')


def ensure_directory(path):
    if not os.path.exists(path):
        print(f'[CREATE] Missing directory: {path}')
        try:
            os.makedirs(path)
            subprocess.run(['chmod', '700', path], check=True)
            print(f'[OK] Created and fixed: {path}')
        except Exception as e:
            print(f'[ERROR] Failed to create {path}: {e}')


def main():
    print('=== TERMUX PERMISSION DIAGNOSTIC & REPAIR TOOL ===')

    print(f'\n[INFO] PREFIX = {PREFIX}')
    print(f'[INFO] HOME   = {HOME}\n')

    for path in DIRS_TO_CHECK:
        print(f'[CHECK] {path}')

        ensure_directory(path)

        if not os.path.isdir(path):
            print(f'  [SKIP] Not a directory.')
            continue

        if is_writable(path):
            print('  [OK] Writable')
        else:
            print('  [BAD] Not writable')
            fix_permissions(path)

    print('\n=== DONE ===')
    print(
        'If errors remain, you may need to reinstall Termux if the filesystem is read-only.'
    )


if __name__ == '__main__':
    main()
