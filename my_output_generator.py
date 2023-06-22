#!/usr/bin/env python3

from common import format_tour, print_tour, read_input
from update_solver_greedy_with_2opt import (
    cal_dist,
    find_endpoints,
    solve,
    solver_greedy,
    start_end_fix_solver_greedy,
)


CHALLENGES = 3

best_start_cities = {
    "input_0.csv": 3,
    "input_1.csv": 1,
    "input_2.csv": 6,
    "input_3.csv": 35,
    "input_4.csv": 111,
    "input_5.csv": 374,
}


def generate_my_output():
    for i in range(CHALLENGES):
        cities = read_input(f"input_{i}.csv")
        # start_city = best_start_cities[f"input_{i}.csv"]
        dist = cal_dist(cities)
        N = len(cities)
        start_city, end_city, _, _ = find_endpoints(cities)
        tour = start_end_fix_solver_greedy(N, dist, start_city, end_city)
        print("-------")
        print_tour(tour)
        print("-----")
        # tour = solver_greedy(N, dist, start_city)
        # tour, _ = solve(cities, tour, dist, start_city)
        with open(f"output_{i}.csv", "w") as f:
            f.write(format_tour(tour) + "\n")


if __name__ == "__main__":
    generate_my_output()
