# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import shutil


def find64(cont):
    list1 = [str(cont).split('\n')]
    for line in list1:
        if (
            'b64 = """' in line
            or "b64 = '''" in line
            or 'b64="""' in line
            or "b64='''" in line
        ):
            return True
    return False


def main():
    target_dir = '/data/data/com.termux/files/home/tmp'
    for root, _, files in os.walk('/data/data/com.termux/files'):
        for f in files:
            contents = ''
            fp = os.path.join(root, f)
            if os.path.isfile(fp) and os.path.exists(fp):
                try:
                    with open(fp, 'rb') as fobj:
                        contents = fobj.read().decode('utf-8')
                    if 'b64 =' in contents:
                        print(contents)
                        #                    if find64(contents):
                        #                        shutil.copy2(fp, target_dir)
                        print(f'Found base64 in {f}')
                except UnicodeDecodeError:
                    pass
                    # This exception is raised for files that can't be decoded as UTF-8
                #                    print(f"Skipping binary or non-UTF-8 file: {f}")
                except PermissionError:
                    # This exception is raised if the program doesn't have permission to read the file
                    print(f'Permission error reading file: {f}')
                except Exception as e:
                    # Catch any other unexpected exceptions
                    print(f'Error reading {f}: {e}')


if __name__ == '__main__':
    main()
