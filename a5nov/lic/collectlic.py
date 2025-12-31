# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09
"""
Script to find text files with 'license' in their names and store contents in SQLite database.
"""

import os
import sqlite3
import argparse
from pathlib import Path


def is_text_file(file_path):
    """
    Check if a file is text-based by attempting to read it as text.
    Returns True if readable as text, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Read first 1KB to check if it's text
        return True
    except (UnicodeDecodeError, IOError, OSError):
        return False


def get_file_contents(file_path):
    """
    Read the contents of a text file.
    Returns the content as string, or None if error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f'Error reading {file_path}: {e}')
        return None


def create_database(db_path):
    """
    Create SQLite database and table for storing license file information.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS license_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            filesize INTEGER,
            content TEXT,
            found_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    return conn


def find_license_files(root_dir):
    """
    Recursively find files with 'license' in their name in the given directory.
    """
    license_files = []
    root_path = Path(root_dir)

    # Case-insensitive search for files containing 'license' in name
    pattern = '*license*'

    for file_path in root_path.rglob(pattern):
        if file_path.is_file():
            license_files.append(file_path)

    # Also check case variations
    for file_path in root_path.rglob('*'):
        if file_path.is_file() and 'license' in file_path.name.lower():
            if file_path not in license_files:  # Avoid duplicates
                license_files.append(file_path)

    return license_files


def main():
    parser = argparse.ArgumentParser(
        description='Find license files and store in SQLite database'
    )
    parser.add_argument(
        '--directory',
        '-d',
        default='.',
        help='Directory to search (default: current directory)',
    )
    parser.add_argument(
        '--output',
        '-o',
        default='license_files.db',
        help='Output SQLite database file (default: license_files.db)',
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='Verbose output'
    )

    args = parser.parse_args()

    # Validate directory
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist.")
        return 1

    print(f'Searching for license files in: {os.path.abspath(args.directory)}')

    # Find license files
    license_files = find_license_files(args.directory)

    if not license_files:
        print('No license files found.')
        return 0

    print(f"Found {len(license_files)} files with 'license' in name.")

    # Create database
    try:
        conn = create_database(args.output)
        cursor = conn.cursor()
    except Exception as e:
        print(f'Error creating database: {e}')
        return 1

    # Process files
    processed_count = 0
    skipped_count = 0

    for file_path in license_files:
        if args.verbose:
            print(f'Processing: {file_path}')

        # Check if file is text-based
        if not is_text_file(file_path):
            if args.verbose:
                print(f'  Skipping non-text file: {file_path}')
            skipped_count += 1
            continue

        # Get file contents
        content = get_file_contents(file_path)
        if content is None:
            skipped_count += 1
            continue

        # Insert into database
        try:
            file_size = file_path.stat().st_size
            cursor.execute(
                """
                INSERT INTO license_files (filename, filepath, filesize, content)
                VALUES (?, ?, ?, ?)
            """,
                (file_path.name, str(file_path), file_size, content),
            )

            processed_count += 1

        except Exception as e:
            print(f'Error inserting {file_path} into database: {e}')
            skipped_count += 1

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f'\nProcessing complete:')
    print(f'  Files processed successfully: {processed_count}')
    print(f'  Files skipped: {skipped_count}')
    print(f'  Database saved as: {args.output}')

    return 0


def query_database(db_path):
    """
    Example function to query the created database.
    """
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' does not exist.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count total records
    cursor.execute('SELECT COUNT(*) FROM license_files')
    total = cursor.fetchone()[0]
    print(f'Total license files in database: {total}')

    # Show file list
    cursor.execute('SELECT filename, filepath, filesize FROM license_files')
    files = cursor.fetchall()

    print('\nFiles in database:')
    for filename, filepath, filesize in files:
        print(f'  {filename} ({filesize} bytes)')
        print(f'    Path: {filepath}')

    conn.close()


if __name__ == '__main__':
    exit(main())
