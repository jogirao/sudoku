# Sudoku Project Structure

This document describes the organization of the Sudoku application codebase.

## Directory Structure

```
sudoku/
├── src/                        # Source code
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Main application entry point
│   ├── screens/               # Screen widgets (different app screens)
│   │   ├── __init__.py
│   │   ├── menu.py           # Main menu screen
│   │   ├── puzzle.py         # Puzzle playing screen
│   │   └── library.py        # Puzzle library/gallery screen
│   ├── widgets/               # Custom widgets (reusable UI components)
│   │   ├── __init__.py
│   │   ├── sudoku_grid.py   # Grid-related widgets (Cell, SudokuBox, SudokuGrid)
│   │   └── numpad.py        # Number pad widgets
│   ├── utils/                 # Utility functions and helpers
│   │   ├── __init__.py
│   │   └── solver.py         # Sudoku solving algorithms (TBD)
│   └── assets/                # UI definition files (KV files)
│       ├── menu.kv           # Menu screen layout
│       ├── puzzle.kv         # Puzzle screen layout
│       └── library.kv        # Library screen layout
├── data/                      # Data files
│   ├── puzzles/              # Sudoku puzzle data
│   │   ├── Test_Sudoku.txt  # Test puzzle
│   │   ├── Puzzles.txt      # Puzzle collection
│   │   └── Solutions.txt    # Puzzle solutions
│   └── images/               # Image assets
│       └── sudoku.png       # Example sudoku image
├── tests/                     # Test files
│   ├── __init__.py
│   ├── test_sudoku.py       # Unit tests for sudoku logic
│   ├── test_integration.py  # Integration tests
│   └── manual/               # Manual/visual tests
│       ├── test_library.py
│       ├── test_library_manual.py
│       └── test_refactor.py
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Running the Application

### Option 1: Using the entry point wrapper
```bash
python Main.py
```

### Option 2: Using the module
```bash
python -m src.main
```

## Code Organization

### Screens (`src/screens/`)
Contains the main screen widgets that represent different views in the application:
- **menu.py**: Main menu with options to play, use camera, or browse library
- **puzzle.py**: Interactive Sudoku grid with number pad for playing
- **library.py**: Gallery view of available Sudoku puzzles

### Widgets (`src/widgets/`)
Reusable UI components:
- **sudoku_grid.py**: Grid components (Cell, SudokuBox, SudokuGrid, etc.)
- **numpad.py**: Number input pad components

### Assets (`src/assets/`)
Kivy language files that define the UI layout and styling for each screen.

### Data (`data/`)
Application data files:
- **puzzles/**: Text files containing Sudoku puzzles and solutions
- **images/**: Image assets used in the application

## Development

### Running Tests
```bash
# Run all unit tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_sudoku.py

# Run integration tests
python -m pytest tests/test_integration.py
```

### Adding New Puzzles
1. Add puzzle images to `data/images/`
2. They will automatically appear in the library screen

### Code Style
- Follow PEP 8 guidelines
- Use docstrings for classes and functions
- Keep imports organized (stdlib, third-party, local)

### TODO
1. Initialise camera and process sudoku
2. Populate library with more examples and separate by difficulty
3. Improve navigation between sudoku app pages
4. Finish UI Layout of menu screen (links, remaining buttons)