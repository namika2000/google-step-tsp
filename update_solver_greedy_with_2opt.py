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


# 始点と終点を固定する
def start_end_fix_solver_greedy(cities, dist, start_city, end_city):
    current_city = start_city
    unvisited_cities = cities
    unvisited_cities.remove(start_city)
    unvisited_cities.remove(end_city)
    tour = [current_city]

    while unvisited_cities:
        next_city = min(unvisited_cities, key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    tour.append(end_city)
    return tour


def area_segmented_greedy_solver_with_two_opt(original_cities, dist):
    # 領域の端点を見つける
    x_min_city, y_max_city, x_max_city, y_min_city = find_endpoints(original_cities)
    start_end_cities = {
        1: [x_min_city, y_max_city],
        2: [y_max_city, x_max_city],
        3: [x_max_city, y_min_city],
        4: [y_min_city, x_min_city],
    }

    # 領域を四分割し、どのエリアに属すかで都市を分ける.
    area_segmented_cities = split_cities(
        original_cities, x_min_city, y_max_city, x_max_city, y_min_city
    )

    # エリアごとに始点と終点を固定して貪欲法で経路を見つける
    segmented_tours = {}  # {area1: tour1, area2: tour2,...}
    for area, cities in area_segmented_cities.items():
        start_city, end_city = start_end_cities[area]
        tour = start_end_fix_solver_greedy(cities, dist, start_city, end_city)
        tour = update_solve(len(cities), tour, dist)
        segmented_tours[area] = tour

    # 分割した経路をつなげる
    merged_tour = []
    for area, tour in segmented_tours.items():
        if area == 1:
            merged_tour += tour
        elif area == 4:
            merged_tour += tour[1:-1]
        else:
            merged_tour += tour[1:]
    tour_length = sum(
        dist[merged_tour[i]][merged_tour[(i + 1) % len(merged_tour)]]
        for i in range(len(merged_tour))
    )

    print("tour_length", tour_length)
    return merged_tour


# 端点(1:x_min_city, 2:y_max_city, 3:x_max_city, 4:y_min_city)を見つける
# 端点のcityのidを返す
def find_endpoints(cities) -> list[int]:
    x_min_city, y_min_city, x_max_city, y_max_city = 0, 0, 0, 0

    for i in range(len(cities)):
        if cities[i][0] < cities[x_min_city][0]:
            x_min_city = i
        elif cities[i][1] < cities[y_min_city][1]:
            y_min_city = i
        elif cities[i][0] > cities[x_max_city][0]:
            x_max_city = i
        elif cities[i][1] > cities[y_max_city][1]:
            y_max_city = i
    return x_min_city, y_max_city, x_max_city, y_min_city


# 領域を分割する
def split_cities(cities, x_min_city, y_max_city, x_max_city, y_min_city):
    N = len(cities)
    # 領域を設定
    # areas= {area_number: [x_min, y_min, x_max, y_max]}
    areas = {
        1: [
            cities[x_min_city][0],
            cities[x_min_city][1],
            cities[y_max_city][0],
            cities[y_max_city][1],
        ],
        2: [
            cities[y_max_city][0],
            cities[x_max_city][1],
            cities[x_max_city][0],
            cities[y_max_city][1],
        ],
        3: [
            cities[y_min_city][0],
            cities[y_min_city][1],
            cities[x_max_city][0],
            cities[x_max_city][1],
        ],
    }
    # {area_number: [city1, city2, ...]}
    area_segmented_cities = {}
    city_id_list = [i for i in range(N)]
    for area_id, area in areas.items():
        cities_of_area = []
        for city_id in city_id_list:
            if (
                cities[city_id][0] >= area[0]
                and cities[city_id][0] <= area[2]
                and cities[city_id][1] >= area[1]
                and cities[city_id][1] <= area[3]
            ):
                cities_of_area.append(city_id)

        area_segmented_cities[area_id] = cities_of_area
        # 次のエリアの都市を探すための準備
        # すでに前のエリアにある都市は除外する
        for city_id in cities_of_area:
            city_id_list.remove(city_id)
    # 残りの都市はarea4に属す
    area_segmented_cities[4] = city_id_list
    # 重複で除外された始点、終点を追加する
    # area2,3,4は始点が前のエリアの終点と重複する
    # area4がさらに終点がarea1の始点と重複する
    area_segmented_cities[2].append(y_max_city)
    area_segmented_cities[3].append(x_max_city)
    area_segmented_cities[4].append(y_min_city)
    area_segmented_cities[4].append(x_min_city)

    return area_segmented_cities


# 始点を色々試す用の2opt
def solve(cities, tour, dist: list[list], start_city=0):
    # start = time.time()
    prev_tour_length = sum(
        dist[tour[i]][tour[(i + 1) % len(cities)]] for i in range(len(cities))
    )
    tour_length = 0
    # 最後と最初をつなぐ
    tour.append(start_city)
    while tour_length < prev_tour_length:
        if tour_length == 0:
            tour_length = prev_tour_length
        prev_tour_length = tour_length
        prev_tour = tour
        for i in range(len(tour)):
            if i >= len(tour) - 3:
                break

            for j in range(i + 2, len(tour) - 1):
                if i == 0 and j + 1 == len(tour) - 1:
                    continue
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
                    tour_length += diff
                    tour = new_tour
    # end = time.time()
    # print(end - start)

    print(prev_tour_length)
    return prev_tour[:-1]


# 始点と終点は固定して、それ以外の都市で2optを行う
def update_solve(num_of_cities, tour, dist: list[list]):
    # start = time.time()
    # startからendまでの経路の長さを求める
    # endとstartは繋がない
    prev_tour_length = sum(dist[tour[i]][tour[i + 1]] for i in range(num_of_cities - 1))
    tour_length = 0
    prev_tour = tour
    while tour_length < prev_tour_length:
        if tour_length == 0:
            tour_length = prev_tour_length
        prev_tour_length = tour_length
        prev_tour = tour
        for i in range(len(tour) - 3):
            for j in range(i + 2, len(tour) - 1):
                if i == 0 and j + 1 == len(tour) - 1:
                    continue
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
                    tour_length += diff
                    tour = new_tour
    # end = time.time()
    # print(end - start)
    # print(prev_tour_length)
    return prev_tour


# #### ベストな始点
best_start_cities = {
    "input_0.csv": 3,
    "input_1.csv": 1,
    "input_2.csv": 6,
    "input_3.csv": 35,
    "input_4.csv": 111,
    "input_5.csv": 374,
}
if __name__ == "__main__":
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    # start_city = best_start_cities[sys.argv[1]]
    dist = cal_dist(cities)
    # tour = area_segmented_greedy_solver_with_two_opt(cities, dist)
    # split_cities(cities, x_min_city, y_max_city, x_max_city, y_min_city)
    # tour = start_end_fix_solver_greedy(N, dist, x_min_city, y_max_city)
    # min_tour_length = 10**10
    # start_city = -1
    # for i in range(50):
    #     tour = solver_greedy(N, dist, start_city=i)
    #     tour, tour_length = solve(cities, tour, dist, start_city=i)
    #     if tour_length < min_tour_length:
    #         start_city, min_tour_length = i, tour_length
    # print(
    #     f"{sys.argv[1]}: start_city: {start_city}, min_tour_length: {min_tour_length}"
    # )
    tour = solver_greedy(len(cities), dist)
    # solve_two_opt(cities, tour)
    tour = solve(cities, tour, dist)
    # print_tour(tour)
