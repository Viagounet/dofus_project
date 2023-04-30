import glob
import json
import time

from scipy.spatial.distance import cdist

from shortest_path import find_shortest_path, create_points_from_input
import pyautogui as pg

from utility import find_in_screen


class Bot:
    def __init__(self):
        self.player = Player()

    def run(self):
        time.sleep(2)
        print("Démarrage du bot !")
        print("En recherche de minerais..")
        minerals = self.player.tile.minerals_status()
        if minerals["fer"]:
            print("Fer détecté !")
            self.player.move("floor1")
            self.player.mine(minerals["fer"])
        if minerals["bronze"]:
            print("Bronze détecté !")
            self.player.move("floor1")
            self.player.mine(minerals["bronze"])
        if minerals["cuivre"]:
            print("Cuivre détecté !")
            self.player.move("floor0")
            self.player.mine(minerals["cuivre"])
        self.player.move("floor2")
        self.player.move("to_9_-19_BT")
        # self.player.move("cave")
        # self.player.patrol("floor0", "floor1")


class Player:
    def __init__(self):
        self.speed = 100
        self.tile = Tile(10, -19)
        self.position = "floor1"

    def move(self, point):
        path = self.tile.path(self.position, point)
        print("Joueur en direction de :", point)
        for path_info in path:
            point_name, point_coordinates = path_info
            if self.position == point_name:
                continue
            x, y = point_coordinates
            print(f"\t-> {point_name} {point_coordinates}")
            pg.moveTo(x, y)
            pg.click()
            time.sleep(self.tile.travelling_time(self.position, point_name))
            self.position = point_name
        print()

    def patrol(self, point1, point2):
        self.move(point1)
        self.move(point2)

    def mine(self, minerals_coordinates):
        for mineral_coordinates in minerals_coordinates:
            print(f"Minage de", mineral_coordinates)
            # A None mistake here
            x, y = mineral_coordinates
            pg.moveTo(x, y)
            pg.click()
            time.sleep(3)
        self.move(self.position)


class Tile:
    def __init__(self, x, y):
        with open(f"{x}_{y}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.coordinates = data["points"]
        self.points = create_points_from_input(data["links"])

    def path(self, point1: str, point2: str):
        print(find_shortest_path(self.points, point1, point2))
        return [(point, self.coordinates[point]) for point in find_shortest_path(self.points, point1, point2)]

    def distance(self, point1: str, point2: str):
        x0, y0 = self.coordinates[point1]
        x1, y1 = self.coordinates[point2]
        return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5

    def minerals_status(self):
        minerals = {"fer": [],
                    "cuivre": [],
                    "bronze": []}
        for img in glob.glob("imgs/*_full*.png"):
            boxes = find_in_screen(img, "temp.png")
            if boxes:
                for key in minerals.keys():
                    if key in img:
                        for box in boxes:
                            box = box[0]
                            minerals[key].append(((box[0][0] + box[1][0]) / 2,
                                                  (box[0][1] + box[1][1]) / 2))
        return minerals

    def travelling_time(self, point1: str, point2: str):
        return self.distance(point1, point2) / 250


class Map:
    def __init__(self):
        pass


my_bot = Bot()
my_bot.run()
