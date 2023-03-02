# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 20:14:42 2020

@author: joaom
"""
import sys
from copy import deepcopy
from random import randint


class SudokuSolver:
    
    def __init__(self, sdk):
        # Initialize solver
        self.sudoku = sdk
        self.possibleNumbersForCell = {}
        self.rowSets = {}
        self.cellsByRow = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        self.colSets = {}
        self.cellsByCol = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        self.sqrSets = {}
        self.cellsBySqr = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        self.emptyCells = []
        self.States = []
        self.order = int(len(self.sudoku.state)**0.5)
    
    def check_column(self, nbs, cell):
        # Checks if any number in the set is unique in its column
        for i in range(len(self.sudoku.state)):
            if len(nbs) > 0:
                if (i, cell[1]) != cell:
                    try:
                        nums = deepcopy(self.possibleNumbersForCell[i, (cell[1])])
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
                        nums = deepcopy(self.possibleNumbersForCell[(cell[0], i)])
                    except:
                        nums = set()
                    nbs -= nums
            else:
                break
        return nbs
    
    def check_box(self, nbs, cell):
        # Checks if any number in the set is unique in the box that contains it
        side_length = int(len(self.sudoku.state)**0.5)
        R = int(cell[0] / side_length) * side_length
        C = int(cell[1] / side_length) * side_length
        for r in range(side_length):
            row = R+r
            for c in range(side_length):
                col = C+c
                if len(nbs) > 0:
                    if (row,col) != cell:
                        try:
                            nums = deepcopy(self.possibleNumbersForCell[(row, col)])
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
        
    def fillCell(self, c, newEmptyCells):
        # Only one number meets criteria
        # Fill cell
        self.sudoku.state[c] = self.possibleNumbersForCell[c].pop()
        del self.possibleNumbersForCell[c]
        # Update row/column/square info
        self.rowSets[c[0]].add(self.sudoku.state[c])
        self.colSets[c[1]].add(self.sudoku.state[c])
        self.sqrSets[(c[1]//self.order)+(self.order*(c[0]//self.order))].add(self.sudoku.state[c])
        # Remove cell from list of empty cells
        newEmptyCells.remove(c)
        self.cellsByRow[c[0]].remove(c)
        self.cellsByCol[c[1]].remove(c)
        self.cellsBySqr[(c[1]//self.order)+(self.order*(c[0]//self.order))].remove(c)
        
    def getCellInfo(self):
        # Get information about the sudoku cells' states
        l = len(self.sudoku.state)
        numList = set(range(1, l+1))
        # Fill list for each cell
        for r in range(l):
            for c in range(l):
                if self.sudoku.state[r, c] == 0:
                    # Update lists of cells by row/column/square
                    self.cellsByRow[r].append((r, c))
                    self.cellsByCol[c].append((r, c))
                    self.cellsBySqr[(c//self.order)+(self.order*(r//self.order))].append((r, c))
                    # Get list of possible numbers for the cell
                    self.possibleNumbersForCell[r, c] = numList - self.rowSets[r] - self.colSets[c] - \
                        self.sqrSets[(c // self.order) + (self.order * (r // self.order))]
                    # Update set of empty cells
                    self.emptyCells.append((r, c))
                    
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
        
    def get_preemptive_sets(self):
        # Find the preemptive sets in the sudoku puzzle
        for size in range(self.order+1, 1, -1):
            for row in range(9):
                self.preemptive_set(size, self.cellsByRow[row])
            for col in range(9):
                self.preemptive_set(size, self.cellsByCol[col])
            for sqr in range(9):
                self.preemptive_set(size, self.cellsBySqr[sqr])
                
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
                nums, ps_flg = self.join_sets(nums, self.possibleNumbersForCell[cell], size)
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
            for cell in self.possibleNumbersForCell:
                if len(self.possibleNumbersForCell[cell]) == lgt:
                    found = 1
                    break
        Set = list(self.possibleNumbersForCell[cell])
        num = Set[randint(0, len(Set)-1)]
        return cell, num
    
    def randomGuess(self, emptyCells):
        # Choose random number to proceed with sudoku solution
        cell, num = self.randomChoice()
        # Save current state
        State = [deepcopy(self.sudoku), deepcopy(self.possibleNumbersForCell), deepcopy(self.rowSets),
                 deepcopy(self.cellsByRow), deepcopy(self.colSets), deepcopy(self.cellsByCol),
                 deepcopy(self.sqrSets), deepcopy(self.cellsBySqr), deepcopy(self.emptyCells),
                 cell, num]
        # Update state list
        self.States.append(State)
        self.possibleNumbersForCell[cell] = {num}
        self.fillCell(cell, emptyCells)
    
    def reduceList(self, c, lastClue, looped):
        # More than one possibility found, reduce list of possible numbers
        newList = self.possibleNumbersForCell[c] - self.rowSets[c[0]] - self.colSets[c[1]] - \
                  self.sqrSets[(c[1] // self.order) + (self.order * (c[0] // self.order))]
        if newList != self.possibleNumbersForCell[c]:
            # Update last cell that got closer to a solution
            lastClue = c
            self.possibleNumbersForCell[c] = newList
            looped = 0
        else:
            # Deploy additional techniques to reduce list of possible numbers
            newList = self.check_for_unique_number(deepcopy(self.possibleNumbersForCell[c]), c)
            if newList != self.possibleNumbersForCell[c]:
                # Update last cell that got closer to a solution
                lastClue = c
                self.possibleNumbersForCell[c] = newList
                looped = 0
        return lastClue, looped
    
    def revertGuess(self):
        # Revert to previous state due to incorrect choice
        State = self.States.pop(-1)
        if len(State[1][State[9]]) == 1:  # Check if cell has no available numbers
            # Impossible state, return to previous choice
            State = self.States.pop(-1)
        # Update state
        self.sudoku = State[0]
        self.possibleNumbersForCell = State[1]
        self.rowSets = State[2]
        self.cellsByRow = State[3]
        self.colSets = State[4]
        self.cellsByCol = State[5]
        self.sqrSets = State[6]
        self.cellsBySqr = State[7]
        self.emptyCells = State[8]
        # Remove chosen number from list of possibilities
        self.possibleNumbersForCell[State[9]].remove(State[10])
        
    def solve(self):
        # Solve sudoku puzzle
        # Initialize auxiliary informative variables
        self.getSets()
        self.getCellInfo()
        clue=(-1,-1)
        # While sudoku isn't solved
        cnt=0
        looped = 0
        while len(self.emptyCells) != 0:
            # New loop
            newEmptyCells = deepcopy(self.emptyCells)
            cnt += 1

            if cnt == 500:
                print("Counter full!")
                print(self.possibleNumbersForCell)
                break
            reverted = 0
            # For each empty cell
            for cell in self.emptyCells:
                # Check list of possible numbers
                try:
                    self.possibleNumbersForCell[cell]
                except:
                    # Impossible state, return to previous set
                    self.revertGuess()
                    reverted = 1
                    break
                if len(self.possibleNumbersForCell[cell]) == 0:
                    # Impossible state, return to previous set
                    self.revertGuess()
                    clue, looped = self.reduceList(cell, clue, looped)
                    reverted = 1
                    break
                elif len(self.possibleNumbersForCell[cell]) == 1:
                    self.fillCell(cell, newEmptyCells)
                else:
                    clue, looped = self.reduceList(cell, clue, looped)
                    # Recheck list of possible numbers
                    try:
                        self.possibleNumbersForCell[cell]
                    except:
                        # Impossible state, return to previous set
                        self.revertGuess()
                        clue, looped = self.reduceList(cell, clue, looped)
                        reverted = 1
                        break
                    if len(self.possibleNumbersForCell[cell]) == 0:
                        # Impossible state, return to previous set
                        self.revertGuess()
                        reverted = 1
                        break
                    elif len(self.possibleNumbersForCell[cell]) == 1:
                        self.fillCell(cell, newEmptyCells)
                    elif looped == 1 and (cell == clue or clue not in self.emptyCells):
                        # Resort to preemptive set search
                        prevCellNbs = deepcopy(self.possibleNumbersForCell)
                        self.get_preemptive_sets()
                        if prevCellNbs == self.possibleNumbersForCell:
                            # Resort to random guessing
                            self.randomGuess(newEmptyCells)
                            break
                        else:
                            looped = 0
                # print(self.sudoku.__str__())
            if reverted == 0:
                self.emptyCells = newEmptyCells
            looped = 1
        return self.sudoku.state

    def updateCells(self, preemptive_set, cells, group):
        # Remove numbers in preemptive set from the remaining cells
        out = []
        for cell in group:
            if cell not in cells:
                # Cell does not belong to preemptive set
                self.possibleNumbersForCell[cell] -= preemptive_set
                out.append(cell)
        return out
