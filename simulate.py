import letters_and_numbers as lan
from random import randint
from collections import Counter

def random_instance(n_large, n_small):
    numbers = \
        [randint(1, 4)*25 for _ in range(n_large)] + \
        [randint(1, 10) for _ in range(n_small)]
    target = randint(1, 999)
    return numbers, target


counts = Counter()
for i in range(10000):
    """
    Questions to ask (as functions of n_large and n_small):
    - what percentage of problems are infeasible?
    - what are the distributions of distances?
    - what are the distributions of solving times?
    - what kind of instances are hard?
    """
    numbers, target = random_instance(2, 4)
    res = (
        lan.distance_from_target(
            target,
            next(lan.last(lan.run_solver(numbers, target)))
        )
    )
    counts[res] += 1

    print()
    for k, v in sorted(counts.items()):
        print(f"{k}: {v}")
