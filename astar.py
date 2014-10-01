#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Imports

Stuff we need to run the code
"""

from math import fabs
from Tkinter import *

"""
Board class

Consists of all a matrix of Nodes
"""

class Board:
    # Constructor
    def __init__(self, gui, algorithm):
        # Reference to the gui class
        self.gui = gui
        
        # Contains the entire board
        self.board = []
        
        # List of open Nodes
        self.open = list()
        
        # List of closed Nodes
        self.closed = list()
        
        # The goal Node
        self.goal = None
        
        # Sizes defining the board
        self.size_x = None
        self.size_y = None
        
        # Algorithm to use
        # 0 = astar regular, 1 = BFS, 2 = Dijkstra
        self.algorithm = algorithm
    
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
            # Empty array to store the current line
            temp_line = []
            
            # Loop x items
            for x in range(len(lines[y])):
                # Ignore elements consisting of newlines
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
            self.open[0].f = self.manhattan_distance(self.open[0]) + self.terrain_score(self.open[0])
            self.open[0].on_path = True
    
    # Sorts all the open Nodes on manhatten score
    def sort_open(self):
        # Check what algorithm to sort by
        if self.algorithm is 0:
            self.open = sorted(self.open, key=lambda x: float(x.f))
        elif self.algorithm is 1:
            # No sorting, FIFO
            self.open = self.open # this is an important line
        else:
            # Dijkstra, sort based on lowes G score, discard H
            self.open = sorted(self.open, key=lambda x: float(x.g))

    # Returns all parents for the current Node
    def get_parents(self, node):
        # Init array for the parents
        parents = []
        
        # Get valid parents that are in the map
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
    
    # Reccursive reconstruct the path from goal to start
    def reconstruct_path(self, current):
        if current.navigated_from is not None:
            current.on_path = True
            self.reconstruct_path(current.navigated_from)
            
    
    # Selected what algorithm to use
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
    
    # Loops all the Nodes in the open set, evaluating scores for each of them
    def run(self):
        # Check if finished
        if len(self.open) == 0:
            # Current map is finished, kill
            self.gui.draw([], True)
            return;
        
        # Sort the Nodes
        self.sort_open()
        
        # Select the Node to evaluate
        current = self.open[0]
        
        # Check if we found the goal
        if current.type == 'B':
            # We found the goal!
            self.reconstruct_path(self.goal)
            
            # Calling draw one last time
            self.gui.draw(self.board, True)
            return;
        
        # Remove from open and add to closed
        self.open.pop(0)
        self.closed.append(current)
        current.closed = True
        
        # Get all parents for the current node
        temp_parents = self.get_parents(current)
        
        # Loop all the parents
        for parent in temp_parents:
            # Check that the current parent is not already closed
            if parent in self.closed:
                continue
            
            # Calculate new g score for this node
            new_g_score = current.g + 0 + self.terrain_score(parent)
            
            # Check if we should evaluate the parent node
            if parent not in self.open or new_g_score < parent.g:
                # Define how we naviaged to the Node
                parent.navigated_from = current
                
                # Set new values
                parent.g = new_g_score
                parent.f = parent.g + self.manhattan_distance(parent)
                
                # If not in open list, add to list
                if parent not in self.open:
                    self.open.append(parent)
        
        # Draw
        self.gui.draw(self.board, False)


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
        
        # g and f scores
        self.g = 0
        self.f = 0
        
        # Reference to the Node we navigated from
        self.navigated_from = None
        
        # Variables that decide how to paint the map
        self.on_path = False
        self.closed = False
  

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

        # Algorithm to use, default = 0 -> astar
        self.algorithm = 0
    
    # Open a map file
    def open_file(self, file_name):
        # Kill earlier reference to Board
        self.board = None

        # Create new instance of Board
        self.board = Board(self.gui, self.algorithm)
        
        # Open file
        try:
            with open('boards/' + file_name) as f:
                lines = []
                for i in f.readlines():
                    lines.append(list(i))
                self.board.add_board(lines)
        except:
            print 'Map not found...'
    
    # Set algorithm
    def set_algorithm(self, type):
        self.algorithm = type
        # Does nothin as it sets the alogorithm to late
        #self.board.set_algorithm(type)
    
    # Set delay
    def set_delay(self, delay):
        self.board.set_delay(delay)
    
    # Run algorithm
    def run(self):
        # Calculate scores
        self.board.run()


"""
Gui class

The class creating a visual gui for the algorithm solving the problem
"""

class Gui(Tk):
    # Constructor
    def __init__(self, *args, **kwargs):
        # Call super
        Tk.__init__(self, *args, **kwargs)
        
        # Force fullscreen
        self.geometry("{0}x{1}+0+0".format(
            self.winfo_screenwidth()-3, self.winfo_screenheight()-3)) 
        
        # The canvas we're drawing in
        self.canvas = None
        
        # Set the title
        self.title("A* - Kristian Ekle & Thomas Gautvedt")

        # Reference to a menu
        self.menubar = Menu(self)
        
        # Reference to the Run class, executing the algorithm
        self.run = Run(self)
        
        # The sizof the squares in the map
        self.sqsize = 30
        
        # Defining the colors for the icons
        self.icon = {
            ".": "#bfbfbf", 
            "#": "#4c4c4c", 
            "A": "#4c4",
            "B": "#b20000", 
            "w": "#6666ff", 
            "m": "#731d1d", 
            "f": "#006600", 
            "g": "#329932", 
            "r": "#b2d8b2"
        }
        
        # How long we should wait between each redraw
        self.delay = 20
        
        # Radiobuttons
        self.v1 = None
        self.v2 = None
        self.v3 = None
        
        # Populate the menues
        self.populate_menu()
    
    # Populates the menu
    def populate_menu(self):
        # Dummy
        self.v1 = IntVar()
        self.v2 = IntVar()
        self.v2.set(1)
        self.v3 = IntVar()
        self.v3.set(1)
        
        
        # Create a pulldown menu for chosing what level to play
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_radiobutton(label="Board-1-1",
                                      variable = self.v1,
                                      command=lambda: self.play_level('board-1-1.txt'))
        self.filemenu.add_radiobutton(label="Board-1-2",
                                      variable = self.v1,
                                      command=lambda: self.play_level('board-1-2.txt'))
        self.filemenu.add_radiobutton(label="Board-1-3",
                                      variable = self.v1,
                                      command=lambda: self.play_level('board-1-3.txt'))
        self.filemenu.add_radiobutton(label="Board-1-4",
                                      variable = self.v1,
                                      command=lambda: self.play_level('board-1-4.txt'))
        self.filemenu.add_separator()
        self.filemenu.add_radiobutton(label="Board-2-1",
                                      variable = self.v1,
                                      command=lambda: self.play_level('board-2-1.txt'))
        self.filemenu.add_radiobutton(label="Board-2-2",
                                      variable = self.v1,
                                      command=lambda: self.play_level('board-2-2.txt'))
        self.filemenu.add_radiobutton(label="Board-2-3",
                                      variable = self.v1,
                                      command=lambda: self.play_level('board-2-3.txt'))
        self.filemenu.add_radiobutton(label="Board-2-4",
                                      variable = self.v1,
                                      command=lambda: self.play_level('board-2-4.txt'))
        self.menubar.add_cascade(label="Boards", menu=self.filemenu)

        # Create a pulldown menu for chosing what algorithm to use
        self.algmenu = Menu(self.menubar, tearoff=0)
        self.algmenu.add_radiobutton(label="Astar",
                                     variable = self.v2,
                                     value = 1,
                                     command=lambda: self.choose_algorithm(0))
        self.algmenu.add_radiobutton(label="BFS",
                                     variable = self.v2,
                                     command=lambda: self.choose_algorithm(1))
        self.algmenu.add_radiobutton(label="Dijkstra",
                                     variable = self.v2,
                                     command=lambda: self.choose_algorithm(2))
        self.menubar.add_cascade(label="Algorithms", menu=self.algmenu)
        
        # Create a pulldown menu for chosing delays
        self.delaymenu = Menu(self.menubar, tearoff=0)
        self.delaymenu.add_radiobutton(label="No delay",
                                       variable = self.v3,
                                       value = 1,
                                       command=lambda: self.set_delay('0'))
        self.delaymenu.add_radiobutton(label="20ms",
                                       variable = self.v3,
                                       command=lambda: self.set_delay('20'))
        self.delaymenu.add_radiobutton(label="50ms",
                                       variable = self.v3,
                                       command=lambda: self.set_delay('50'))
        self.delaymenu.add_radiobutton(label="100ms",
                                       variable = self.v3,
                                       command=lambda: self.set_delay('100'))
        self.delaymenu.add_radiobutton(label="200ms",
                                       variable = self.v3,
                                       command=lambda: self.set_delay('200'))
        self.delaymenu.add_radiobutton(label="500ms",
                                       variable = self.v3,
                                       command=lambda: self.set_delay('500'))
        self.delaymenu.add_radiobutton(label="1 sec",
                                       variable = self.v3,
                                       command=lambda: self.set_delay('1000'))
        self.menubar.add_cascade(label="Delay", menu=self.delaymenu)
        
        # Menu element for closing the application
        self.menubar.add_command(label="Quit!", command= self.quit)
        
        # Apply the config
        self.config(menu=self.menubar)
    
    # Drawing the board
    def draw(self, grid, finished):
        # Kill if no grid was returned and finished flag is True
        if len(grid) is 0 and finished:
            return
        
        # Avoid redrawing on top of the canvas
        if self.canvas is not None:
            self.canvas.pack_forget()
        
        # New canvas
        self.canvas = Canvas(self, bg='white')
        
        # Loop the grid
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                # Define some sizes
                top = y * self.sqsize
                left = x * self.sqsize
                bottom = y * self.sqsize + self.sqsize - 2
                right = x * self.sqsize + self.sqsize - 2
                
                # Store current Node
                current_node = grid[y][x]
                
                # Check if current Node is closed or not
                if current_node.closed == False:
                    self.canvas.create_rectangle(left, top, right, bottom,
                                outline="#ff0000",
                                fill=self.icon.get(current_node.type))
                else:
                    self.canvas.create_rectangle(left, top, right, bottom,
                                outline=self.icon.get(current_node.type),
                                fill=self.icon.get(current_node.type))
                
                # Check if on path
                if grid[y][x].on_path:
                    self.canvas.create_oval(left, top, right, bottom, fill="#000")
        
        # Pack
        self.canvas.pack(fill=BOTH, expand=1)
        
        # Wait and redraw if not finished
        if finished is False:
            self.after(self.delay, self.run.run)

    # Deciding what level to play
    def play_level(self, level):
        # Open file
        self.run.open_file(level)
        
        # Run!
        self.run.run()
    
    # Deciding what algoruthm to use
    def choose_algorithm(self, algorithm):
        self.run.set_algorithm(algorithm)
    
    # Set delay for the drawing
    def set_delay(self, delay):
        self.delay = int(delay)


"""
Main method

Executing the entire application
"""


def main():
    # New instance of Gui
    app = Gui()
    
    # Start the mainloop
    app.mainloop()


"""
Calling main

Executing
"""

main()