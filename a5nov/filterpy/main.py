# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import sys
import regex as re
import string
import tokenize
from io import StringIO
from multiprocessing import Pool, cpu_count

# Import fast cython function
from cy_heu import heuristic_score


# -----------------------------
# Noise line filter
# -----------------------------
def is_noise_line(line):
    stripped = line.strip()
    if not stripped:
        return False

    # long spans of whitespace = garbage
    if re.search(r'\s{10,}', line):
        return True

    letters = sum(c.isalpha() for c in stripped)
    printable = sum(c in string.printable for c in stripped)

    if printable == 0:
        return True

    # too little readable text → garbage
    if letters / printable < 0.25:
        return True

    return False


# -----------------------------
# Hybrid Python detection
# -----------------------------
def tokenizer_valid_python(block):
    try:
        tokenize.generate_tokens(StringIO(block).readline)
        return True
    except:
        return False


def is_python_block(lines):
    block_text = ''.join(lines)
    score = heuristic_score(lines)

    if score >= 3:
        return True

    if score >= 1 and tokenizer_valid_python(block_text):
        return True

    return False


# -----------------------------
# Worker function
# -----------------------------
def analyze_block(block_lines):
    if is_python_block(block_lines):
        return ''.join(block_lines)
    return ''


# -----------------------------
# Main extractor
# -----------------------------
def extract_python_blocks(filename):
    pool = Pool(cpu_count())
    async_tasks = []

    inside_block = False
    current_block = []

    with open(filename, 'r', encoding='utf-8') as f:
        for raw_line in f:
            stripped = raw_line.rstrip('\n')

            # Start fenced block
            if not inside_block:
                if stripped.startswith('```'):
                    inside_block = True
                    current_block = []
                continue

            # End fenced block
            else:
                if stripped.startswith('```'):
                    inside_block = False
                    # Send block to worker
                    async_tasks.append(
                        pool.apply_async(analyze_block, (current_block,))
                    )
                    current_block = []
                else:
                    current_block.append(raw_line)

    pool.close()
    pool.join()

    # Write filtered output
    with open('out.txt', 'w', encoding='utf-8') as out:
        for task in async_tasks:
            block = task.get()
            if not block:
                continue

            # Remove noise lines
            cleaned = []
            for line in block.splitlines(True):
                if not is_noise_line(line):
                    cleaned.append(line)

            out.write(''.join(cleaned))


# -----------------------------
# Entry point
# -----------------------------
def main():
    if len(sys.argv) < 2:
        print('Usage: extractor.py <filename>')
        sys.exit(1)

    extract_python_blocks(sys.argv[1])


if __name__ == '__main__':
    main()
