# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09


# cy_heu.pyx
# Fast Cython heuristic scoring

cdef list KEYWORDS = [
    "def", "class", "import", "from",
    "async", "await", "lambda", "yield",
    "try", "except", "finally", "with",
    "for", "while", "if", "elif", "else"
]

cpdef double heuristic_score(list lines):
    cdef double score = 0.0
    cdef str line
    cdef str stripped
    cdef str kw

    for line in lines:
        stripped = line.strip()

        # Keywords
        for kw in KEYWORDS:
            if stripped.startswith(kw + " ") or stripped.startswith(kw + ":"):
                score += 2.0
                break

        # Colon ending
        if stripped.endswith(":"):
            score += 1.0

        # Indentation
        if line.startswith("    ") or line.startswith("\t"):
            score += 0.5

        # Decorators
        if stripped.startswith("@"):
            score += 2.0

    return score