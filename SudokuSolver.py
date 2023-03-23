# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 20:14:42 2020

@author: joaom
"""
from random import randint


class SudokuSolver:
    
    def __init__(self, puzzle):
        # Initialize solver
        self.sudoku = puzzle
        self.cell_number_options = {}
        self.empty_cells = []
        self.States = []
        self.side_length = len(self.sudoku.state)
        self.box_length = int(self.side_length ** 0.5)
        self.cells_without_update = 0
        self.looped_flg = False
        self.reverted_flg = False
        self.start_cell_options()
    
    def check_column(self, cell: tuple) -> set:
        # Checks if any option in cell is unique in its column
        number_options = self.cell_number_options[cell].copy()
        for row in range(self.side_length):
            if row != cell[0]:
                number_options -= self.cell_number_options[row, cell[1]]
        if not number_options:
            # Empty set, return original set
            return self.cell_number_options[cell].copy()
        return number_options
    
    def check_row(self, cell: tuple) -> set:
        # Checks if any option in cell is unique in its row
        number_options = self.cell_number_options[cell].copy()
        for column in range(self.side_length):
            if column != cell[1]:
                number_options -= self.cell_number_options[cell[0], column]
        if not number_options:
            # Empty set, return original set
            return self.cell_number_options[cell].copy()
        return number_options
    
    def check_box(self, cell: tuple) -> set:
        # Checks if any option in cell is unique in its box
        number_options = self.cell_number_options[cell].copy()
        start_row = (cell[0] // self.box_length) * self.box_length
        start_column = (cell[1] // self.box_length) * self.box_length
        for row in range(start_row, start_row + self.box_length):
            for column in range(start_column, start_column + self.box_length):
                if (row, column) != cell:
                    number_options -= self.cell_number_options[row, column]
        if not number_options:
            # Empty set, return original set
            return self.cell_number_options[cell].copy()
        return number_options
    
    def check_for_unique_number(self, cell: tuple) -> set:
        # Check if there is a number in the given cell that can only exist there.
        # Check row for unique number
        new_cell_options = self.check_row(cell)
        if len(new_cell_options) == 1:
            return new_cell_options
        # Check column for unique number
        new_cell_options = self.check_column(cell)
        if len(new_cell_options) == 1:
            return new_cell_options
        # Check box for unique number
        new_cell_options = self.check_box(cell)
        if len(new_cell_options) == 1:
            return new_cell_options
        return self.cell_number_options[cell].copy()

    def check_for_preemptive_sets(self, cell_options: dict) -> None:
        # Check for preemptive sets if worth it
        if len(cell_options) > 2:
            new_cell_options = self.check_preemptive_sets(cell_options, self.box_length * 2)
            for cell in new_cell_options:
                self.cell_number_options[cell] = new_cell_options[cell]

    def check_preemptive_sets(self, set_dict: dict, max_size: int) -> dict:
        # Check for preemptive sets in a set dictionary
        sorted_dict = dict(sorted(set_dict.items(), key=lambda item: len(item[1])))
        for set_size in range(2, max_size + 1):
            cells, union = self.join_sets([], set(), sorted_dict, set_size, set_size)
            if cells:
                excluded_cells = {}
                for cell in set_dict.keys():
                    if cell not in cells:
                        sorted_dict.update({cell: set_dict[cell].difference(union)})
                    else:
                        excluded_cells.update({cell: set_dict[cell]})
                        sorted_dict.pop(cell)
                if sorted_dict:
                    sorted_dict = self.check_preemptive_sets(sorted_dict, max_size)
                    sorted_dict.update(excluded_cells)
                    return sorted_dict
                else:
                    self.looped_flg = False
                    return excluded_cells
        return set_dict
        
    def examine_cell(self, cell: tuple):
        # Examine cell and act based on cell state
        if not self.cell_number_options[cell]:
            # Empty cell with no possible move, reverse guess
            self.revert_guess()
            self.reduce_options(cell)
            self.reverted_flg = True
            self.looped_flg = False
        elif len(self.cell_number_options[cell]) == 1:
            # Only one option left
            self.fill_cell(cell)
        else:
            # Multiple options left
            if self.cells_without_update == len(self.empty_cells):
                self.looped_flg = True
            self.reduce_options(cell)
        
    def fill_cell(self, cell: tuple) -> None:
        # Fill cell
        self.sudoku.state[cell] = self.cell_number_options[cell].pop()
        # Remove cell from list of empty cells
        self.empty_cells.remove(cell)

    def get_cell_number_options(self, current_options: set, row: int, column: int) -> set:
        # Get the list of numbers that can fill the cell
        row_numbers = self.get_numbers_in_row(row)
        column_numbers = self.get_numbers_in_column(column)
        box_numbers = self.get_numbers_in_box(row, column)
        return current_options - row_numbers - column_numbers - box_numbers

    def get_numbers_in_box(self, row: int, column: int) -> set:
        # Get the numbers of the filled cells in the current box
        start_row, start_column = row // self.box_length * self.box_length, column // self.box_length * self.box_length
        number_set = set()
        for row in range(start_row, start_row + self.box_length):
            for column in range(start_column, start_column + self.box_length):
                if self.sudoku.state[row, column] != 0:
                    number_set.add(self.sudoku.state[row, column])
        return number_set

    def get_numbers_in_column(self, column: int) -> set:
        # Get the numbers of the filled cells in the current box
        number_set = set()
        for row in range(self.side_length):
            if self.sudoku.state[row, column] != 0:
                number_set.add(self.sudoku.state[row, column])
        return number_set

    def get_numbers_in_row(self, row: int) -> set:
        # Get the numbers of the filled cells in the current box
        number_set = set()
        for column in range(self.side_length):
            if self.sudoku.state[row, column] != 0:
                number_set.add(self.sudoku.state[row, column])
        return number_set

    def get_preemptive_sets(self):
        # Find the preemptive sets in the sudoku puzzle
        previous_cell_options = self.cell_number_options.copy()
        for number in range(self.side_length):
            # Check row
            cell_options = {}
            for column in range(self.side_length):
                if self.sudoku.state[number, column] == 0:
                    cell_options.update({(number, column): self.cell_number_options[number, column]})
            self.check_for_preemptive_sets(cell_options)
            # Check column
            cell_options = {}
            for row in range(self.side_length):
                if self.sudoku.state[row, number] == 0:
                    cell_options.update({(row, number): self.cell_number_options[row, number]})
            self.check_for_preemptive_sets(cell_options)
            # Check box
            cell_options = {}
            for num in range(self.side_length):
                row = (number // self.box_length) * self.box_length + num // self.box_length
                column = (number % self.box_length) * self.box_length + num % self.box_length
                if self.sudoku.state[row, column] == 0:
                    cell_options.update({(row, column): self.cell_number_options[row, column]})
            self.check_for_preemptive_sets(cell_options)
        if previous_cell_options != self.cell_number_options:
            self.cells_without_update = 0
            self.get_preemptive_sets()

    def join_sets(self, group: list, number_set: set, set_dict: dict, set_size: int, groups_left: int):
        for key, value in set_dict.items():
            union = number_set.union(value)
            if len(union) <= set_size and groups_left > 1:
                new_set_dict = dict(list(set_dict.items())[list(set_dict.items()).index((key, value)) + 1:])
                return self.join_sets(group + [key], union, new_set_dict, set_size, groups_left - 1)
            elif len(union) == set_size and groups_left == 1:
                return group + [key], union
        return [], {}

    @staticmethod
    def random_choice(options: set) -> int:
        # Choose a number given the list of all possible choices
        options = list(options)
        return options[randint(0, len(options) - 1)]
    
    def random_guess(self) -> None:
        # Make a random guess to proceed with sudoku solving
        sorted_cells_by_options = dict(sorted(self.cell_number_options.items(), key=lambda item: len(item[1])))
        for cell in sorted_cells_by_options:
            if cell in self.empty_cells:
                choice = self.random_choice(self.cell_number_options[cell])
                self.cell_number_options[cell].remove(choice)
                # Save current state
                self.States.append([self.sudoku.state.copy(), self.cell_number_options.copy(), self.empty_cells.copy()])
                # Update information on guessed cell
                self.cells_without_update = 0
                self.sudoku.state[cell] = choice
                self.cell_number_options[cell] = set()
                self.empty_cells.remove(cell)
                self.looped_flg = False
                break
    
    def reduce_options(self, cell: tuple) -> None:
        # More than one option for cell, reduce list of possible numbers
        number_options = self.get_cell_number_options(self.cell_number_options[cell], *cell)
        if number_options == self.cell_number_options[cell]:
            # Deploy additional techniques to reduce list of possible numbers
            number_options = self.check_for_unique_number(cell)
        if number_options != self.cell_number_options[cell]:
            # Update cell options
            self.cells_without_update = 0
            self.cell_number_options[cell] = number_options.copy()
            if len(number_options) == 1:
                self.fill_cell(cell)
            self.looped_flg = False
    
    def revert_guess(self):
        # Revert to previous state due to incorrect choice
        state = self.States.pop(-1)
        # Update state
        self.sudoku.state = state[0]
        self.cell_number_options = state[1]
        self.empty_cells = state[2]
        
    def solve(self):
        # Solve sudoku puzzle
        counter = 0
        while len(self.empty_cells) != 0:
            # New loop
            counter += 1
            if counter == 5000:
                # print("Counter full!\n", self.cell_number_options)
                return []
            # For each empty cell
            for cell in self.empty_cells:
                # Check list of possible numbers
                self.cells_without_update += 1
                self.examine_cell(cell)
                if self.reverted_flg:
                    self.reverted_flg = False
                    break
                if self.looped_flg:
                    # Resort to preemptive set search
                    previous_cell_options = self.cell_number_options.copy()
                    self.get_preemptive_sets()
                    if previous_cell_options == self.cell_number_options:
                        # Resort to random guessing
                        self.random_guess()

        return self.sudoku.state

    def start_cell_options(self):
        # Get information about the sudoku cells' states
        numbers = set(range(1, self.side_length + 1))
        # Fill list for each cell
        for r in range(self.side_length):
            for c in range(self.side_length):
                if self.sudoku.state[r, c] == 0:
                    # Get list of possible numbers for the cell
                    self.cell_number_options[(r, c)] = self.get_cell_number_options(numbers, r, c)
                    # Update set of empty cells
                    self.empty_cells.append((r, c))
                else:
                    self.cell_number_options[(r, c)] = set()
