# refactor_utils

Small utility to reorganize small Python packages.

Install locally:

```bash
pip install -e .

pyrefactor run --mode small
pyrefactor run --mode merge
pyrefactor run --mode subpkg
pyrefactor run --mode dry-run
pyrefactor run --mode merge --undo


after install
goto project dir abd run:

     pyrefactor run --mode dry-run --root path/to/yourpkg

     pyrefactor run --mode merge --root path/to/yourpkg
```
