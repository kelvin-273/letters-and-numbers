import sys
import json
import itertools
import subprocess
import collections

def gen_solutions(stdin=sys.stdin):
    sol_str = ''
    for i, line in enumerate(stdin):
        if line.strip() == '----------' and sol_str != '':
            yield json.loads(sol_str)
            sol_str = ''
        elif line.strip() == '----------' and sol_str == '':
            pass
        else:
            sol_str += line


def format_sol(d: dict):
    tree_depth = d["used"]*2 - 1
    t = [x['e'] for x in d['tree']]
    l = [i-1 for i in d['left']]
    r = [i-1 for i in d['right']]
    tvs = d['tree_vals']

    def str_Val(i: int):
        return str(tvs[i])

    def str_Add(i: int):
        """
        Addition has the lowest precedence so no fancy logic is required

        (b + c) + a == b + c + a
        (b - c) + a == b - c + a
        (b * c) + a == b * c + a
        (b / c) + a == b / c + a

        a + (b + c) == a + b + c
        a + (b - c) == a + b - c
        a + (b * c) == a + b * c
        a + (b / c) == a + b / c
        """
        lstr = aux(l[i])
        rstr = aux(r[i])
        return lstr + ' + ' + rstr

    def str_Sub(i: int):
        """
        Subtraction has the lowest precedence but if negates the entire result
        of the left hand computation This only becomes relevant if the left
        hand computation is addition or subtraction. As multiplication and
        division have higher precedence, ...

        (b + c) - a == b + c - a
        (b - c) - a == b - c - a
        (b * c) - a == b * c - a
        (b / c) - a == b / c - a

        a - (b + c) != a - b + c
        a - (b - c) != a - b - c
        a - (b * c) == a - b * c
        a - (b / c) == a - b / c
        """
        lstr = aux(l[i])
        rstr = aux(r[i])

        if t[r[i]] in {'Add', 'Sub'}:
            rstr = '(' + rstr + ')'

        return lstr + ' - ' + rstr

    def str_Mul(i: int):
        """
        Multiplication has higher precedence than Addition and Subtraction and
        is symmetric, and associative with multiplication and division.

        (b + c) * a != b + c * a
        (b - c) * a != b - c * a
        (b * c) * a == b * c * a
        (b / c) * a == b / c * a

        a * (b + c) != a * b + c
        a * (b - c) != a * b - c
        a * (b * c) == a * b * c
        a * (b / c) == a * b / c
        """
        lstr = aux(l[i])
        rstr = aux(r[i])

        if t[l[i]] in {'Add', 'Sub'}:
            lstr = '(' + lstr + ')'
        if t[r[i]] in {'Add', 'Sub'}:
            rstr = '(' + rstr + ')'

        return lstr + ' * ' + rstr

    def str_Div(i: int):
        """
        Multiplication has higher precedence than Addition and Subtraction and
        is symmetric, and associative with multiplication and division.

        (b + c) / a != b + c / a
        (b - c) / a != b - c / a
        (b * c) / a == b * c / a
        (b / c) / a == b / c / a

        a / (b + c) != a / b + c
        a / (b - c) != a / b - c
        a / (b * c) != a / b * c
        a / (b / c) != a / b / c
        """
        lstr = aux(l[i])
        rstr = aux(r[i])

        if t[l[i]] in {'Add', 'Sub'}:
            lstr = '(' + lstr + ')'
        if t[r[i]] in {'Add', 'Sub', 'Mul', 'Div'}:
            rstr = '(' + rstr + ')'

        return lstr + ' / ' + rstr

    def aux(i: int):
        if t[i] == "Val":
            return str_Val(i)
        elif t[i] == "Add":
            return str_Add(i)
        elif t[i] == "Sub":
            return str_Sub(i)
        elif t[i] == "Mul":
            return str_Mul(i)
        elif t[i] == "Div":
            return str_Div(i)
        else:
            raise ValueError("rubbish string found")

    return aux(0) + ' = ' + str(d['tree_vals'][0])


def distance_from_target(target: int, d: dict):
    return abs(target - d['tree_vals'][0])


def last(iterable, n=1):
    return iter(collections.deque(iterable, maxlen=n))


def run_solver(numbers, target):
    proc_minizinc = subprocess.Popen([
        'minizinc',
        'lettersAndNumbers.mzn',
        '-D', f'n = {len(numbers)}; numbers = {numbers}; target = {target}',
        '--output-mode', 'json',
        '--all-solutions',
    ], stdout=subprocess.PIPE)
    stdout, stderr = proc_minizinc.communicate()
    return gen_solutions(
        stdout.decode('utf-8').splitlines()
    )


if __name__ == "__main__":
    for d in gen_solutions():
        print(format_sol(d))
