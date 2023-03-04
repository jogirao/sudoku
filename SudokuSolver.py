# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 20:14:42 2020

@author: joaom
"""
import sys
from copy import deepcopy
from random import randint


class SudokuSolver:
    
    def __init__(self, puzzle):
        # Initialize solver
        self.sudoku = puzzle
        self.cell_number_options = {}
        self.rowSets = {}
        self.cellsByRow = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        self.colSets = {}
        self.cellsByCol = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        self.sqrSets = {}
        self.cellsBySqr = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        self.empty_cells = []
        self.States = []
        self.order = int(len(self.sudoku.state)**0.5)
    
    def check_column(self, nbs, cell):
        # Checks if any number in the set is unique in its column
        for i in range(len(self.sudoku.state)):
            if len(nbs) > 0:
                if (i, cell[1]) != cell:
                    try:
                        nums = deepcopy(self.cell_number_options[i, (cell[1])])
                    except:
                        nums = set()
                    nbs -= nums
            else:
                break
        return nbs
    
    def check_row(self, nbs, cell):
        # Checks if any number in the set is unique in its row
        for i in range(len(self.sudoku.state)):
            if len(nbs) > 0:
                if (cell[0], i) != cell:
                    try:
                        nums = deepcopy(self.cell_number_options[(cell[0], i)])
                    except:
                        nums = set()
                    nbs -= nums
            else:
                break
        return nbs
    
    def check_box(self, nbs, cell):
        # Checks if any number in the set is unique in the box that contains it
        box_size = int(len(self.sudoku.state)**0.5)
        start_row, start_column = (cell[0] // box_size) * box_size, (cell[1] // box_size) * box_size
        for row in range(start_row, start_row + box_size):
            for column in range(start_column, start_column + box_size):
                if len(nbs) > 0:
                    if (row, column) != cell:
                        try:
                            nums = deepcopy(self.cell_number_options[(row, column)])
                        except:
                            nums = set()
                        nbs -= nums
                else:
                    break
        return nbs
    
    def check_for_unique_number(self, nums, cell):
        # Checks if there is any number in the given cell that can only exist there.
        # This is done via comparisons with the other possible numbers in the cells 
        # that belong to the same group (row, column or square) as the input cell.
        nbs = deepcopy(nums)
        # Check rows
        numbers_in_set = self.check_row(nbs, cell)
        if len(numbers_in_set) != 0:
            nbs = deepcopy(numbers_in_set)
        else:
            nbs = deepcopy(nums)
        if len(numbers_in_set) != 1:
            # Check columns
            numbers_in_set = self.check_column(nbs, cell)
            if len(numbers_in_set) != 0:
                nbs = deepcopy(numbers_in_set)
            else:
                nbs = deepcopy(nums)
            if len(numbers_in_set) != 1:
                # Check squares
                numbers_in_set = self.check_box(nbs, cell)
                if len(numbers_in_set) != 0:
                    nbs = deepcopy(numbers_in_set)
                else:
                    nbs = deepcopy(nums)
        return nbs
        
    def fillCell(self, c, new_empty_cells):
        # Only one number meets criteria
        # Fill cell
        self.sudoku.state[c] = self.cell_number_options[c].pop()
        del self.cell_number_options[c]
        # Update row/column/square info
        self.rowSets[c[0]].add(self.sudoku.state[c])
        self.colSets[c[1]].add(self.sudoku.state[c])
        self.sqrSets[(c[1]//self.order)+(self.order*(c[0]//self.order))].add(self.sudoku.state[c])
        # Remove cell from list of empty cells
        new_empty_cells.remove(c)
        self.cellsByRow[c[0]].remove(c)
        self.cellsByCol[c[1]].remove(c)
        self.cellsBySqr[(c[1]//self.order)+(self.order*(c[0]//self.order))].remove(c)
        
    def get_cell_number_options(self):
        # Get information about the sudoku cells' states
        side_length = len(self.sudoku.state)
        numbers = set(range(1, side_length + 1))
        # Fill list for each cell
        for r in range(side_length):
            for c in range(side_length):
                if self.sudoku.state[r, c] == 0:
                    # Get list of possible numbers for the cell
                    row_numbers = self.get_numbers_in_row(r)
                    column_numbers = self.get_numbers_in_column(c)
                    box_numbers = self.get_numbers_in_box(r, c, int(side_length ** 0.5))
                    self.cell_number_options[(r, c)] = numbers - row_numbers - column_numbers - box_numbers
                    # Update set of empty cells
                    self.empty_cells.append((r, c))
                else:
                    self.cell_number_options[(r, c)] = set()

    def get_numbers_in_box(self, row: int, column: int, box_length: int):
        # Get the numbers of the filled cells in the current box
        start_row, start_column = row // box_length * box_length, column // box_length * box_length
        number_set = set()
        for r in range(row, row + box_length):
            for c in range(column, column + box_length):
                if self.sudoku.state[r, c] != 0:
                    number_set.add(self.sudoku.state[r, c])
        return number_set

    def get_numbers_in_column(self, column: int):
        # Get the numbers of the filled cells in the current box
        number_set = set()
        for r in range(len(self.sudoku.state)):
            if self.sudoku.state[r, column] != 0:
                number_set.add(self.sudoku.state[r, column])
        return number_set

    def get_numbers_in_row(self, row: int):
        # Get the numbers of the filled cells in the current box
        number_set = set()
        for c in range(len(self.sudoku.state)):
            if self.sudoku.state[row, c] != 0:
                number_set.add(self.sudoku.state[row, c])
        return number_set

    def get_preemptive_sets(self):
        # Find the preemptive sets in the sudoku puzzle
        for size in range(self.order+1, 1, -1):
            for row in range(9):
                self.preemptive_set(size, self.cellsByRow[row])
            for col in range(9):
                self.preemptive_set(size, self.cellsByCol[col])
            for sqr in range(9):
                self.preemptive_set(size, self.cellsBySqr[sqr])

    def getSets(self):
        # Get the list of numbers in the rows, columns and squares of the puzzle
        l = len(self.sudoku.state)
        # Initialize auxiliary variables
        for i in range(l):
            self.rowSets[i] = set()
            self.colSets[i] = set()
            self.sqrSets[i] = set()
        # Populate sets from sudoku state
        for r in range(l):
            for c in range(l):
                # Fill lists for each non-empty cell
                if self.sudoku.state[r, c] != 0:
                    self.rowSets[r].add(self.sudoku.state[r, c])
                    self.colSets[c].add(self.sudoku.state[r, c])
                    self.sqrSets[(c//self.order)+(self.order*(r//self.order))].add(self.sudoku.state[r, c])

    def groupCombinations(self, cells, group, size, comb):
        # Get possible cell combinations
        if len(comb) == size:
            cells.append(comb)
        else:
            if len(group)+len(comb) >= size:
                comb1 = comb.copy()
                comb.append(group[0])
                self.groupCombinations(cells, group[1:], size, comb)
                if len(group)+len(comb1) > size:
                    self.groupCombinations(cells, group[1:], size, comb1)
        
    def join_sets(self, base, numbers_set, size):
        # Adds set to existing preemptive set 
        # flg: -2 -> Set too big to add
        #      -1 -> Union bigger than what's expected
        #       0 -> Union smaller than what's expected
        #       1 -> Preemptive set found
        flg = -2
        if len(numbers_set) <= size:
            flg += 1
            out = base.union(numbers_set)
            if len(out) <= size:
                flg += 1
        else:
            out = base
        return out, flg
                
    def preemptive_set(self, size, group):
        # Computes preemptive sets
        # Get all possible cell combinations
        combList = []
        self.groupCombinations(combList, group, size, [])
        # Check if combination is a preemptive_set
        for Set in combList:
            ps_flg = 0
            nums = set()
            for cell in Set:
                # join_sets
                nums, ps_flg = self.join_sets(nums, self.cell_number_options[cell], size)
                # Exit if there are too many numbers for the preemptive set
                if ps_flg < 0:
                    break
            if ps_flg == 0 and len(nums) == size:
                # Take numbers in preemptive set from other cells in the range
                newGroup = self.updateCells(nums, Set, group)
                # Search for preemptive sets in the remaining cells
                self.preemptive_set(size, newGroup)
                # Exit current search
                
                break
    
    def randomChoice(self):
        # Choose a number given the list of all possible choices
        found = 0
        lgt = 1
        while found == 0:
            lgt += 1
            for cell in self.cell_number_options:
                if len(self.cell_number_options[cell]) == lgt:
                    found = 1
                    break
        Set = list(self.cell_number_options[cell])
        num = Set[randint(0, len(Set)-1)]
        return cell, num
    
    def randomGuess(self, empty_cells):
        # Choose random number to proceed with sudoku solution
        cell, num = self.randomChoice()
        # Save current state
        State = [deepcopy(self.sudoku), deepcopy(self.cell_number_options), deepcopy(self.rowSets),
                 deepcopy(self.cellsByRow), deepcopy(self.colSets), deepcopy(self.cellsByCol),
                 deepcopy(self.sqrSets), deepcopy(self.cellsBySqr), deepcopy(self.empty_cells),
                 cell, num]
        # Update state list
        self.States.append(State)
        self.cell_number_options[cell] = {num}
        self.fillCell(cell, empty_cells)
    
    def reduceList(self, c, lastClue, looped):
        # More than one possibility found, reduce list of possible numbers
        newList = self.cell_number_options[c] - self.rowSets[c[0]] - self.colSets[c[1]] - \
                  self.sqrSets[(c[1] // self.order) + (self.order * (c[0] // self.order))]
        if newList != self.cell_number_options[c]:
            # Update last cell that got closer to a solution
            lastClue = c
            self.cell_number_options[c] = newList
            looped = False
        else:
            # Deploy additional techniques to reduce list of possible numbers
            newList = self.check_for_unique_number(deepcopy(self.cell_number_options[c]), c)
            if newList != self.cell_number_options[c]:
                # Update last cell that got closer to a solution
                lastClue = c
                self.cell_number_options[c] = newList
                looped = False
        return lastClue, looped
    
    def revertGuess(self):
        # Revert to previous state due to incorrect choice
        State = self.States.pop(-1)
        if len(State[1][State[9]]) == 1:  # Check if cell has no available numbers
            # Impossible state, return to previous choice
            State = self.States.pop(-1)
        # Update state
        self.sudoku = State[0]
        self.cell_number_options = State[1]
        self.rowSets = State[2]
        self.cellsByRow = State[3]
        self.colSets = State[4]
        self.cellsByCol = State[5]
        self.sqrSets = State[6]
        self.cellsBySqr = State[7]
        self.empty_cells = State[8]
        # Remove chosen number from list of possibilities
        self.cell_number_options[State[9]].remove(State[10])
        
    def solve(self):
        # Solve sudoku puzzle
        # Initialize auxiliary informative variables
        self.getSets()
        self.get_cell_number_options()
        clue = (-1, -1)
        # While sudoku isn't solved
        counter = 0
        looped = False
        while len(self.empty_cells) != 0:
            # New loop
            new_empty_cells = self.empty_cells.copy()
            counter += 1
            if counter == 500:
                print("Counter full!")
                print(self.cell_number_options)
                break
            reverted = False
            # For each empty cell
            for cell in self.empty_cells:
                # Check list of possible numbers
                if not self.cell_number_options[cell]:
                    # Impossible state, return to previous set
                    self.revertGuess()
                    reverted = True
                    clue, looped = self.reduceList(cell, clue, looped)
                    break
                elif len(self.cell_number_options[cell]) == 1:
                    self.fillCell(cell, new_empty_cells)
                else:
                    clue, looped = self.reduceList(cell, clue, looped)
                    # Recheck list of possible numbers
                    try:
                        self.cell_number_options[cell]
                    except:
                        # Impossible state, return to previous set
                        self.revertGuess()
                        clue, looped = self.reduceList(cell, clue, looped)
                        reverted = True
                        break
                    if len(self.cell_number_options[cell]) == 0:
                        # Impossible state, return to previous set
                        self.revertGuess()
                        reverted = True
                        break
                    elif len(self.cell_number_options[cell]) == 1:
                        self.fillCell(cell, new_empty_cells)
                    elif looped and (cell == clue or clue not in self.empty_cells):
                        # Resort to preemptive set search
                        prevCellNbs = deepcopy(self.cell_number_options)
                        self.get_preemptive_sets()
                        if prevCellNbs == self.cell_number_options:
                            # Resort to random guessing
                            self.randomGuess(new_empty_cells)
                            break
                        else:
                            looped = False
                # print(self.sudoku.__str__())
            if not reverted:
                self.empty_cells = new_empty_cells.copy()
            looped = True
        return self.sudoku.state

    def updateCells(self, preemptive_set, cells, group):
        # Remove numbers in preemptive set from the remaining cells
        out = []
        for cell in group:
            if cell not in cells:
                # Cell does not belong to preemptive set
                self.cell_number_options[cell] -= preemptive_set
                out.append(cell)
        return out
