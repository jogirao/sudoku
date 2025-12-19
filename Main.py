from kivy.app import App
from kivy.graphics import RoundedRectangle
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from menu import MenuWidget
import ast

Builder.load_file("menu.kv")


class MainWidget(Screen):
    pass


class MainBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_cell = None

    def on_kv_post(self, base_widget):
        """Called after the kv lang file has been applied to this widget"""
        # Now that the .kv file has created all children, bind events

        # Find and bind Sudoku Grid cells
        for child in self.children:
            if isinstance(child, SudokuGridLayout):
                sudoku_grid = self._find_sudoku_grid(child)
                if sudoku_grid:
                    for box in sudoku_grid.children:
                        for cell in box.children:
                            cell.bind(state=self.on_cell_click)

            # Find and bind NumPad buttons
            elif isinstance(child, NumPadLayout):
                self._bind_numpad_events(child)

    def _find_sudoku_grid(self, widget):
        """Recursively find the SudokuGrid widget in the layout tree"""
        if isinstance(widget, SudokuGrid):
            return widget
        for child in widget.children:
            result = self._find_sudoku_grid(child)
            if result:
                return result
        return None

    def _bind_numpad_events(self, numpad):
        """Bind events to all NumPad buttons"""
        for child in numpad.children:
            # Check if it's the controls container
            if isinstance(child, BoxLayout) and child.orientation == 'horizontal':
                for button in child.children:
                    if button.text == "Delete":
                        button.bind(on_press=self.on_delete_click)
                    elif button.text == "Clear":
                        button.bind(on_press=self.on_clear_click)
            # Check if it's the numbers grid
            elif isinstance(child, GridLayout):
                for button in child.children:
                    if isinstance(button, NumPadButton):
                        button.bind(on_press=self.on_number_click)

    def on_cell_click(self, widget, value):
        if widget.state == "down":
            self.selected_cell = widget
        else:
            self.selected_cell = None

    def on_number_click(self, widget):
        if self.selected_cell:
            if self.selected_cell.color != [0, 0, 0, 1]:
                self.selected_cell.text = widget.text

    def on_delete_click(self, widget):
        if self.selected_cell:
            if self.selected_cell.color != [0, 0, 0, 1]:
                self.selected_cell.text = ""

    def on_clear_click(self, widget):
        # Find the SudokuGridLayout (second child after UpperBoxLayout)
        for child in self.children:
            if isinstance(child, SudokuGridLayout):
                sudoku_grid = self._find_sudoku_grid(child)
                if sudoku_grid:
                    for box in sudoku_grid.children:
                        for cell in box.children:
                            if cell.color != [0, 0, 0, 1]:
                                cell.text = ""
                break


class UpperBoxLayout(BoxLayout):
    pass


class NumPadLayout(BoxLayout):
    pass


class SudokuBox(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(9):
            b = Cell(size_hint=(.3, .3), color=(0, 0, 0.8, 1))
            self.add_widget(b)


class Cell(ToggleButton):
    pass


class NumPadButton(Button):
    pass


class NumPadControlButton(Button):
    pass


class SudokuGridLayout(RelativeLayout):
    pass


class SudokuGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(9):
            s = SudokuBox()
            self.add_widget(s)
        with open("Test_Sudoku.txt", "r") as f:
            puzzle = ast.literal_eval(f.read())
        i = 0
        for box in self.children:
            for cell in box.children:
                if puzzle[i] != 0:
                    cell.text = str(puzzle[i])
                    cell.color = (0, 0, 0, 1)
                i += 1


class SudokuApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(MenuWidget(name="menu"))
        sm.add_widget(MainWidget(name="puzzle"))

        return sm

if __name__ == '__main__':
    SudokuApp().run()
