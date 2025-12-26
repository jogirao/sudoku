"""Puzzle screen for playing Sudoku"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from src.widgets.sudoku_grid import Cell


class MainWidget(Screen):
    """Main puzzle screen"""
    pass


class MainBoxLayout(BoxLayout):
    """Main container for the puzzle screen with game logic"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_cell = None

    def on_cell_click(self, widget, value):
        """Handle cell selection"""
        if widget.state == "down":
            self.selected_cell = widget
        else:
            self.selected_cell = None

    def on_number_click(self, widget):
        """Handle number button click"""
        if self.selected_cell:
            if self.selected_cell.color != [0, 0, 0, 1]:
                self.selected_cell.text = widget.text

    def on_delete_click(self, widget):
        """Handle delete button click"""
        if self.selected_cell:
            if self.selected_cell.color != [0, 0, 0, 1]:
                self.selected_cell.text = ""

    def _find_all_cells(self, widget):
        """Recursively find all Cell widgets in the widget tree"""
        cells = []
        if isinstance(widget, Cell):
            cells.append(widget)
        if hasattr(widget, 'children'):
            for child in widget.children:
                cells.extend(self._find_all_cells(child))
        return cells

    def on_clear_click(self, widget):
        """Clear all user-editable cells in the Sudoku grid"""
        for cell in self._find_all_cells(self):
            if cell.color != [0, 0, 0, 1]:  # Only clear non-fixed cells
                cell.text = ""

    def on_hint_selected(self, option):
        """Handle selection from the lightbulb dropdown"""
        # Simple handler: log the selected option for now; implement actions later
        print(f"Hint selected: {option}")
        if option == "Show Hints":
            print("Show Hints selected (not implemented).")
        elif option == "Reveal Cell":
            print("Reveal Cell selected (not implemented).")
        elif option == "Auto Solve Step":
            print("Auto Solve Step selected (not implemented).")
        elif option == "Toggle Notes":
            print("Toggle Notes selected (not implemented).")
