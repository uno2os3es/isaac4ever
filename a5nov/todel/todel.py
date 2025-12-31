# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os


def delete_multiline_string_from_files(search_string, directory='.'):
    # Recursively walk through the directory
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            # Only process files (skip directories)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r') as file:
                        content = file.read()

                    # Check if the string to delete exists in the file
                    if search_string in content:
                        # Remove the multiline string from the file
                        new_content = content.replace(search_string, '')

                        with open(file_path, 'w') as file:
                            file.write(new_content)
                        print(f'Deleted string from {file_path}')
                except Exception as e:
                    print(f'Error processing file {file_path}: {e}')


def read_string_to_delete(filename='todel.txt'):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except Exception as e:
        print(f'Error reading the file {filename}: {e}')
        return None


if __name__ == '__main__':
    string_to_delete = read_string_to_delete()
    if string_to_delete:
        delete_multiline_string_from_files(string_to_delete)
