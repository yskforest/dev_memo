import matplotlib.pyplot as plt
import copy
import urllib.request

# https://qiita.com/maskot1977/items/e1819b7a1053eb9f7d61

def minimum_tree(neighbor, start):
    visited = []
    queue = []
    result = []
    queue.append([start, start, 0])
    while len(queue) > 0:
        queue = sorted(queue, key=lambda e: e[2])
        curr_i, curr_j, accum_dist = queue.pop(0)
        if (curr_i in visited) and (curr_j in visited):
            continue
        visited.append(curr_i)
        visited.append(curr_j)
        if curr_i != curr_j:
            result.append([curr_i, curr_j])
        for curr in [curr_i, curr_j]:
            for nei in neighbor[curr]:
                if nei[1] in visited:
                    continue
                queue.append([curr, nei[1], nei[0] + accum_dist])
    return result

def shortest_path(original_neighbor, start, goal):
    neighbor = {}
    for edge in minimum_tree(original_neighbor, start):
        if edge[0] not in neighbor.keys():
            neighbor.update({edge[0]:[]})
        neighbor[edge[0]].append(edge[1])
        if edge[1] not in neighbor.keys():
            neighbor.update({edge[1]:[]})
        neighbor[edge[1]].append(edge[0])
    queue = []
    queue.append([start])
    result = []
    while len(queue) > 0:
        curr_path = queue.pop()
        if curr_path[-1] == goal:
            result.append(curr_path)
            break
        for nei in neighbor[curr_path[-1]]:
            if nei in curr_path:
                continue
            new_path = copy.copy(curr_path)
            new_path.append(nei)
            queue.append(new_path)
    return result

def draw_path(all_cities, all_xs, all_ys, paths):
    city2xy = {}
    path_xs = []
    path_ys = []
    for city, x, y in zip(all_cities, all_xs, all_ys):
        city2xy.update({city:[x, y]})
    for path in paths:
        for city in path:
            path_xs.append(city2xy[city][0])
            path_ys.append(city2xy[city][1])
    plt.figure(figsize=(10, 8))
    plt.title("Prefectural capitals in Japan")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    shown_cities = []
    for path in paths:
        for i in range(len(path) - 1):
            city1 = path[i]
            city2 = path[i + 1]
            x1 = city2xy[city1][0]
            y1 = city2xy[city1][1]
            x2 = city2xy[city2][0]
            y2 = city2xy[city2][1]
            plt.plot([x1, x2], [y1, y2], 'k-', alpha=0.5, lw=2)
            if city1 not in shown_cities:
                shown_cities.append(city1)
            if city2 not in shown_cities:
                shown_cities.append(city2)
    plt.scatter(path_xs, path_ys)
    for city in shown_cities:
        plt.text(city2xy[city][0], city2xy[city][1], city, alpha=0.5, size=12)
    plt.show()


def main():
    url = 'https://raw.githubusercontent.com/maskot1977/ipython_notebook/master/toydata/location.txt'
    urllib.request.urlretrieve(url, 'location.txt')

    url = 'https://raw.githubusercontent.com/maskot1977/ipython_notebook/master/toydata/walk.txt'
    urllib.request.urlretrieve(url, 'walk.txt') # Python 3 の場合

    # ダウンロードしたデータから、列ごとに数字を読み込んでリストに格納する。
    col1 = [] # ０列目の数字を格納する予定のリスト
    col2 = [] # １列目の数字を格納する予定のリスト
    col3 = [] # ２列目の数字を格納する予定のリスト
    for i, line in enumerate(open('location.txt')): # ファイルを開いて一行一行読み込む
        if i == 0: # ０番目の行の場合
            continue # 次の行に行く
        c = line.split(",") # 行をコンマで分割したものをcというリストに入れる
        col1.append(c[0]) # ０列目の単語col1に入れる
        col2.append(float(c[1])) # １列目の単語を実数に変換してcol2に入れる
        col3.append(float(c[2])) # ２列目の単語を実数に変換してcol3に入れる
    print (col1)

    # ダウンロードしたデータから、列ごとに数字を読み込んでリストに格納する。
    col4 = [] # ０列目の数字を格納する予定のリスト
    col5 = [] # １列目の数字を格納する予定のリスト
    col6 = [] # ２列目の数字を格納する予定のリスト
    for i, line in enumerate(open('walk.txt')): # ファイルを開いて一行一行読み込む
        if i == 0: # ０番目の行の場合
            continue # 次の行に行く
        c = line.split() # 行を空白文字で分割したものをcというリストに入れる
        col4.append(c[0]) # ０列目の単語をcol4に入れる
        col5.append(c[1]) # １列目の単語をcol5に入れる
        col6.append(float(c[2])) # ２列目の単語を実数に変換してcol6に入れる

    walk_neighbor = {}
    for city1, city2, walk in zip(col4, col5, col6):
        if city1 not in walk_neighbor.keys():
            walk_neighbor.update({city1:[]})
        walk_neighbor[city1].append([walk, city2])
        if city2 not in walk_neighbor.keys():
            walk_neighbor.update({city2:[]})
        walk_neighbor[city2].append([walk, city1])
    # 東京に隣接している都市を、近い順に並べる

    print (sorted(walk_neighbor["Tokyo"]))   
    draw_path(col1, col3, col2, shortest_path(walk_neighbor, "Nagasaki", "Tokyo"))


if __name__ == '__main__':
    main()