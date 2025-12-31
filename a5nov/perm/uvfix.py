# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os

HOME = os.path.expanduser('~')

UV_CACHE = os.path.join(HOME, '.uv-cache')
UV_TEMP = os.path.join(HOME, '.uv-tmp')


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    os.chmod(path, 0o700)


def main():
    ensure_dir(UV_CACHE)
    ensure_dir(UV_TEMP)

    print('=== UV ENVIRONMENT VARIABLES TO FIX TERMUX/ANDROID7 ===')
    print(f'export UV_CACHE_DIR={UV_CACHE}')
    print(f'export UV_TEMP_DIR={UV_TEMP}')
    print('Add these two lines to ~/.bashrc or ~/.zshrc.')
    print('========================================================')


if __name__ == '__main__':
    main()
