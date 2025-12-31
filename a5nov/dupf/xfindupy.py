# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import json
import argparse
import multiprocessing as mp
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
import xxhash

# ----------------------------------------
# GLOBAL STORAGE
# ----------------------------------------

SKIPPED_PATHS = []
EXCLUDED_DIRS = {'.git', '.venv', 'venv', 'usr'}

# ----------------------------------------
# FILE HASHING (Worker Function)
# ----------------------------------------


def hash_file_mp(path: str, chunk_size: int = 8192):
    """
    Worker function for multiprocessing.
    Computes xxhash64 hash of a file. Returns (path, hash).
    """
    path = Path(path)
    hasher = xxhash.xxh64()

    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)

    except (PermissionError, OSError):
        return path, None  # Skip silently in worker

    return path, hasher.hexdigest()


# ----------------------------------------
# FILE COLLECTION
# ----------------------------------------


def collect_all_files(directory: Path):
    """
    Collect files recursively, skipping excluded dirs.
    """
    files = []
    for root, dirs, fs in os.walk(directory, onerror=lambda e: None):
        # Remove excluded dirs in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for f in fs:
            full = Path(root) / f
            files.append(full)

    return files


# ----------------------------------------
# STAGE 1: Prefilter by size
# ----------------------------------------


def group_by_size(files):
    groups = defaultdict(list)
    for f in files:
        try:
            size = f.stat().st_size
            groups[size].append(f)
        except (PermissionError, OSError):
            SKIPPED_PATHS.append(str(f))
    return groups


# ----------------------------------------
# STAGE 2: Multiprocessing Hashing
# ----------------------------------------


def hash_groups_in_parallel(groups):
    """
    Accepts dict {size: [paths...]}, where len(paths) > 1.
    Uses multiprocessing to hash all candidates.
    """
    candidates = []
    for size, paths in groups.items():
        if len(paths) > 1:  # only these need hashing
            candidates.extend(paths)

    if not candidates:
        return {}

    print(f'\n⚡ Hashing {len(candidates)} candidate files...\n')

    # MP pool
    with mp.Pool(processes=mp.cpu_count()) as pool:
        results = list(
            tqdm(
                pool.imap_unordered(
                    hash_file_mp, [str(p) for p in candidates]
                ),
                total=len(candidates),
                unit='file',
                desc='Hashing Files',
            )
        )

    # Build hash groups
    hash_groups = defaultdict(list)
    for path, h in results:
        if h is None:
            SKIPPED_PATHS.append(str(path))
            continue
        hash_groups[h].append(str(path))

    # Filter only duplicates
    return {h: ps for h, ps in hash_groups.items() if len(ps) > 1}


# ----------------------------------------
# DUPLICATE REMOVAL
# ----------------------------------------


def auto_delete_duplicates(dups):
    """
    Deletes all duplicate files EXCEPT the first one in each group.
    """
    print('\n🔥 AUTO-DELETE MODE: Removing duplicates...\n')

    deleted_count = 0

    for h, files in dups.items():
        keep = files[0]
        duplicates = files[1:]

        for f in duplicates:
            try:
                os.remove(f)
                deleted_count += 1
                print(f'🗑 Deleted: {f}')
            except Exception as e:
                print(f'⚠️ Could not delete {f}: {e}')

    print(f'\n✅ Auto-delete complete. {deleted_count} duplicates removed.\n')


# ----------------------------------------
# DUPLICATE REPORTING
# ----------------------------------------


def print_duplicates(dups):
    if not dups:
        print('🎉 No duplicates found!')
        return

    print('\n🔍 Duplicate Files Found:\n')
    for i, (h, paths) in enumerate(dups.items(), start=1):
        print(f'Group {i} (hash={h[:12]}...):')
        for p in paths:
            print(f'   • {p}')
        print('-' * 40)


def print_skipped():
    if SKIPPED_PATHS:
        print('\n⚠️ Skipped due to permission errors:')
        for p in SKIPPED_PATHS:
            print(f'   • {p}')


# ----------------------------------------
# MAIN LOGIC
# ----------------------------------------


def main():
    parser = argparse.ArgumentParser(description='Ultra-Fast Duplicate Finder')
    parser.add_argument('folder', help='Folder to scan')
    parser.add_argument(
        '-a',
        '--auto-delete',
        action='store_true',
        help='Automatically delete duplicates',
    )
    parser.add_argument(
        '-o', '--output', default='duplicates.json', help='JSON export path'
    )
    args = parser.parse_args()

    target = Path(args.folder)
    if not target.exists():
        print('❌ Folder does not exist.')
        return

    print('📁 Collecting files...')
    all_files = collect_all_files(target)

    print(f'📦 Total files detected: {len(all_files)}')

    # Stage 1: Prefilter
    print('\n🔎 Prefiltering by file size...\n')
    size_groups = group_by_size(all_files)

    # Stage 2: Hashing with multiprocessing
    duplicates = hash_groups_in_parallel(size_groups)

    # Report
    print_duplicates(duplicates)
    print_skipped()

    # Save JSON
    if duplicates:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(duplicates, f, indent=2)
        print(f'\n📄 Results saved to {args.output}')

        # Auto delete
        if args.auto_delete:
            auto_delete_duplicates(duplicates)


if __name__ == '__main__':
    main()
