__author__ = 'krekle'

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
from collections import namedtuple
from math import fabs


class Map:

    def __init__(self):
        self.coords = namedtuple('Coordinates', 'y,x')
        self.grid = Map.read_map()
        #print(self.grid)
        self.start, self.end, self.closed = self.find_extremes()
        self.open = set()
        self.current = self.start

    def find_extremes(self):
        a = None
        b = None
        wall = set()
        for y in range(0, len(self.grid)):
            for x in range(0, len(self.grid[y])):
                if self.grid[y][x] is 'A':
                    #a = str(y) + ',' + str(x)
                    a = self.coords(y, x)
                elif self.grid[y][x] is'B':
                    #b = str(y) + ',' + str(x)
                    b = self.coords(y, x)
                elif self.grid[y][x] is'#':
                    wall.add(self.coords(y, x))
        return a, b, wall

    def manhattan_distance(self, node_coordinate):
        return fabs(self.end.x - node_coordinate.x) + fabs(self.end.y - node_coordinate.y)

    def terrain_score(self, node_coordinate):
        terrain = self.grid[node_coordinate.y][node_coordinate.x]
        if terrain is 'w':
            return 100
        elif terrain is 'm':
            return 50
        elif terrain is 'f':
            return 10
        elif terrain is 'g':
            return 5
        elif terrain is 'r':
            return 1
        else:
            return 0

    def valid_tile(self, node):
        if node.x >= 0 and node.y >= 0:
            try:
                temp = self.grid[node.y][node.x]
                return True
            except:
                return False
        else:
            return False


    def get_parents(self, node_coordinate):
        parents = []

        parents.append([self.coords(node_coordinate.y-1, node_coordinate.x), 0]) #up
        parents.append([self.coords(node_coordinate.y+1, node_coordinate.x), 0]) #down
        parents.append([self.coords(node_coordinate.y, node_coordinate.x-1), 0]) #left
        parents.append([self.coords(node_coordinate.y, node_coordinate.x+1), 0]) #right

        for i in range(len(parents)):
            print(parents[i][0])
            if parents[i][0] not in self.closed and self.valid_tile(parents[i][0]):
                parents[i].append(int(self.manhattan_distance(parents[i][0])))
                parents[i][1] += self.terrain_score(parents[i][0])
                self.open.add(parents[i][0])
        # Sorterer på vekt
        return sorted(parents, key=lambda x: x[1])

    def move_logical(self):
        moves = self.get_parents(self.current)
        print moves
        raw_input("ds")
        if self.current.x == self.end.x and self.current.y == self.end.y:
            print("GRATTIS!")
            self.print_map()
            exit()
        elif not moves:
            self.current = self.start
        else:
            self.closed.add(self.current)
            self.current = moves[0][0]
        self.print_map()

    def print_map(self):
        self.grid[self.current.y][self.current.x] = "o"
        for y in range(len(self.grid)):
            print(self.grid[y])
        self.grid[self.current.y][self.current.x] = '+'

    @staticmethod
    def read_map():
        #name = str(raw_input('skriv inn bane: '))
        name = 'board-1-4.txt'
        try:
            with open(name) as f:
                return [list(i) for i in f.readlines()]
        except:
            print('error, no such map')


board = Map()
while True:
    board.move_logical()
    wait = raw_input('moved to ' + str(board.current.y) + str(board.current.x))