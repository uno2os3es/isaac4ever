# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import sys
import tokenize
from io import StringIO
from multiprocessing import Pool, cpu_count

# Import the Cython-compiled module
from cy_heu import heuristic_score


def tokenizer_valid_python(block):
    try:
        tokenize.generate_tokens(StringIO(block).readline)
        return True
    except:
        return False


def is_python_block(lines):
    block = ''.join(lines)

    score = heuristic_score(lines)

    # Fast-path decision
    if score >= 3:
        return True

    # Combined hybrid detection
    if score >= 1 and tokenizer_valid_python(block):
        return True

    return False


def analyze_block(lines):
    if is_python_block(lines):
        return ''.join(lines)
    return ''


def extract_python_blocks_mp(filename):
    pool = Pool(cpu_count())
    jobs = []

    inside = False
    current = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.rstrip('\n')

            if not inside:
                if stripped.startswith('```'):
                    inside = True
                    current = []
                continue

            else:
                if stripped.startswith('```'):
                    inside = False
                    jobs.append(pool.apply_async(analyze_block, (current,)))
                    current = []
                else:
                    current.append(line)

    pool.close()
    pool.join()

    for job in jobs:
        result = job.get()
        if result:
            sys.stdout.write(result)


def main():
    if len(sys.argv) < 2:
        print('Usage: extractor.py <filename>')
        sys.exit(1)

    extract_python_blocks_mp(sys.argv[1])


if __name__ == '__main__':
    main()
