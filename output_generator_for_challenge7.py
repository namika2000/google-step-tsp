#!/usr/bin/env python3

from common import format_tour, print_tour, read_input
from solver_segmented_area import (
    area_segmented_greedy_solver_with_two_opt,
    cal_dist,
    update_solver_area_segmented,
)


CHALLENGES = 8


def generate_my_output():
    for i in range(CHALLENGES):
        cities = read_input(f"input_{i}.csv")
        dist = cal_dist(cities)
        # tour = area_segmented_greedy_solver_with_two_opt(cities, dist)
        tour = update_solver_area_segmented(cities, dist)
        with open(f"output_{i}.csv", "w") as f:
            f.write(format_tour(tour) + "\n")


if __name__ == "__main__":
    generate_my_output()
