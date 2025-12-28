#!/usr/bin/env python3
"""
Sudoku Application - Entry Point

This is the main entry point for the Sudoku application.
For development, you can also run: python -m src.main
"""
# Re-export commonly used application classes so tests and scripts can import from `Main`
from src.main import main, SudokuApp
from src.screens.puzzle import MainBoxLayout
from src.widgets.sudoku_grid import Cell
from src.widgets.numpad import NumPadButton

__all__ = ["SudokuApp", "MainBoxLayout", "Cell", "NumPadButton", "main"]

if __name__ == '__main__':
    main()
