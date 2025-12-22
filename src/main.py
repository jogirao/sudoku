"""Main application file for Sudoku"""
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from src.screens import MenuWidget, PuzzleLibraryWidget, MainWidget, ScannerWidget


class SudokuApp(App):
    """Main Sudoku application"""

    def build(self):
        # Load KV files
        Builder.load_file("src/assets/menu.kv")
        Builder.load_file("src/assets/library.kv")
        Builder.load_file("src/assets/puzzle.kv")
        Builder.load_file("src/assets/scanner.kv")

        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(MenuWidget(name="menu"))
        sm.add_widget(MainWidget(name="puzzle"))
        sm.add_widget(PuzzleLibraryWidget(name="library"))
        sm.add_widget(ScannerWidget(name="scanner"))

        return sm


def main():
    """Entry point for the application"""
    SudokuApp().run()


if __name__ == '__main__':
    main()
