#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Imports

Stuff we need to run the code
"""

import traceback
from math import fabs
from Tkinter import *

"""
Board class

Consists of all a matrix of Nodes
"""

class Board:
    # Constructor
    def __init__(self, gui):
        # Reference to the gui class
        self.gui = gui
        
        # Contains the entire board
        self.board = []
        
        # List of open Nodes
        self.open = list()
        
        # List of closed Nodes
        self.closed = list()
        
        # The finished path of Nodes leading from start to goal
        self.path = list()
        
        # The goal Node
        self.goal = None
        
        # Sizes defining the board
        self.size_x = None
        self.size_y = None
        
        # Algorithm to use
        self.algorithm = 'derp'
        
        # Delay to use
        self.delay = 0
    
    # Calculate manhatten score for a given Node
    def manhattan_distance(self, node):
        return fabs(self.goal.x - node.x) + fabs(self.goal.y - node.y)
    
    # Calculate terrain score (if any) for a given Node
    def terrain_score(self, node):
        score = {'w': 100, 'm': 50, 'f': 10, 'g': 5, 'r': 1}
        return score.get(node.type, 0)
    
    # Takes a matrix of chars, used to initialize the Nodes
    def add_board(self, lines):
        # Loop y items
        for y in range(len(lines)):
            temp_line = []
            
            # Loop x items
            for x in range(len(lines[y])):
                # Ignore chars consisting of newlines
                if lines[y][x] != '\n':
                    # Create new Node
                    temp_node = Node(self, y, x, lines[y][x])
                    
                    # Set special Nodes
                    if lines[y][x] == 'B':
                        # Goal Node
                        self.goal = temp_node
                    elif lines[y][x] == 'A':
                        # Start Node, add to the open set
                        self.open.append(temp_node)
                    elif lines[y][x] == '#':
                        # Add all walls to the closed set
                        self.closed.append(temp_node)
                    
                    # Add node to temp array
                    temp_line.append(temp_node)
                    
            # Calculate map width
            if self.size_x is None:
                self.size_x = len(temp_line) - 1
            
            # Add array to board
            self.board.append(temp_line)
        
        # Calculate map height
        if self.size_y is None:
            self.size_y = len(self.board) - 1
        
        # Define variables for the start Node
        if (len(self.open) > 0):
            self.open[0].g = 0
            self.open[0].f = self.manhattan_distance(self.open[0])
    
    # Sorts all the open Nodes on manhatten score
    def sort_open(self):
        sorted(self.open, key=lambda x: x.f)
    
    # Returns all parents for the current Node
    def get_parents(self, node):
        # Get all parents
        parents = []
        
        # Get valid parents that are not outside the map
        if (node.y > 0): # Up
            parents.append(self.board[node.y - 1][node.x])
        if (node.y < self.size_y): # Down
            parents.append(self.board[node.y + 1][node.x])
        if (node.x > 0): # Left
            parents.append(self.board[node.y][node.x - 1])
        if (node.x < self.size_x): # Right
            parents.append(self.board[node.y][node.x + 1])
        
        # Return list of parents
        return parents
    
    # Distance between two nodes
    def distance_between(self, current, parent):
        return fabs(current.x - parent.x) + fabs(current.y - parent.y)
    
    # Reccursive reconstruct the path from goal to start
    def reconstruct_path(self, current):
        if current.navigated_from is not None:
            current.on_path = True
            self.path.append(current)
            self.reconstruct_path(current.navigated_from)
            
            # Draw
            self.gui.draw(self.board)
    
    # Draw the path in the terminal
    def draw_path(self):
        output = ''
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                current_node = self.board[i][j]
                if current_node in self.path or current_node.type == 'A':
                    output = output + 'o | '
                else:
                    output = output + str(self.board[i][j]) + ' | '
            output = output + "\n"
        print output
    
    # Selected what algorithm to use
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
    
    # Selecting what delay to use
    def set_delay(self, delay):
        self.delay = delay
    
    # Loops all the Nodes in the open set, evaluating scores for each of them
    def run(self):
        # Loop at long at the list of open Nodes is not empty
        while len(self.open) > 0:
            # Sort the Nodes
            self.sort_open()
            
            # Define what Node we should work on
            current = self.open[0]
            
            # Check if we found the goal
            if current.type == 'B':
                # We found the goal
                self.reconstruct_path(self.goal)
                self.draw_path()
                return;
            
            # Remove from open and add to closed
            self.open.pop(0)
            self.closed.append(current)
            
            temp_parents = self.get_parents(current)
            for parent in temp_parents:
                # Check that the current parent is not already closed
                if parent in self.closed:
                    continue
                
                # Calculate new g score for this node
                new_g_score = current.g + self.distance_between(current, parent)
                
                # Check if we should evaluate the parent node
                if parent not in self.open or new_g_score < parent.g:
                    # Define how we naviaged to the Node
                    parent.navigated_from = current
                    
                    # Set new values
                    parent.g = new_g_score + self.terrain_score(parent)
                    parent.f = parent.g #+ self.manhattan_distance(parent)
                    
                    # If not in open list, add to list
                    if parent not in self.open:
                        self.open.append(parent)
            # Draw
            self.gui.draw(self.board)
        
        # No path was found, return None
        return None


"""
Node class

Represents one node on the board
"""

class Node:
    # Constructor
    def __init__(self, board, y, x, type):
        # Reference to the board class
        self.board = board
        
        # Coordinates
        self.x = x
        self.y = y
        
        # Type of Node
        self.type = type
        
        # G and F scores
        self.g = 0
        self.f = 0
        
        # Reference to the Node we navigated from
        self.navigated_from = None
        
        self.on_path = False
    
    # For debugging
    def coor(self):
        return '[' + str(self.x) + ', ' + str(self.y) + ']'
    def __repr__(self):
        return self.type


"""
Run class

The class opening files etc
"""

class Run:
    # Constructor
    def __init__(self, gui):
        self.file = None
        self.board = None
        self.gui = gui
    
    # Open a map file
    def open_file(self, file_name):
        # Kill earlier reference to Board
        self.boar = None
        
        # Create new instance of Board
        self.board = Board(self.gui)
        
        # Open file
        try:
            with open('boards/' + file_name) as f:
                lines = []
                for i in f.readlines():
                    lines.append(list(i))
                self.board.add_board(lines)
                self.board.run()
        except:
            print traceback.print_exc()
    
    # Set algorithm
    def set_algorithm(self, type):
        self.board.set_algorithm(type)
    
    # Set delay
    def set_delay(self, delay):
        self.board.set_delay(delay)
    
    # Run algorithm
    def run(self):
        # Calculate scores
        #self.board.run()
        print 'fuck'
    
    def size_x(self):
        return self.board.size_x
    def size_y(self):
        return self.board.size_y

"""
Gui class

The class creating a visual gui for the algorithm solving the problem
"""

class Gui(Tk):
    # Constructor
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        
        #Force fullscreen
        self.geometry("{0}x{1}+0+0".format(
            self.winfo_screenwidth()-3, self.winfo_screenheight()-3))
        self.bind('<Escape>',self.toggle_geom) 
        
        
        # The canvas we're drawing in
        self.canvas = None
        
        self.title("Astar")
        self._geom='200x200+0+0'
        
        # Reference to a new frame
        self.parent = Frame()
        self.parent.pack()
        
        # Reference to a menu
        self.menubar = Menu(self)
        
        # Reference to the Run class, executing the algorithm
        self.run = Run(self)
        
        # The sizof the squares
        #self.parent.geometry(self.calculate_window_size(self.run.size_x, self.run.size_y))
        self.sqsize = 30
        
        # Create a pulldown menu for chosing what level to play
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Board-1-1", command=lambda: self.play_level('board-1-1.txt'))
        self.filemenu.add_command(label="Board-1-2", command=lambda: self.play_level('board-1-2.txt'))
        self.filemenu.add_command(label="Board-1-3", command=lambda: self.play_level('board-1-3.txt'))
        self.filemenu.add_command(label="Board-1-4", command=lambda: self.play_level('board-1-4.txt'))
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Board-2-1", command=lambda: self.play_level('board-2-1.txt'))
        self.filemenu.add_command(label="Board-2-2", command=lambda: self.play_level('board-2-2.txt'))
        self.filemenu.add_command(label="Board-2-3", command=lambda: self.play_level('board-2-3.txt'))
        self.filemenu.add_command(label="Board-2-4", command=lambda: self.play_level('board-2-4.txt'))
        self.filemenu.add_separator()
        self.menubar.add_cascade(label="Chose board", menu=self.filemenu)

        # Create a pulldown menu for chosing what algorithm to use
        self.algmenu = Menu(self.menubar, tearoff=0)
        self.algmenu.add_command(label="Manhattan Distance", command=lambda: self.play_level('manhattan distance'))
        self.algmenu.add_command(label="Euclid", command=lambda: self.play_level('euclid something'))
        self.algmenu.add_separator()
        self.algmenu.add_command(label="Astar", command=lambda: self.play_level('Astar regular'))
        self.algmenu.add_command(label="BFS", command=lambda: self.play_level('BFS'))
        self.algmenu.add_command(label="Dijkstra", command=lambda: self.play_level('Dijkstra'))
        self.algmenu.add_separator()
        self.menubar.add_cascade(label="Chose algorithm", menu=self.algmenu)
        
        # Create a pulldown menu for chosing delays
        self.delaymenu = Menu(self.menubar, tearoff=0)
        self.delaymenu.add_command(label="No delay", command=lambda: self.set_delay('0'))
        self.delaymenu.add_command(label="100ms", command=lambda: self.set_delay('100ms'))
        self.delaymenu.add_separator()
        self.menubar.add_cascade(label="Chose delay", menu=self.delaymenu)
        
        # Menu element for running the application
        self.menubar.add_command(label="Run!", command= self.run)
        
        # Menu element for closing the application
        self.menubar.add_command(label="Quit!", command= self.quit)
        
        # Apply the config
        self.config(menu=self.menubar)
    
    # Drawing the entire board
    def draw(self, grid):
        if self.canvas is not None:
            self.canvas.destroy()
        
        icon = {".": "#bfbfbf", 
                "#": "#4c4c4c", 
                "A": "#4c4",
                "B": "#b20000", 
                "w": "#6666ff", 
                "m": "#731d1d", 
                "f": "#006600", 
                "g": "#329932", 
                "r": "#b2d8b2"}
        
        self.canvas = Canvas(self, bg='white', width=500, height=500)
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                print str(y)+","+str(x)
                top = y * self.sqsize
                left = x * self.sqsize
                bottom = y * self.sqsize + self.sqsize -2
                right = x * self.sqsize + self.sqsize -2
                self.canvas.create_rectangle(left, top, right, bottom,
                                    outline=icon.get(grid[y][x].type), fill=icon.get(grid[y][x].type))
                
                # Check if on path
                if grid[y][x].on_path:
                    self.canvas.create_oval(left, top, right, bottom, fill="#000")

        self.canvas.pack(fill=BOTH, expand=1)
        
    #Toggle minimize
    def toggle_geom(self,event):
        geom=self.winfo_geometry()
        print(geom,self._geom)
        self.geometry(self._geom)
        self._geom=geom

    # Deciding what level to play
    def play_level(self, level):
        self.run.open_file(level)
    
    def calculate_window_size(self, x, y):
        return str(x*30 + 'x' + y*30)
    
    # Deciding what algoruthm to use
    def choose_algorithm(self, algorithm):
        self.run.set_algorithm(algorithm)
    
    def set_delay(self, delay):
        self.run.set_delay(delay)
    
    def run(self):
        # self.run.run()
        print 'rifl'


app = Gui()
app.mainloop()
