import pytest
from unittest.mock import MagicMock, Mock
from kivy.uix.togglebutton import ToggleButton
from Main import MainBoxLayout, NumPadButton, Cell


class TestSudokuNumberPopulation:
    """Test suite for validating that numpad buttons populate cells correctly"""

    def test_on_cell_click_selects_cell(self):
        """Test that clicking a cell selects it"""
        main_layout = MainBoxLayout()
        # Create a mock cell to avoid .kv binding issues
        cell = Mock()
        cell.color = [0, 0, 0.8, 1]  # User-editable cell (not black)
        cell.state = "down"

        # Simulate cell click
        main_layout.on_cell_click(cell, "down")

        assert main_layout.selected_cell == cell, "Cell should be selected when clicked"

    def test_on_cell_click_deselects_cell(self):
        """Test that clicking a selected cell deselects it"""
        main_layout = MainBoxLayout()
        cell = Mock()
        cell.color = [0, 0, 0.8, 1]
        cell.state = "normal"

        # First select the cell
        cell.state = "down"
        main_layout.on_cell_click(cell, "down")
        assert main_layout.selected_cell == cell

        # Then deselect it
        cell.state = "normal"
        main_layout.on_cell_click(cell, "normal")

        assert main_layout.selected_cell is None, "Cell should be deselected when clicked again"

    def test_on_number_click_populates_selected_cell(self):
        """Test that clicking a numpad button populates the selected cell"""
        main_layout = MainBoxLayout()
        cell = Mock()
        cell.color = [0, 0, 0.8, 1]  # User-editable cell (not black)
        cell.text = ""

        # Select the cell
        cell.state = "down"
        main_layout.on_cell_click(cell, "down")

        # Create a mock numpad button
        numpad_button = Mock()
        numpad_button.text = "5"

        # Click the numpad button
        main_layout.on_number_click(numpad_button)

        assert cell.text == "5", f"Cell text should be '5' but got '{cell.text}'"

    def test_on_number_click_does_not_populate_fixed_cell(self):
        """Test that numpad buttons don't modify fixed (black) cells"""
        main_layout = MainBoxLayout()
        cell = Mock()
        cell.color = [0, 0, 0, 1]  # Fixed cell (black)
        cell.text = "3"

        # Select the cell
        cell.state = "down"
        main_layout.on_cell_click(cell, "down")

        # Create a mock numpad button
        numpad_button = Mock()
        numpad_button.text = "7"

        # Click the numpad button
        main_layout.on_number_click(numpad_button)

        assert cell.text == "3", "Fixed cell text should not change"

    def test_on_number_click_without_selected_cell(self):
        """Test that clicking numpad without selecting a cell does nothing"""
        main_layout = MainBoxLayout()

        # Create a mock numpad button
        numpad_button = Mock()
        numpad_button.text = "5"

        # Click the numpad button without selecting a cell
        main_layout.on_number_click(numpad_button)

        # Should not raise an error
        assert main_layout.selected_cell is None

    def test_on_delete_click_clears_selected_cell(self):
        """Test that clicking delete clears the selected cell"""
        main_layout = MainBoxLayout()
        cell = Mock()
        cell.color = [0, 0, 0.8, 1]
        cell.text = "7"

        # Select the cell
        cell.state = "down"
        main_layout.on_cell_click(cell, "down")

        # Create a delete button
        delete_button = Mock()

        # Click delete
        main_layout.on_delete_click(delete_button)

        assert cell.text == "", "Cell text should be cleared"

    def test_multiple_number_clicks_on_same_cell(self):
        """Test that multiple number clicks update the same cell"""
        main_layout = MainBoxLayout()
        cell = Mock()
        cell.color = [0, 0, 0.8, 1]
        cell.text = ""

        # Select the cell
        cell.state = "down"
        main_layout.on_cell_click(cell, "down")

        # Click different numbers
        for number in ["1", "2", "3"]:
            numpad_button = Mock()
            numpad_button.text = number
            main_layout.on_number_click(numpad_button)
            assert cell.text == number, f"Cell text should be '{number}'"
