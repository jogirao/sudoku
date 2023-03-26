# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 22:44:58 2020

@author: joaom
"""
import numpy as np
import SudokuSolver as Ss
import SudokuGUI
from sqlitedict import SqliteDict
from tkinter import Tk
import os.path


class Sudoku:
    
    def __init__(self, puzzle_number=1, user_name="User"):
        self.user = self.login_user(user_name)
        self.game_over = False
        self.sudoku_id = puzzle_number
        # Chosen sudoku's state
        self.start_state = np.array(self.get_from_db(user_name + ".sqlite", "puzzles", puzzle_number))
        self.state = np.copy(self.start_state)
        # Chosen sudoku's solution
        self.solution = np.array(self.get_from_db(user_name + ".sqlite", "solutions", puzzle_number))
        # self.run_ui()
            
    def __str__(self, solved=False):
        # String representation of the sudoku state
        if solved:
            sdk = self.solution
        else:
            sdk = self.state
        length, size = len(sdk), int(len(sdk)**0.5)
        string = ''
        # Horizontal separator
        line = ''
        for i in range(length * 3 - size + 1):
            line += '-'
        line += '\n'
        string += line
        # Fill each line
        for r in range(length):
            string += '|'
            for c in range(length):
                if sdk[r, c] == 0:
                    string += ' '
                else:
                    string += str(sdk[r, c])
                if (c + 1) % size == 0:
                    string += '|'
                else:
                    string += '  '
            string += '\n'
            if (r + 1) % size == 0:
                string += line
        return string

    def change_sudoku(self, num: int) -> None:
        # Choose another sudoku
        # Chosen sudoku
        self.sudoku_id = num
        # Chosen sudoku's state
        self.state = np.array(self.get_from_db(self.user + ".sqlite", "puzzles", self.sudoku_id))
        # Chosen sudoku's solution
        self.solution = np.array(self.get_from_db(self.user + ".sqlite", "solutions", self.sudoku_id))
        
    def check_solution(self) -> bool:
        # Check solution's correctness
        if np.all(self.state == self.solution):
            return True
        return False

    def compute_solution(self) -> int:
        # Computes solution to given sudoku
        solver = Ss.SudokuSolver(self)
        solution = solver.solve()
        if len(solution) == 0:
            return -1
        return self.save_to_db(self.user + ".sqlite", "solutions", solution)

    def create_new_user(self, user_name: str) -> None:
        # Add new user to DB
        db_name = user_name + ".sqlite"
        self.import_default_files(db_name)

    def draw_sudoku(self, solved=False) -> None:
        # Prints a legible form of sudoku to console
        print(Sudoku.__str__(self, solved=solved))

    @staticmethod
    def get_from_db(db_name: str, table_name: str, sudoku_number: int) -> tuple:
        # Retrieve specified data from selected DB
        with SqliteDict(db_name, tablename=table_name, autocommit=True) as db:
            return db[table_name].get(sudoku_number, None)

    @staticmethod
    def import_data(db_name: str, file_name: str, table_name: str) -> None:
        # Imports data from file to SqliteDict DB
        temp_dict = dict()
        with open(file_name, "r") as f:
            for line in f:
                args = line.split(": ")
                temp_dict.update({eval(args[0]): eval(args[1])})
        with SqliteDict(db_name, tablename=table_name, autocommit=True) as db:
            db[table_name] = temp_dict

    def import_default_files(self, db: str) -> None:
        # Imports the base puzzles and solutions for the creation of a new user
        self.import_data(db, "puzzles.txt", "puzzles")
        self.import_data(db, "solutions.txt", "solutions")

    def login_user(self, user_name: str) -> str:
        # Initialize user account with files from DB
        path = "./Users.txt"
        if os.path.isfile(path):
            with open("Users.txt", "r") as f:
                for line in f:
                    if line == user_name:
                        return user_name    # User exists
        self.create_new_user(user_name)
        with open("Users.txt", "a") as f:
            f.write(user_name)
        return user_name

    def new_puzzle(self, board: np.array) -> None:
        # Get new puzzle
        self.start_state = board
        self.state = np.copy(self.start_state)
        solved_flg = self.compute_solution()
        if solved_flg == -1:
            print("WARNING: Could not compute solution to the puzzle! \n\t\tPlease check the board's validity.")
            self.start_state = np.array(self.get_from_db(self.user + ".sqlite", "puzzles", self.sudoku_id))
            self.state = np.copy(self.start_state)
        else:
            puzzle_number = self.save_to_db(self.user + ".sqlite", "puzzles", board)
            self.reset_sudoku()
            self.sudoku_id = puzzle_number

    def reset_sudoku(self) -> None:
        # Reset game state
        self.state = np.copy(self.start_state)
        self.game_over = False

    def run_ui(self):
        # Start the Sudoku UI
        root = Tk()
        SudokuGUI.SudokuUI(root, self)
        root.mainloop()

    @staticmethod
    def save_to_db(db_name: str, table_name: str, sudoku: tuple) -> int:
        # Save given sudoku state to selected DB
        with SqliteDict(db_name, tablename=table_name, autocommit=True) as db:
            temp_dict = db[table_name]
            new_id = len(db[table_name]) + 1
            temp_dict.update({new_id: tuple(map(tuple, sudoku))})
            db[table_name] = temp_dict
        return new_id
