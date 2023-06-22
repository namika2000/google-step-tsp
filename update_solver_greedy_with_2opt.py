#!/usr/bin/env python3

import math
import time
from common import print_tour, read_input
import sys

sys.setrecursionlimit(10**6)  # スタックフローを防ぐ


def distance(city_1, city_2):
    return math.sqrt((city_1[0] - city_2[0]) ** 2 + (city_1[1] - city_2[1]) ** 2)


def cal_dist(cities):
    N = len(cities)
    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])
    return dist


# 始点を変える
def solver_greedy(num_of_cities, dist, start_city=0):
    current_city = start_city
    unvisited_cities = set(range(0, num_of_cities))
    unvisited_cities.remove(start_city)
    tour = [current_city]

    while unvisited_cities:
        next_city = min(unvisited_cities, key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    return tour


# 2opt
def normal_two_opt(tour, dist: list[list]):
    is_updated = True
    while is_updated:
        is_updated = False
        for i in range(len(tour) - 3):
            for j in range(i + 2, len(tour) - 1):
                # city1とcity3を,city2とcity4をつなぐ
                diff = (dist[tour[i]][tour[j]] + dist[tour[i + 1]][tour[j + 1]]) - (
                    dist[tour[i]][tour[i + 1]] + dist[tour[j]][tour[j + 1]]
                )
                if diff < 0:
                    new_tour = (
                        tour[: i + 1]
                        + [city for city in reversed(tour[i + 1 : j + 1])]
                        + tour[j + 1 :]
                    )
                    tour = new_tour
                    is_updated = True

    return tour


def solve(cities):
    dist = cal_dist(cities)
    num_of_cities = len(cities)
    min_tour_length = 10**6
    best_tour = []
    best_start = 0
    # tour = solver_greedy(num_of_cities, dist, 70)
    # tour = normal_two_opt(tour, dist)
    for i in range(num_of_cities):
        tour = solver_greedy(num_of_cities, dist, i)
        tour = normal_two_opt(tour, dist)
        tour_length = sum(
            dist[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour))
        )
        if tour_length < min_tour_length:
            min_tour_length = tour_length
            best_tour = tour
            best_start = i

    # tour_length = sum(
    #     dist[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour))
    # )
    print("min_tour_length", min_tour_length)
    print("start_city", best_start)

    return best_tour


# #### ベストな始点
best_start_cities = {
    "input_0.csv": 3,  # 3291.6217214092458
    "input_1.csv": 6,  # 3832.290093905199
    "input_2.csv": 10,  # 4670.266133897527
    "input_3.csv": 35,  # 8511.224110970263
    "input_4.csv": 70,  # 11169.376590988231
    "input_5.csv": 212,  # 21072.67865612365
    "input_6.csv":
}
if __name__ == "__main__":
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    # start_city = best_start_cities[sys.argv[1]]
    # min_tour_length = 10**10
    # start_city = -1
    # for i in range(50):
    #     tour = solver_greedy(N, dist, start_city=i)
    #     tour, tour_length = solve(cities, tour, dist, start_city=i)
    #     if tour_length < min_tour_length:
    #         start_city, min_tour_length = i, tour_length
    print(f"------------{sys.argv[1]}:")
    tour = solve(cities)
    # print_tour(tour)
