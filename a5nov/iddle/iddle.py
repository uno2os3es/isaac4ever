# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import subprocess
import tempfile
from pathlib import Path


class SimplePythonIDE:
    def __init__(self):
        self.editor = 'nano'  # or "vim" if you prefer
        self.workspace = Path.home() / 'python_projects'
        self.workspace.mkdir(exist_ok=True)

    def create_file(self, filename):
        filepath = self.workspace / filename
        subprocess.run([self.editor, str(filepath)])
        return filepath

    def run_python_file(self, filepath):
        if filepath.exists():
            print(f'\n--- Running {filepath} ---')
            result = subprocess.run(
                ['python', str(filepath)], capture_output=True, text=True
            )
            print(result.stdout)
            if result.stderr:
                print('Errors:', result.stderr)
            print('--- Execution completed ---\n')

    def interactive_menu(self):
        while True:
            print('\n=== Simple Python IDE ===')
            print('1. Create new Python file')
            print('2. List existing files')
            print('3. Run a Python file')
            print('4. Exit')

            choice = input('\nChoose an option: ').strip()

            if choice == '1':
                filename = input('Enter filename (e.g., script.py): ')
                if not filename.endswith('.py'):
                    filename += '.py'
                filepath = self.create_file(filename)
                print(f'Created: {filepath}')

            elif choice == '2':
                files = list(self.workspace.glob('*.py'))
                if files:
                    print('\nPython files:')
                    for i, f in enumerate(files, 1):
                        print(f'{i}. {f.name}')
                else:
                    print('No Python files found.')

            elif choice == '3':
                files = list(self.workspace.glob('*.py'))
                if files:
                    for i, f in enumerate(files, 1):
                        print(f'{i}. {f.name}')
                    try:
                        file_num = int(input('Select file number: ')) - 1
                        if 0 <= file_num < len(files):
                            self.run_python_file(files[file_num])
                    except (ValueError, IndexError):
                        print('Invalid selection')
                else:
                    print('No Python files found.')

            elif choice == '4':
                print('Goodbye!')
                break
            else:
                print('Invalid option')


if __name__ == '__main__':
    ide = SimplePythonIDE()
    ide.interactive_menu()
