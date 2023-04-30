import json
import sys


class Point:
    def __init__(self, start_point, end_point, coordinates, orientation):
        self.start_point = start_point
        self.end_point = end_point
        self.coordinates = coordinates
        self.orientation = orientation


def create_points_from_input(input_data):
    points = []
    for point_data in input_data:
        point = Point(point_data["start_point"], point_data["end_point"], point_data["coordinates"],
                      point_data["orientation"])
        points.append(point)
    return points


def find_shortest_path(points, start, end, path=[]):
    path = path + [start]

    if start == end:
        return path

    shortest = None
    for point in points:
        if point.start_point == start:
            if point.end_point not in path:
                newpath = find_shortest_path(points, point.end_point, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        elif (point.orientation == "bidirectional" and point.end_point == start) or (point.orientation == "end_to_start" and point.end_point == start):
            if point.start_point not in path:
                newpath = find_shortest_path(points, point.start_point, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
    return shortest

# with open("10_-19.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
# points = create_points_from_input(data["links"])
#
# start = "fer1"
# end = "floor2"
#
# path = find_shortest_path(points, start, end)
# print([data["points"][point] for point in path])
# print([point for point in path])

