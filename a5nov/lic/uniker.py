# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09
"""
Simple version - retrieve license contents and save unique lines to uniq.txt
"""

import sqlite3


def extract_unique_license_lines():
    # Database file
    db_file = 'license_files.db'

    try:
        # Connect to database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get all license contents
        cursor.execute(
            'SELECT content FROM license_files WHERE content IS NOT NULL'
        )
        results = cursor.fetchall()

        if not results:
            print('No license contents found in the database.')
            return

        # Extract all lines and get unique ones
        all_lines = set()

        for (content,) in results:
            if content:
                lines = content.split('\n')
                for line in lines:
                    cleaned_line = line.strip()
                    if (
                        cleaned_line and len(cleaned_line) > 2
                    ):  # Skip very short lines
                        all_lines.add(cleaned_line)

        # Convert to sorted list
        unique_lines = sorted(list(all_lines))

        # Save to file
        with open('uniq.txt', 'w', encoding='utf-8') as f:
            for line in unique_lines:
                f.write(f'{line}\n')

        print(
            f'Extracted {len(unique_lines)} unique lines from {len(results)} license files'
        )
        print('Saved to: uniq.txt')

        # Show some statistics
        total_lines = sum(
            len(content.split('\n')) for (content,) in results if content
        )
        print(f'Total lines processed: {total_lines}')
        print(
            f'Unique lines ratio: {len(unique_lines) / total_lines * 100:.1f}%'
        )

        conn.close()

    except sqlite3.Error as e:
        print(f'Database error: {e}')
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    extract_unique_license_lines()
