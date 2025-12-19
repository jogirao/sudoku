from kivy.app import App
from kivy.graphics import RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
# from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from menu import MenuWidget

Builder.load_file("menu.kv")


class MainWidget(Screen):
    pass


class MainBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_cell = None
        ubl = UpperBoxLayout()
        self.add_widget(ubl)
        sgl = SudokuGridLayout()
        self.add_widget(sgl)
        for box in self.children[0].children[0].children:
            for cell in box.children:
                cell.bind(state=self.on_cell_click)
        np = NumPadLayout()
        self.add_widget(np)
        for button in self.children[0].children:
            if button.text == "Delete":
                button.bind(on_press=self.on_delete_click)
            elif button.text == "Clear":
                button.bind(on_press=self.on_clear_click)
            else:
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
        for box in self.children[1].children[0].children:
            for cell in box.children:
                if cell.color != [0, 0, 0, 1]:
                    cell.text = ""


class UpperBoxLayout(BoxLayout):
    pass


class NumPadLayout(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        BOX_WIDTH1 = 60
        BOX_WIDTH2 = 91
        BOX_HEIGHT = 60
        for i in range(9):
            if i == 0:
                b = NumPadCornerButton1(text=str(i + 1), size_hint=(None, None), size=(dp(BOX_WIDTH1), dp(BOX_HEIGHT)), bold=True)
                self.add_widget(b)
            elif i == 2:
                b = NumPadCornerButton2(text=str(i + 1), size_hint=(None, None), size=(dp(BOX_WIDTH1), dp(BOX_HEIGHT)), bold=True)
                self.add_widget(b)
            else:
                b = NumPadButton(text=str(i+1), size_hint=(None, None), size=(dp(BOX_WIDTH1), dp(BOX_HEIGHT)), bold=True)
                self.add_widget(b)
        b = NumPadCornerButton3(text="Delete", size_hint=(None, None), size=(dp(BOX_WIDTH2), dp(BOX_HEIGHT)), bold=True)
        self.add_widget(b)
        b = NumPadCornerButton4(text="Clear", size_hint=(None, None), size=(dp(BOX_WIDTH2), dp(BOX_HEIGHT)), bold=True)
        self.add_widget(b)


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


class NumPadCornerButton1(Button):
    pass


class NumPadCornerButton2(Button):
    pass


class NumPadCornerButton3(Button):
    pass


class NumPadCornerButton4(Button):
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
            puzzle = eval(f.read())
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
