"""
The program that drives the finding of solutions for Letters and Numbers.

Usage: `python driver.py 3 4 5 6 7 8 80`
The last number is treated as the target and all numbers prior are part of the
expression formed by the solution.
"""

import sys
import subprocess
import letters_and_numbers as lan

if len(sys.argv) < 3:
    raise ValueError("Not enough args given")

NUMBERS = [int(x) for x in sys.argv[1:-1]]
TARGET = int(sys.argv[-1])

proc_minizinc = subprocess.Popen([
    'minizinc',
    'lettersAndNumbers.mzn',
    'lettersAndNumbers_symmetryBreaking.mzn',
    '-D', f'n = {len(NUMBERS)}; numbers = {NUMBERS}; target = {TARGET}',
    '--output-mode', 'json',
    '--all-solutions',
], stdout=subprocess.PIPE)

proc_parser = subprocess.Popen([
    'python',
    'letters_and_numbers.py',
], stdin=proc_minizinc.stdout, stdout=subprocess.PIPE)

for line in proc_parser.stdout:
    print(line.decode('utf-8').strip())
