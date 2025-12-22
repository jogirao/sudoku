#!/usr/bin/env python3
"""Quick test to verify the refactored on_clear_click works"""
import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from Main import MainBoxLayout, Cell, SudokuGrid, SudokuBox


def test_find_all_cells():
    """Test that _find_all_cells finds all cells"""
    main_layout = MainBoxLayout()
    grid = SudokuGrid()

    cells = main_layout._find_all_cells(grid)

    print(f"✓ Found {len(cells)} cells in SudokuGrid")
    assert len(cells) == 81, f"Expected 81 cells, found {len(cells)}"

    for cell in cells:
        assert isinstance(cell, Cell), "All found widgets should be Cell instances"

    print("✓ All found widgets are Cell instances")


def test_clear_functionality():
    """Test that clear only clears user-editable cells"""
    main_layout = MainBoxLayout()
    grid = SudokuGrid()

    # Add grid to the layout (simulating the widget tree)
    from kivy.uix.boxlayout import BoxLayout
    container = BoxLayout()
    container.add_widget(grid)
    main_layout.add_widget(container)

    # Get all cells
    all_cells = main_layout._find_all_cells(main_layout)

    # Find fixed cells (black color) and user cells
    fixed_cells = [c for c in all_cells if c.color == [0, 0, 0, 1]]
    user_cells = [c for c in all_cells if c.color != [0, 0, 0, 1]]

    print(f"✓ Found {len(fixed_cells)} fixed cells")
    print(f"✓ Found {len(user_cells)} user-editable cells")

    # Set text on some user cells
    for i, cell in enumerate(user_cells[:5]):
        cell.text = str(i + 1)

    # Store original text of fixed cells
    fixed_texts = {id(cell): cell.text for cell in fixed_cells}

    # Clear all
    main_layout.on_clear_click(None)

    # Verify user cells are cleared
    for cell in user_cells:
        assert cell.text == "", f"User cell should be cleared but has text: {cell.text}"

    print("✓ All user cells cleared")

    # Verify fixed cells are unchanged
    for cell in fixed_cells:
        assert cell.text == fixed_texts[id(cell)], "Fixed cell text should not change"

    print("✓ Fixed cells unchanged")


if __name__ == "__main__":
    print("\n=== Testing Refactored on_clear_click ===\n")
    test_find_all_cells()
    print()
    test_clear_functionality()
    print("\n✓ All tests passed!")
