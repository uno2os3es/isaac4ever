# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import subprocess
import sys
import os


def run_command(command):
    """Utility function to run a command in the shell."""
    result = subprocess.run(
        command, shell=True, text=True, capture_output=True
    )
    if result.returncode != 0:
        print(f'Error: {result.stderr}')
        sys.exit(1)
    return result.stdout.strip()


def create_gitignore():
    """Create a .gitignore file with common Python project exclusions."""
    gitignore_content = """# Python Bytecode Files
*.pyc
*.pyo
__pycache__/

# Distribution / Packaging
*.egg
*.egg-info/
dist/
build/
eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/

# Virtual Environment
venv/
ENV/
env/
.venv/

# IDE/Editor settings
.vscode/
.idea/
*.swp
*.swo

# Pytest
.cache/

# Jupyter Notebook
.ipynb_checkpoints

# mypy
.mypy_cache/

# Pylint
.pylint.d/

# Coverage reports
.coverage
.coverage.*

# tox
.tox/

# Flake8
.flake8

# pytest
.pytest_cache/

# Sphinx
docs/_build/

# virtualenv
*.virtualenv/

# .env files (sensitive credentials like API keys)
.env
.env.*

# Docker
docker-compose.override.yml
Dockerfile*

# macOS
.DS_Store

# Windows
Thumbs.db"""

    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print('.gitignore file created.')


def create_new_repo(repo_name):
    """Create a new GitHub repo using gh CLI."""
    print(f'Creating GitHub repository: {repo_name}')
    create_command = f'gh repo create {repo_name} --public --source=. --remote=origin --push'
    run_command(create_command)
    print(f'Repository {repo_name} created and pushed to GitHub.')


def check_repo_exists(repo_name):
    """Check if the repository exists on GitHub."""
    try:
        result = run_command(f'gh repo view {repo_name}')
        return True  # Repo exists
    except SystemExit as e:
        if e.code == 1:
            return False  # Repo does not exist
        raise


def main():
    # If no repository name is given, use the name of the current directory
    if len(sys.argv) != 2:
        repo_name = os.path.basename(os.getcwd())  # Use current directory name
        print(
            f'No repo name provided. Using current directory name as repo name: {repo_name}'
        )
    else:
        repo_name = sys.argv[1]

    # Check if the repo already exists locally
    if os.path.isdir('.git'):
        print('Git repository already initialized.')
    else:
        print('Initializing git repository.')
        run_command('git init')
        create_gitignore()  # Create .gitignore file
        run_command('git add .')
        run_command('git commit -m "Initial commit"')

    # Check if the GitHub repository exists
    if check_repo_exists(repo_name):
        print(
            f'Repository {repo_name} already exists on GitHub. Pushing changes.'
        )
        run_command('git push origin main')
    else:
        print(f'Repository {repo_name} does not exist. Creating and pushing.')
        create_new_repo(repo_name)


if __name__ == '__main__':
    main()
