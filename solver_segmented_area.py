#!/usr/bin/env python3

import math
import time
from common import print_tour, read_input
import sys


def distance(city_1, city_2):
    return math.sqrt((city_1[0] - city_2[0]) ** 2 + (city_1[1] - city_2[1]) ** 2)


def cal_dist(cities):
    N = len(cities)
    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])
    return dist


# 領域の端のx,y座標を算出
def find_end_coords(cities) -> list[int]:
    x_min, y_min, x_max, y_max = (
        10**6,
        10**6,
        -(10**6),
        -(10**6),
    )

    for i in range(len(cities)):
        if cities[i][0] < x_min:
            x_min = cities[i][0]
        if cities[i][1] < y_min:
            y_min = cities[i][1]
        if cities[i][0] > x_max:
            x_max = cities[i][0]
        if cities[i][1] > y_max:
            y_max = cities[i][1]
    return x_min, y_min, x_max, y_max


# 領域を4等分し、どの領域に属すかで都市を分ける
def split_cities(cities):
    N = len(cities)
    x_min, y_min, x_max, y_max = find_end_coords(cities)
    # エリアごとの範囲を設定
    # areas= {area_number: [x_min, x_max, y_min, y_max]}
    areas = {
        1: [
            x_min,
            (x_min + x_max) / 2,
            y_min,
            (y_min + y_max) / 2,
        ],
        2: [
            (x_min + x_max) / 2,
            x_max,
            y_min,
            (y_min + y_max) / 2,
        ],
        3: [
            (x_min + x_max) / 2,
            x_max,
            (y_min + y_max) / 2,
            y_max,
        ],
        4: [
            x_min,
            (x_min + x_max) / 2,
            (y_min + y_max) / 2,
            y_max,
        ],
    }

    # {[], [city1, city2, ...],[city3, city4,...],..}
    area_segmented_cities = [[] for _ in range(5)]  # インデックスの0はdummy
    city_id_list = [i for i in range(N)]
    for area_id, area in areas.items():
        cities_of_area = []
        for city_id in city_id_list:
            if (
                cities[city_id][0] < area[0]
                or cities[city_id][0] > area[1]
                or cities[city_id][1] < area[2]
                or cities[city_id][1] > area[3]
            ):
                continue
            cities_of_area.append(city_id)
        area_segmented_cities[area_id] = cities_of_area

        # 次のエリアの都市を探すための準備
        # すでに前のエリアにある都市は除外する
        for city_id in cities_of_area:
            city_id_list.remove(city_id)

    return areas, area_segmented_cities


# 境界に近い4点を見つける
def find_boundary_points(cities, areas, area_segmented_cities):
    min_left_diff, min_top_diff, min_right_diff, min_bottom_diff = (
        10**6,
        10**6,
        10**6,
        10**6,
    )
    left, top, right, bottom = 0, 0, 0, 0
    left_candidates, top_candidates, right_candidates, bottom_candidates = (
        [],
        [],
        [],
        [],
    )
    # エリア1の都市の中でもっともエリア2に近いleftとエリア4に近いtopを見つける
    for city_id in area_segmented_cities[1]:
        left_diff = cities[city_id][1] - areas[1][3]
        top_diff = areas[1][1] - cities[city_id][0]
        if left_diff < min_left_diff:
            min_left_diff = left_diff
            left_candidates.append(city_id)
        if top_diff < min_top_diff:
            min_top_diff = top_diff
            top_candidates.append(city_id)
    # 実験の結果、エリア4、エリア2との境界に近いもののうち2個から、最も領域の端の方にあるものを選ぶと良い解が得られた
    left = min(
        left_candidates[:2], key=lambda left_candidate: cities[left_candidate][0]
    )
    top = min(top_candidates[:2], key=lambda top_candidate: cities[top_candidate][1])

    # エリア3の都市の中でもっともエリア2に近いrightとエリア4に近いbottomを見つける
    for city_id in area_segmented_cities[3]:
        right_diff = cities[city_id][1] - areas[3][2]
        bottom_diff = cities[city_id][0] - areas[3][0]
        if right_diff < min_right_diff:
            min_right_diff = right_diff
            right_candidates.append(city_id)
        if bottom_diff < min_bottom_diff:
            min_bottom_diff = bottom_diff
            bottom_candidates.append(city_id)
    right = max(
        right_candidates[:2], key=lambda right_candidate: cities[right_candidate][0]
    )
    bottom = max(
        bottom_candidates[:2], key=lambda bottom_candidate: cities[bottom_candidate][1]
    )
    return left, top, right, bottom


# 最初の視点だけ指定して、あとはgreedyに任せる
def update_solver_area_segmented(original_cities, dist):
    areas, area_segmented_cities = split_cities(original_cities)
    left, _, _, _ = find_boundary_points(original_cities, areas, area_segmented_cities)

    # エリアごとに始点を固定して貪欲法で経路を見つける
    segmented_tours = [[] for i in range(5)]  # インデックスの0はdummy
    start_city = left
    for area, cities in enumerate(area_segmented_cities):
        if area == 0:
            continue
        tour = solver_greedy(cities, dist, start_city=start_city)
        tour = solve(cities, tour, dist)
        start_city = tour[-1]
        segmented_tours[area] = tour

    # 分割した経路をつなげる
    merged_tour = []
    for area, tour in enumerate(segmented_tours):
        if area == 1:
            merged_tour += tour
        else:
            merged_tour += tour[1:]
    tour_length = sum(
        dist[merged_tour[i]][merged_tour[(i + 1) % len(merged_tour)]]
        for i in range(len(merged_tour))
    )

    print("tour_length", tour_length)
    return merged_tour


# 貪欲法: 始点は指定可能
def solver_greedy(cities, dist, start_city=0):
    unvisited_cities = cities
    if start_city in cities:
        unvisited_cities.remove(start_city)

    current_city = start_city
    tour = [current_city]

    while unvisited_cities:
        next_city = min(unvisited_cities, key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    return tour


# 始点と終点を指定
def area_segmented_greedy_solver_with_two_opt(original_cities, dist):
    # 領域の端のx,y座標を見つける
    x_min, y_min, x_max, y_max = find_end_coords(original_cities)
    # 領域を4等分し、どのエリアに属すかで都市を分ける.
    areas, area_segmented_cities = split_cities(original_cities)
    # 4等分した境界付近の都市を見つける
    left, top, right, bottom = find_boundary_points(
        original_cities, areas, area_segmented_cities
    )

    # エリアごとに始点、終点を定める
    start_end_cities = {
        1: [left, top],
        2: [top, right],
        3: [right, bottom],
        4: [bottom, left],
    }

    # エリアごとに始点と終点を固定して貪欲法で経路を見つける
    segmented_tours = [[] for i in range(5)]
    for area, cities in enumerate(area_segmented_cities):
        if area == 0:
            continue
        start_city, end_city = start_end_cities[area]
        tour = start_end_fix_solver_greedy(cities, dist, start_city, end_city)
        tour = update_solve(len(cities), tour, dist)
        segmented_tours[area] = tour

    # 分割した経路をつなげる
    merged_tour = []
    for area, tour in enumerate(segmented_tours):
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


# 貪欲法: 始点と終点を固定する
def start_end_fix_solver_greedy(cities, dist, start_city, end_city):
    unvisited_cities = cities
    if start_city in cities:
        unvisited_cities.remove(start_city)
    if end_city in cities:
        unvisited_cities.remove(end_city)

    current_city = start_city
    tour = [current_city]

    while unvisited_cities:
        next_city = min(unvisited_cities, key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    tour.append(end_city)
    return tour


# 始点から終点の長さが最短となるように2optを行う
def update_solve(num_of_cities, tour, dist: list[list]):
    # start = time.time()
    # startからendまでの経路の長さを求める
    # endとstartは繋がない
    tour_length = sum(dist[tour[i]][tour[i + 1]] for i in range(num_of_cities - 1))
    is_updated = True
    while is_updated:
        is_updated = False
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
                    is_updated = True
    # end = time.time()
    # print(end - start)
    # print("tour_length", tour_length)

    return tour


def solve(cities, tour, dist: list[list], start_city=0):
    # start = time.time()
    prev_tour_length = sum(
        dist[tour[i]][tour[(i + 1) % len(cities)]] for i in range(len(cities))
    )
    tour_length = 0
    # 最後と最初をつなぐ
    prev_tour = tour
    # tour.append(start_city)
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


if __name__ == "__main__":
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    dist = cal_dist(cities)
    # tour = update_solver_area_segmented(cities, dist)
    tour = area_segmented_greedy_solver_with_two_opt(cities, dist)
    # print_tour(tour)
