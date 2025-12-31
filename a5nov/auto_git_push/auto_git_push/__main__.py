# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09
"""
auto_git_push CLI

Run:
  python -m auto_git_push ...
or after install:
  auto-git-push [--dry-run] [--no-precommit] [--verbose]

Features:
 - Detect git repo root
 - Merge ~/.gitignore_global into .gitignore if missing
 - Fast black execution (single call)
 - Accurate python detection (py_compile + shebang)
 - Multiprocessing for detection
 - Skip work for clean repos
 - Stage, commit (timestamped), push to current branch with upstream detection
 - Skip commit if only whitespace changes
 - Pre-commit integration (optional)
 - Config via ~/.auto_git_config.json
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import multiprocessing
import os
import shutil
import subprocess
import sys
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import List, Set

# Default configuration
DEFAULT_CONFIG = {
    'skip_dirs': [
        'venv',
        '.venv',
        '.git',
        '__pycache__',
        '.mypy_cache',
        '.ruff_cache',
    ],
    'dry_run': False,
    'precommit': True,
    'black_args': ['.'],  # by default, black .
    'commit_msg_prefix': '[AUTO]',
    'logging_level': 'INFO',
    'py_compile_timeout_seconds': 5,
}

HOME = Path.home()
CONFIG_PATH = HOME / '.auto_git_config.json'
GLOBAL_GITIGNORE = HOME / '.gitignore_global'
LOG = logging.getLogger('auto_git_push')


def load_config() -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as fh:
                user_cfg = json.load(fh)
            cfg.update(user_cfg)
            LOG.debug('Loaded user config from %s', CONFIG_PATH)
        except Exception as e:
            LOG.warning('Failed to read config %s: %s', CONFIG_PATH, e)
    return cfg


def setup_logging(level_name: str):
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)-5s %(name)s: %(message)s',
    )


def run_cmd(
    cmd: List[str],
    cwd: Path | None = None,
    capture: bool = False,
    check: bool = False,
):
    """Run a subprocess command. Returns CompletedProcess."""
    LOG.debug('Running command: %s (cwd=%s)', ' '.join(cmd), cwd)
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            check=check,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        LOG.debug('Command failed: %s', e)
        raise


def is_inside_git_repo() -> bool:
    """Return True if the current working dir is inside a git repo."""
    try:
        res = run_cmd(
            ['git', 'rev-parse', '--is-inside-work-tree'], capture=True
        )
        return res.returncode == 0 and res.stdout.strip() == 'true'
    except Exception:
        return False


def git_repo_root() -> Path | None:
    """Return repo root Path or None."""
    try:
        res = run_cmd(['git', 'rev-parse', '--show-toplevel'], capture=True)
        if res.returncode == 0:
            return Path(res.stdout.strip())
    except Exception:
        pass
    return None


def ensure_gitignore(repo_root: Path):
    """
    If .gitignore doesn't exist in repo root, merge ~/.gitignore_global
    into a new .gitignore (dedup + sort).
    """
    repo_gitignore = repo_root / '.gitignore'
    if repo_gitignore.exists():
        LOG.debug('.gitignore already exists in repo.')
        return

    if GLOBAL_GITIGNORE.exists():
        try:
            LOG.info('Creating local .gitignore from %s', GLOBAL_GITIGNORE)
            try:
                with open(GLOBAL_GITIGNORE, 'r', encoding='utf-8') as src:
                    global_lines = [line.rstrip('\n') for line in src]
            except Exception:
                global_lines = []

            # If local file existed earlier, we'd merge. Since it doesn't, just write unique sorted lines.
            unique = sorted({l for l in global_lines if l.strip()})
            with open(repo_gitignore, 'w', encoding='utf-8') as dest:
                dest.write('\n'.join(unique) + ('\n' if unique else ''))
            LOG.debug('Wrote %s with %d lines', repo_gitignore, len(unique))
        except Exception as e:
            LOG.warning('Failed to create local .gitignore: %s', e)
    else:
        LOG.info(
            'No global .gitignore_global found at %s. Skipping .gitignore creation.',
            GLOBAL_GITIGNORE,
        )


def iter_files(repo_root: Path, skip_dirs: Set[str]) -> List[Path]:
    """Walk the repo root and produce candidate file paths excluding skip dirs."""
    files = []
    for root, dirs, filenames in os.walk(repo_root):
        # mutate dirs in-place to skip unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fn in filenames:
            # skip dotfiles except scripts
            path = Path(root) / fn
            files.append(path)
    return files


def looks_like_python_by_shebang(p: Path) -> bool:
    """Quick check: shebang contains 'python'."""
    try:
        with p.open('rb') as fh:
            first = fh.readline(200).decode('utf-8', errors='ignore').lower()
            return first.startswith('#!') and 'python' in first
    except Exception:
        return False


def check_py_compile(path_str: str) -> bool:
    """
    Attempt to compile the file with python -m py_compile.
    This runs in separate processes (called via executor).
    Return True if compilation succeeded.
    """
    # run using same python executable
    try:
        res = subprocess.run(
            [sys.executable, '-m', 'py_compile', path_str],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return res.returncode == 0
    except Exception:
        return False


def detect_python_files(
    repo_root: Path, skip_dirs: Set[str], cfg: dict
) -> List[Path]:
    """
    Detect python files:
     - all .py files
     - extensionless files that either have python shebang or compile via py_compile
    Use multiprocessing for py_compile checks.
    """
    LOG.info('Scanning repository for Python files...')
    all_candidates = iter_files(repo_root, skip_dirs)
    py_files: Set[Path] = set()

    # collect .py files
    for p in all_candidates:
        if p.suffix == '.py':
            py_files.add(p)

    # Collect extensionless files (no suffix) and small scripts
    extless = [p for p in all_candidates if p.suffix == '' and p.is_file()]
    LOG.debug('Found %d extensionless files to check', len(extless))

    # First pass: shebang quick accept
    shebang_yes = [p for p in extless if looks_like_python_by_shebang(p)]
    for p in shebang_yes:
        py_files.add(p)

    # Remaining candidates to check with py_compile (to avoid trying huge binary files)
    to_check = [str(p) for p in extless if p not in shebang_yes]

    # Use multiprocessing to speed up py_compile checks
    workers = min((multiprocessing.cpu_count() or 1), 8)
    LOG.debug('Using %d workers for py_compile checks', workers)
    try:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=workers
        ) as exe:
            for path_str, ok in zip(
                to_check, exe.map(check_py_compile, to_check)
            ):
                if ok:
                    py_files.add(Path(path_str))
    except Exception as e:
        LOG.warning(
            'Multiprocessing py_compile checks failed; falling back to sequential. (%s)',
            e,
        )
        for path_str in to_check:
            if check_py_compile(path_str):
                py_files.add(Path(path_str))

    LOG.info('Detected %d Python files.', len(py_files))
    return sorted(py_files)


def is_repo_clean(repo_root: Path) -> bool:
    """
    True if working tree and index are both clean (no unstaged or staged changes).
    We check:
      - git diff --quiet (unstaged)
      - git diff --cached --quiet (staged)
    """
    try:
        unstaged = run_cmd(['git', 'diff', '--quiet'], cwd=repo_root)
        staged = run_cmd(['git', 'diff', '--cached', '--quiet'], cwd=repo_root)
        # run_cmd will return CompletedProcess; returncode 0 => quiet/no-diff
        clean = (unstaged.returncode == 0) and (staged.returncode == 0)
        LOG.debug('Repo clean status: %s', clean)
        return clean
    except Exception:
        return False


def run_black_on_files(repo_root: Path, files: List[Path], cfg: dict) -> bool:
    """
    Run black once. If files is empty, return True.
    Default: run `black .` if cfg['black_args'] == ['.']
    Otherwise pass explicit file paths in a single command call.
    """
    if not files:
        LOG.info('No Python files to format.')
        return True

    # if user set black_args to default ".", prefer running black from repo root to allow black's own discovery
    black_args = cfg.get('black_args', ['.'])
    if black_args == ['.']:
        cmd = ['black', '.']  # run in repo root
    else:
        # pass explicit files (faster than invoking black one-by-one)
        cmd = ['black'] + [str(p.relative_to(repo_root)) for p in files]

    LOG.info('Running black: %s', ' '.join(cmd))
    try:
        if cfg.get('dry_run'):
            LOG.info('[dry-run] Would run: %s', ' '.join(cmd))
            return True
        res = run_cmd(cmd, cwd=repo_root, capture=True)
        if res.returncode != 0:
            LOG.error('black failed: %s', (res.stderr or res.stdout))
            return False
        LOG.debug('black output: %s', res.stdout)
        return True
    except FileNotFoundError:
        LOG.error('black is not installed. Please pip install black.')
        return False
    except Exception as e:
        LOG.exception('Failed running black: %s', e)
        return False


def git_add_all(repo_root: Path, cfg: dict) -> bool:
    if cfg.get('dry_run'):
        LOG.info('[dry-run] git add .')
        return True
    try:
        res = run_cmd(['git', 'add', '.'], cwd=repo_root, capture=True)
        if res.returncode != 0:
            LOG.error('git add failed: %s', res.stderr or res.stdout)
            return False
        return True
    except Exception as e:
        LOG.exception('git add failed: %s', e)
        return False


def staged_changes_names(repo_root: Path) -> List[str]:
    """Return list of staged files (git diff --cached --name-only)."""
    try:
        res = run_cmd(
            ['git', 'diff', '--cached', '--name-only'],
            cwd=repo_root,
            capture=True,
        )
        if res.returncode == 0:
            names = [
                ln for ln in (res.stdout or '').splitlines() if ln.strip()
            ]
            LOG.debug('Staged files: %s', names)
            return names
    except Exception as e:
        LOG.debug('Failed to get staged names: %s', e)
    return []


def staged_changes_only_whitespace(repo_root: Path) -> bool:
    """
    Detect if staged changes are only whitespace changes.
    Method:
      - names_normal = git diff --cached --name-only
      - names_nowsp = git diff --cached -w --name-only
      - if names_normal non-empty and names_nowsp empty -> only whitespace
    """
    try:
        res_norm = run_cmd(
            ['git', 'diff', '--cached', '--name-only'],
            cwd=repo_root,
            capture=True,
        )
        res_nowsp = run_cmd(
            ['git', 'diff', '--cached', '-w', '--name-only'],
            cwd=repo_root,
            capture=True,
        )
        names_norm = (
            [ln for ln in (res_norm.stdout or '').splitlines() if ln.strip()]
            if res_norm
            else []
        )
        names_nowsp = (
            [ln for ln in (res_nowsp.stdout or '').splitlines() if ln.strip()]
            if res_nowsp
            else []
        )
        LOG.debug(
            'staged names normal: %s, ignoring ws: %s', names_norm, names_nowsp
        )
        return bool(names_norm) and (len(names_nowsp) == 0)
    except Exception as e:
        LOG.debug('Whitespace-only detection failed: %s', e)
        return False


def git_commit_and_push(repo_root: Path, cfg: dict) -> bool:
    """
    Commit with timestamped message and push to current branch.
    Skip commit if nothing to commit or only whitespace changes.
    """
    if cfg.get('dry_run'):
        LOG.info('[dry-run] Would commit and push.')
        return True

    # if nothing staged, return False (no commit)
    staged = staged_changes_names(repo_root)
    if not staged:
        LOG.info('Nothing staged to commit.')
        return False

    # Skip commit if only whitespace changes
    if staged_changes_only_whitespace(repo_root):
        LOG.info('Staged changes are only whitespace. Skipping commit.')
        # Optionally you may want to unstage whitespace-only changes; currently we skip commit and leave staged files as-is.
        return False

    # Build commit message
    prefix = cfg.get('commit_msg_prefix', '').strip()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f'{prefix} {ts}' if prefix else ts

    LOG.info('Committing with message: %s', message)
    try:
        res = run_cmd(
            ['git', 'commit', '-m', message], cwd=repo_root, capture=True
        )
        if res.returncode != 0:
            LOG.error('git commit failed: %s', res.stderr or res.stdout)
            return False
    except Exception as e:
        LOG.exception('git commit failed: %s', e)
        return False

    # Detect current branch
    try:
        res = run_cmd(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=repo_root,
            capture=True,
        )
        branch = res.stdout.strip() if res and res.returncode == 0 else None
    except Exception:
        branch = None

    if not branch:
        LOG.info('Could not detect current branch. Using generic git push.')
        push_cmd = ['git', 'push']
    else:
        # check if branch has upstream set
        try:
            res = run_cmd(
                [
                    'git',
                    'rev-parse',
                    '--abbrev-ref',
                    '--symbolic-full-name',
                    '@{u}',
                ],
                cwd=repo_root,
                capture=True,
            )
            if res.returncode == 0:
                push_cmd = ['git', 'push']
            else:
                # set upstream on first push
                push_cmd = ['git', 'push', '-u', 'origin', branch]
        except Exception:
            push_cmd = ['git', 'push', '-u', 'origin', branch]

    LOG.info('Pushing with: %s', ' '.join(push_cmd))
    try:
        res = run_cmd(push_cmd, cwd=repo_root, capture=True)
        if res.returncode != 0:
            LOG.error('git push failed: %s', res.stderr or res.stdout)
            return False
    except Exception as e:
        LOG.exception('git push failed: %s', e)
        return False

    LOG.info('Commit and push completed.')
    return True


def ensure_precommit(repo_root: Path, cfg: dict):
    """Optionally create a .pre-commit-config.yaml (minimal) and run pre-commit install."""
    if not cfg.get('precommit', True):
        LOG.debug('Pre-commit integration disabled by config.')
        return

    yml = repo_root / '.pre-commit-config.yaml'
    if yml.exists():
        LOG.debug('.pre-commit-config.yaml already exists.')
    else:
        LOG.info('Writing minimal .pre-commit-config.yaml (black).')
        content = """repos:
  - repo: https://github.com/psf/black
    rev: stable
    hooks:
      - id: black
"""
        try:
            with open(yml, 'w', encoding='utf-8') as fh:
                fh.write(content)
        except Exception as e:
            LOG.warning('Failed to write pre-commit config: %s', e)
            return

    # attempt to run `pre-commit install`
    try:
        res = run_cmd(['pre-commit', 'install'], cwd=repo_root, capture=True)
        if res.returncode == 0:
            LOG.info('pre-commit installed.')
        else:
            LOG.warning(
                'pre-commit install failed or pre-commit not available: %s',
                res.stderr or res.stdout,
            )
    except FileNotFoundError:
        LOG.warning(
            "pre-commit not installed. To enable, pip install pre-commit and run 'pre-commit install' manually."
        )
    except Exception as e:
        LOG.warning('Failed running pre-commit install: %s', e)


def main(argv=None):
    cfg = load_config()
    parser = argparse.ArgumentParser(
        prog='auto-git-fmt',
        description='Auto-format Python files and auto-commit/push in a git repo.',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would happen without making changes.',
    )
    parser.add_argument(
        '--no-precommit',
        action='store_true',
        help='Do not set up pre-commit integration.',
    )
    parser.add_argument(
        '--verbose', action='store_true', help='Verbose (debug) logging.'
    )
    args = parser.parse_args(argv)

    if args.verbose:
        cfg['logging_level'] = 'DEBUG'
    if args.dry_run:
        cfg['dry_run'] = True
    if args.no_precommit:
        cfg['precommit'] = False

    setup_logging(cfg.get('logging_level', 'INFO'))
    LOG.debug('Config: %s', cfg)

    # Confirm inside git repo
    if not is_inside_git_repo():
        LOG.info('Not inside a Git repository. Doing nothing.')
        return 0

    repo_root = git_repo_root()
    if not repo_root:
        LOG.info('Could not determine git repo root. Doing nothing.')
        return 0

    LOG.info('Repository root: %s', repo_root)

    # Ensure .gitignore exists (copy global)
    ensure_gitignore(repo_root)

    # Optionally set up pre-commit
    ensure_precommit(repo_root, cfg)

    # Detect skip dirs
    skip_dirs = set(cfg.get('skip_dirs', []))

    # If repository is entirely clean (no staged/unstaged changes), we may skip formatting (as requested).
    if is_repo_clean(repo_root):
        LOG.info(
            'Repository appears clean (no unstaged or staged changes). Nothing to do.'
        )
        return 0

    # Detect python files
    py_files = detect_python_files(repo_root, skip_dirs, cfg)

    if not py_files:
        LOG.info('No Python files detected. Exiting.')
        return 0

    # Run black
    if not run_black_on_files(repo_root, py_files, cfg):
        LOG.error('Black formatting failed. Aborting.')
        return 1

    # Stage changes
    if not git_add_all(repo_root, cfg):
        LOG.error('git add failed. Aborting.')
        return 1

    # Commit & push (skip commit if nothing or only whitespace)
    git_commit_and_push(repo_root, cfg)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
