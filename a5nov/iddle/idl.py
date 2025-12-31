# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers import PythonLexer
import subprocess
import os
from pathlib import Path


class LightPythonIDE:
    def __init__(self):
        self.session = PromptSession()
        self.lexer = PygmentsLexer(PythonLexer)
        self.style = Style.from_dict(
            {
                '': '#ffffff',
                'keyword': '#ff79c6',
                'string': '#f1fa8c',
                'number': '#bd93f9',
            }
        )
        self.workspace = Path.home() / 'python_code'
        self.workspace.mkdir(exist_ok=True)

    def edit_file_interactive(self, filename):
        """Simple interactive file editor"""
        filepath = self.workspace / filename
        lines = []

        if filepath.exists():
            with open(filepath, 'r') as f:
                lines = f.read().splitlines()

        print(f'Editing {filename}. Enter your code (empty line to save):')
        for i, line in enumerate(lines, 1):
            print(f'{i:3d}| {line}')

        while True:
            try:
                text = self.session.prompt(
                    '>>> ', lexer=self.lexer, style=self.style
                )
                if text.strip() == '':
                    break
                lines.append(text)
            except KeyboardInterrupt:
                break
            except EOFError:
                break

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

        return filepath

    def show_menu(self):
        menu = """
╔═══════════════════════════╗
║    Light Python IDE       ║
╠═══════════════════════════╣
║ 1. Create/Edit Python file║
║ 2. Run Python file        ║
║ 3. List files             ║
║ 4. Python REPL            ║
║ 5. Exit                   ║
╚═══════════════════════════╝
        """
        print(menu)

    def main_loop(self):
        while True:
            self.show_menu()
            choice = input('Select option: ').strip()

            if choice == '1':
                filename = input('Filename: ').strip()
                if not filename.endswith('.py'):
                    filename += '.py'
                self.edit_file_interactive(filename)

            elif choice == '2':
                files = list(self.workspace.glob('*.py'))
                if files:
                    for i, f in enumerate(files, 1):
                        print(f'{i}. {f.name}')
                    try:
                        idx = int(input('Select: ')) - 1
                        if 0 <= idx < len(files):
                            self.run_file(files[idx])
                    except ValueError:
                        print('Invalid input')
                else:
                    print('No Python files found')

            elif choice == '3':
                files = list(self.workspace.glob('*.py'))
                for f in files:
                    print(f'  {f.name}')

            elif choice == '4':
                print('Starting Python REPL...')
                subprocess.run(['python'])

            elif choice == '5':
                break
            else:
                print('Invalid option')

    def run_file(self, filepath):
        print(f'\n--- Running {filepath.name} ---')
        result = subprocess.run(
            ['python', str(filepath)], capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print('STDERR:', result.stderr)
        print('--- Done ---\n')


if __name__ == '__main__':
    ide = LightPythonIDE()
    ide.main_loop()
