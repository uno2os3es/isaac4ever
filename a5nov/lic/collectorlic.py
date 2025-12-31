# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09
"""
Simple version - search current directory for license files and create database.
"""

from time import perf_counter
import os
import sqlite3
from pathlib import Path


def find_and_store_license_files():
    s = perf_counter()
    # Create database
    conn = sqlite3.connect('license_files.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS license_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filepath TEXT,
            filesize INTEGER,
            content TEXT
        )
    """)

    # Find license files
    license_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if 'license' in file.lower():
                license_files.append(Path(root) / file)

    print(f'Found {len(license_files)} license files')

    # Process files
    for file_path in license_files:
        try:
            # Try to read as text file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_size = file_path.stat().st_size

            cursor.execute(
                """
                INSERT INTO license_files (filename, filepath, filesize, content)
                VALUES (?, ?, ?, ?)
            """,
                (file_path.name, str(file_path), file_size, content),
            )

            print(f'Added: {file_path}')

        except Exception as e:
            print(f'Error processing {file_path}: {e}')

    conn.commit()
    conn.close()
    print(f'{perf_counter() - s} sec: license_files.db')


if __name__ == '__main__':
    find_and_store_license_files()
