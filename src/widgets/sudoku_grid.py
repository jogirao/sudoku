"""Sudoku grid widgets"""
import ast
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.togglebutton import ToggleButton


class Cell(ToggleButton):
    """Individual cell in the Sudoku grid"""
    pass


class SudokuBox(GridLayout):
    """3x3 box within the Sudoku grid"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(9):
            cell = Cell(size_hint=(.3, .3), color=(0, 0, 0.8, 1))
            self.add_widget(cell)


class SudokuGrid(GridLayout):
    """9x9 Sudoku grid composed of 9 SudokuBoxes"""

    def __init__(self, puzzle_file="data/puzzles/Test_Sudoku.txt", **kwargs):
        super().__init__(**kwargs)
        self.puzzle_file = puzzle_file

        # Create 9 boxes
        for i in range(9):
            box = SudokuBox()
            self.add_widget(box)

        # Load puzzle if file exists
        self.load_puzzle()

    def clear_puzzle(self):
        """Clear all cells in the puzzle"""
        for box in self.children:
            for cell in box.children:
                cell.text = ""
                cell.color = (0, 0, 0.8, 1)  # Reset to default color
                cell.state = "normal"  # Reset toggle state

    def load_puzzle(self):
        """Load puzzle from file"""
        try:
            # Clear existing puzzle first
            self.clear_puzzle()

            with open(self.puzzle_file, "r") as f:
                puzzle = str(ast.literal_eval(f.read()))

            i = 0
            for box in self.children:
                for cell in box.children:
                    if puzzle[i] != "0":
                        cell.text = str(puzzle[i])
                        cell.color = (0, 0, 0, 1)  # Black color for fixed cells
                    i += 1
        except FileNotFoundError:
            print(f"Warning: Puzzle file {self.puzzle_file} not found")
        except Exception as e:
            print(f"Error loading puzzle: {e}")


class SudokuGridLayout(RelativeLayout):
    """Container for the Sudoku grid"""
    pass


class UpperBoxLayout(BoxLayout):
    """Header box layout for the puzzle screen"""
    pass
