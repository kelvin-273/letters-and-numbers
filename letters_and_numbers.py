import os
import sys
import json
import subprocess
import collections
from typing import Generator, List
from random import choice, randint, shuffle
from fractions import Fraction
from pprint import pprint


def gen_solutions(input_file=sys.stdin):
    """
    Reads solutions from input_file and yields them as dictionaries.
    Assumes that the solutions coming from the file are json objects.
    """
    sol_str = ""
    for i, line in enumerate(input_file):
        if line.strip() == "----------" and sol_str != "":
            yield json.loads(sol_str)
            sol_str = ""
        elif line.strip() == "----------" and sol_str == "":
            pass
        else:
            sol_str += line


def format_sol(d: dict):
    tree_depth = d["used"] * 2 - 1
    tree_node = [x["e"] for x in d["tree"]]
    child_l = [i - 1 for i in d["left"]]
    child_r = [i - 1 for i in d["right"]]
    tvs = d["tree_vals"]

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
        lstr = aux(child_l[i])
        rstr = aux(child_r[i])
        return lstr + " + " + rstr

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
        lstr = aux(child_l[i])
        rstr = aux(child_r[i])

        if tree_node[child_r[i]] in {"Add", "Sub"}:
            rstr = "(" + rstr + ")"

        return lstr + " - " + rstr

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
        lstr = aux(child_l[i])
        rstr = aux(child_r[i])

        if tree_node[child_l[i]] in {"Add", "Sub"}:
            lstr = "(" + lstr + ")"
        if tree_node[child_r[i]] in {"Add", "Sub"}:
            rstr = "(" + rstr + ")"

        return lstr + " * " + rstr

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
        lstr = aux(child_l[i])
        rstr = aux(child_r[i])

        if tree_node[child_l[i]] in {"Add", "Sub"}:
            lstr = "(" + lstr + ")"
        if tree_node[child_r[i]] in {"Add", "Sub", "Mul", "Div"}:
            rstr = "(" + rstr + ")"

        return lstr + " / " + rstr

    def aux(i: int):
        if tree_node[i] == "Val":
            return str_Val(i)
        elif tree_node[i] == "Add":
            return str_Add(i)
        elif tree_node[i] == "Sub":
            return str_Sub(i)
        elif tree_node[i] == "Mul":
            return str_Mul(i)
        elif tree_node[i] == "Div":
            return str_Div(i)
        else:
            raise ValueError("rubbish string found")

    return aux(0) + " = " + str(d["tree_vals"][0])


def distance_from_target(target: int, d: dict):
    """
    Returns the absolute difference between the solutions value and the target.
    """
    return abs(target - d["tree_vals"][0])


def last(iterable, n=1):
    return iter(collections.deque(iterable, maxlen=n))


def run_solver(numbers: List[int], target: int):
    """
    Solves a single instance and gives the json output of that instances lifted
    into to a generator.
    """
    proc_minizinc = subprocess.Popen(
        [
            "minizinc",
            "lettersAndNumbers.mzn",
            "-D",
            f"n = {len(numbers)}; numbers = {numbers}; target = {target}",
            "--output-mode",
            "json",
            "--all-solutions",
        ],
        stdout=subprocess.PIPE,
    )
    stdout, stderr = proc_minizinc.communicate()
    return gen_solutions(stdout.decode("utf-8").splitlines())


def run_solver_symmetry_breaking(numbers: List[int], target: int):
    """
    Solves a single instance and gives the json output of that instances lifted
    into to a generator.
    """
    proc_minizinc = subprocess.Popen(
        [
            "minizinc",
            "lettersAndNumbers.mzn",
            "lettersAndNumbers_symmetryBreaking.mzn",
            "-D",
            f"n = {len(numbers)}; numbers = {numbers}; target = {target}",
            "--output-mode",
            "json",
            "--all-solutions",
        ],
        stdout=subprocess.PIPE,
    )
    stdout, stderr = proc_minizinc.communicate()
    return gen_solutions(stdout.decode("utf-8").splitlines())


def random_expression(numbers: List[int]):
    """
    Creates an arithmetic expression from the numbers give encoded as minizinc
    arrays. Useful for creating constraints to test the model.
    """
    n = len(numbers)
    numbers = list(map(Fraction, numbers))
    tree_choices = [
        ("Add", lambda a, b: a + b),
        ("Sub", lambda a, b: a - b),
        ("Mul", lambda a, b: a * b),
        ("Div", lambda a, b: a / b),
    ]

    # Initialise minizinc variables
    m = 2 * n - 1
    tree = [None] * m
    left = [0] * m
    right = [0] * m
    lowest = [0] * m
    highest = [0] * m
    indexes = [0] * m
    tree_vals = [Fraction(0)] * m
    used = randint(1, n)

    num_permuation = list(range(n))
    shuffle(num_permuation)

    def aux(n_nodes, tree_idx, val_idx):
        """generate the sublists that are part of the expression"""
        # TODO: keep positions of numbers fixed <10-04-22> #
        if n_nodes == 0:
            tree[tree_idx] = "Val"
            left[tree_idx] = 0
            right[tree_idx] = 0
            lowest[tree_idx] = tree_idx + 1
            highest[tree_idx] = tree_idx + 1
            indexes[tree_idx] = num_permuation[val_idx] + 1
            tree_vals[tree_idx] = numbers[num_permuation[val_idx]]
        else:
            node, op = choice(tree_choices)

            n_nodes_l = randint(0, n_nodes - 1)
            n_leaves_l = n_nodes_l + 1
            tree_idx_l = tree_idx + 1
            val_idx_l = val_idx

            n_nodes_r = n_nodes - 1 - n_nodes_l
            # n_leaves_r = n_nodes_r + 1
            tree_idx_r = tree_idx_l + n_nodes_l + n_leaves_l
            val_idx_r = val_idx_l + n_leaves_l

            aux(n_nodes_l, tree_idx_l, val_idx_l)
            aux(n_nodes_r, tree_idx_r, val_idx_r)

            tree[tree_idx] = node
            left[tree_idx] = tree_idx_l + 1
            right[tree_idx] = tree_idx_r + 1
            lowest[tree_idx] = tree_idx + 1
            highest[tree_idx] = highest[tree_idx_r]
            tree_vals[tree_idx] = op(
                tree_vals[tree_idx_l],
                tree_vals[tree_idx_r]
            )

    try:
        aux(used - 1, 0, 0)
    except ZeroDivisionError:
        return None

    # Fill in null and unused numbers
    tree_len = highest[0]
    assert tree_len >= 1, "highest[0] is less than 1"

    # fill in the Nuls
    for tree_idx in range(tree_len, tree_len + n - used):
        tree[tree_idx] = "Null"
        tree_vals[tree_idx] = Fraction(0)

    # fill in the unused numbers
    for tree_idx, val_idx in zip(
            range(tree_len + n - used, m),
            range(used, n)):
        tree[tree_idx] = "Val"
        tree_vals[tree_idx] = numbers[num_permuation[val_idx]]
        indexes[tree_idx] = num_permuation[val_idx] + 1

    # TODO: Fix the minizinc model and this code (and this whole function) to
    # require the only the final expression to be an integer <09-04-22> #
    if any(tree_vals[k].denominator != 1 for k in range(m)):
        return None

    # convert tree_vals to ints
    tree_vals = [v.numerator for v in tree_vals]

    return {
        "tree": tree,
        "left": left,
        "right": right,
        "lowest": lowest,
        "highest": highest,
        "indexes": indexes,
        "used": used,
        "tree_vals": tree_vals,
    }


def generate_test_case(max_len, max_num):
    return [randint(1, max_num) for _ in range(randint(1, max_len))]


def run_solver_with_constraints(numbers: List[int], minizinc_vars: dict):
    """
    Solves a single instance and gives the json output of that instances lifted
    into to a generator.
    """
    target = minizinc_vars["tree_vals"][0]
    tree = minizinc_vars["tree"]
    left = minizinc_vars["left"]
    right = minizinc_vars["right"]
    lowest = minizinc_vars["lowest"]
    highest = minizinc_vars["highest"]
    indexes = minizinc_vars["indexes"]
    tree_vals = minizinc_vars["tree_vals"]
    used = minizinc_vars["used"]

    test_cons_filename = "test_cons.mzn"
    test_data_filename = "test_data.dzn"
    with open(test_cons_filename, 'w') as f:
        f.write('\n'.join([
            "constraint tree = [" + ", ".join(tree) + "];",
            f"constraint left = {left};",
            f"constraint right = {right};",
            f"constraint lowest = {lowest};",
            f"constraint highest = {highest};",
            f"constraint indexes = {indexes};",
            f"constraint tree_vals = {tree_vals};",
            f"constraint used = {used};",
        ]))
    with open(test_data_filename, 'w') as f:
        f.write('\n'.join([
            f"n={len(numbers)};",
            f"numbers={numbers};",
            f"target={target};",
        ]))

    proc_minizinc = subprocess.Popen(
        [
            "minizinc",
            "lettersAndNumbers.mzn",
            f"{test_cons_filename}",
            "-d",
            f"{test_data_filename}",
            "--output-mode",
            "json",
        ],
        stdout=subprocess.PIPE,
    )
    stdout, stderr = proc_minizinc.communicate()
    return gen_solutions(stdout.decode("utf-8").splitlines())


if __name__ == "__main__":
    # for i in range(100):
        # pprint(random_expression(generate_test_case(6, 100)))
        # print()

    print("testing solver with constraints")
    for _ in range(100):
        minizinc_vars = None
        while minizinc_vars is None or minizinc_vars['tree_vals'][0] not in range(1, 10001):
            numbers = generate_test_case(7, 100)
            minizinc_vars = random_expression(numbers)
        print(f"numbers: {numbers}")
        pprint(minizinc_vars)
        # print(len(list(run_solver(numbers, minizinc_vars['tree_vals'][0]))))
        print(format_sol(list(run_solver(numbers, minizinc_vars['tree_vals'][0]))[-1]))
    # """
    # Reads solutions as json objects from stdin and prints them as the
    # arithmetic expressions and their value.
    # """
    # for d in gen_solutions():
    #     print(format_sol(d))
