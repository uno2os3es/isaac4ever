# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import json
from collections import defaultdict
from pathlib import Path
from tqdm import tqdm
import xxhash  # ultra-fast hashing

SKIPPED_PATHS = []  # store permission-denied paths


def hash_file(path: Path, chunk_size: int = 8192) -> str:
    """
    Compute xxhash64 for a file efficiently with a tqdm progress bar.
    Automatically skips files that cannot be accessed.
    """
    hasher = xxhash.xxh64()

    try:
        file_size = path.stat().st_size

        with (
            open(path, 'rb') as f,
            tqdm(
                total=file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=f'Hashing {path.name}',
                leave=False,
            ) as pbar,
        ):
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
                pbar.update(len(chunk))

    except (PermissionError, OSError):
        SKIPPED_PATHS.append(str(path))
        return None

    return hasher.hexdigest()


def collect_all_files(directory: Path):
    """
    Collect all file paths before hashing to allow an overall progress bar.
    Automatically ignores unreadable directories.
    """
    all_files = []
    for root, dirs, files in os.walk(directory, onerror=lambda e: None):
        for f in files:
            all_files.append(Path(root) / f)
    return all_files


def find_duplicate_files(directory: str):
    directory = Path(directory)
    if not directory.exists():
        raise ValueError(f'Directory does not exist: {directory}')

    all_files = collect_all_files(directory)
    duplicates = defaultdict(list)

    print(f'📁 Scanning {len(all_files)} files...\n')

    for file_path in tqdm(all_files, desc='Overall Progress', unit='file'):
        file_hash = hash_file(file_path)
        if file_hash:
            duplicates[file_hash].append(str(file_path))

    # Keep only those with duplicates
    return {h: p for h, p in duplicates.items() if len(p) > 1}


def print_duplicates(dups: dict):
    if not dups:
        print('🎉 No duplicates found!')
        return

    print('\n🔍 Duplicate Files Found:\n')
    for i, (h, paths) in enumerate(dups.items(), start=1):
        print(f'Group {i} (hash={h[:12]}...):')
        for p in paths:
            print(f'   • {p}')
        print('-' * 40)


def print_skipped_paths():
    if not SKIPPED_PATHS:
        return

    print('\n⚠️ Skipped due to permission errors:')
    for p in SKIPPED_PATHS:
        print(f'   • {p}')


def export_to_json(dups: dict, output='duplicates.json'):
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(dups, f, indent=2)
    print(f'📦 Results saved to {output}')


if __name__ == '__main__':
    folder = input('Enter folder to scan: ').strip()
    duplicates = find_duplicate_files(folder)
    print_duplicates(duplicates)
    print_skipped_paths()

    if duplicates:
        save = input('Export results to JSON? (y/n): ').lower().strip()
        if save == 'y':
            export_to_json(duplicates)
