#!/usr/bin/env python3

from common import format_tour, print_tour, read_input
from solver_segmented_area import solve


CHALLENGES = 8


def generate_my_output():
    for i in range(CHALLENGES):
        cities = read_input(f"input_{i}.csv")
        tour = solve(cities)
        with open(f"output_{i}.csv", "w") as f:
            f.write(format_tour(tour) + "\n")


if __name__ == "__main__":
    generate_my_output()
