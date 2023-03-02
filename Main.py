import Sudoku as s
import SudokuSolver as ss
from sqlitedict import SqliteDict as sd


puzzle = s.Sudoku()
puzzle.draw_sudoku()

solver = ss.SudokuSolver(puzzle)
puzzle.state = solver.solve()

puzzle.check_solution()


