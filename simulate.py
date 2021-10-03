import json
import time
from random import randint
from collections import Counter
from multiprocessing import Process, Queue, Pool
import letters_and_numbers as lan


def random_instance(n_large, n_small):
    numbers = \
        [randint(1, 4)*25 for _ in range(n_large)] + \
        [randint(1, 10) for _ in range(n_small)]
    target = randint(1, 999)
    return numbers, target


if __name__ == "__main__":
    def proc():
        """
        Questions to ask (as functions of n_large and n_small):
        - what percentage of problems are infeasible?
        - what are the distributions of distances?
        - what are the distributions of solving times?
        - what kind of instances are hard?
        """
        N = 6
        n_large = randint(0, N)
        n_small = N-n_large
        numbers, target = random_instance(n_large, n_small)

        time_start = time.time()
        res_proc: dict = (
            next(lan.last(lan.run_solver(numbers, target)))
        )
        time_end = time.time()
        time_taken = time_end - time_start

        res_proc.update({
            "time": time_taken,
            "numbers": numbers,
            "target": target,
            "distance": lan.distance_from_target(target, res_proc),
            "n_total": N,
            "n_large": n_large,
            "n_small": n_small,
            "solution": lan.format_sol(res_proc)
        })
        return res_proc

    def f(x):
        return proc()

    with Pool(processes=4) as pool:
        for res in pool.imap_unordered(f, lan.itertools.count()):
            print(json.dumps(res))
