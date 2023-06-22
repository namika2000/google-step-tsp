#!/usr/bin/env python3

import math
from common import print_tour, read_input
import sys


def distance(city_1: list[float], city_2: list[float]) -> float:
    return math.sqrt((city_1[0] - city_2[0]) ** 2 + (city_1[1] - city_2[1]) ** 2)


# すべての都市間の距離を求める
# dist[i][j] = dist[j][i] = cities[i]とcities[j]の距離
def cal_dist(cities: list[list[float]]) -> list[list[float]]:
    N = len(cities)
    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])
    return dist


def find_end_coords(cities: list[list[float]]) -> list[float]:
    """
    領域の端のx,y座標を算出

    Args:
        cities: 都市のxy座標を要素とするリスト

    Returns:
        list[int]: 領域の最も端の座標. [x_min, y_min, x_max, y_max]
    """
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


def split_cities(cities: list[list[float]]) -> list[dict, list]:
    """
    領域を4等分し、どの領域に属すかで都市を分ける.

    Returns:
        list[dict, list]: [areas, area_segmented_cities]
        areas (dict): 各エリアの範囲を保持した辞書. エリア番号をキー、そのエリアの範囲[xmin, xmax, ymin, ymax]を値とする
        area_segmented_cities (list[list[int]]):  各エリアに属する都市のidを保持したリスト. インデックスをエリア番号、そのエリアに属する都市のリストを要素として持つ
    """
    N = len(cities)
    x_min, y_min, x_max, y_max = find_end_coords(cities)

    # エリアごとの範囲を設定
    # areas: {area_number: [x_min, x_max, y_min, y_max]}
    areas: dict = {
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

    # インデックスをエリア番号として、そのエリアに属する都市のリストを要素として持つリスト
    area_segmented_cities: list[list[int]] = [[] for _ in range(5)]  # インデックスの0はdummy
    # すべての都市のidを記録したリスト
    city_id_list: list[int] = [i for i in range(N)]
    for area_id, area in areas.items():
        # そのエリアに含まれる都市のidを記録したリスト
        cities_of_area: list[int] = []
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
def find_boundary_points(
    cities: list[float], areas: dict, area_segmented_cities: list[list[int]]
) -> list[int]:
    """
    境界に近い4つの都市を見つけ、そのidを返す

    Args:
        cities (list[float]): 都市のxy座標
        areas (dict): エリアごとの範囲
        area_segmented_cities (list[list[int]]): 都市をどのエリアに属するかで分けたもの

    Returns:
        list[int]: 境界に近い4つの都市のid
    """
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

    for city_id in area_segmented_cities[1]:
        left_diff = areas[1][3] - cities[city_id][1]
        top_diff = areas[1][1] - cities[city_id][0]
        if left_diff < min_left_diff:
            min_left_diff = left_diff
            left_candidates.append(city_id)
        if top_diff < min_top_diff:
            min_top_diff = top_diff
            top_candidates.append(city_id)
    # 実験の結果、エリア4、エリア2との境界に近いもののうち2個のうち、領域の端の方にあるものを選ぶと良い解が得られた
    left = min(
        left_candidates[-2:], key=lambda left_candidate: cities[left_candidate][0]
    )
    top = min(top_candidates[-2:], key=lambda top_candidate: cities[top_candidate][1])

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
        right_candidates[-2:], key=lambda right_candidate: cities[right_candidate][0]
    )
    bottom = max(
        bottom_candidates[-2:], key=lambda bottom_candidate: cities[bottom_candidate][1]
    )
    return left, top, right, bottom


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


# 2opt
# 領域ごとに2optを適用する際に使用尾
# tourから最後の要素だけを抜いたものを返す(次の領域の始点と前の領域の終点が重複するため)
def update_two_opt(tour, dist: list[list]):
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

    return tour[:-1]


# 普通の2opt
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


# 大元の関数
def solve(original_cities: list[float]) -> list[int]:
    """
    1. 領域を四等分する
    2. 領域の境界に近い4点を見つける
    3. それらを始点、終点として、各領域で最適経路を求める(貪欲法で初期経路を設定、2optを適用)
    4. 各領域の最適経路を統合
    5. 統合後の経路に2optを適用

    Args:
        original_cities (list[float]): 全ての都市のxy座標

    Returns:
        list[int]: 最適化した経路
    """
    # 都市間の距離を求める
    dist = cal_dist(original_cities)

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
        tour = update_two_opt(tour, dist)
        segmented_tours[area] = tour

    # 分割した経路をつなげる
    merged_tour = []
    for area, tour in enumerate(segmented_tours):
        merged_tour += tour

    # 全体で2optをしてみる
    merged_tour = normal_two_opt(merged_tour, dist)
    tour_length = sum(
        dist[merged_tour[i]][merged_tour[(i + 1) % len(merged_tour)]]
        for i in range(len(merged_tour))
    )

    print("tour_length", tour_length)
    return merged_tour


if __name__ == "__main__":
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    tour = solve(cities)
    # print_tour(tour)
