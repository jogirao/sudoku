#!/usr/bin/env python3
"""Manual visual test for the Puzzle Library screen - runs for 10 seconds"""
import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.base import EventLoop
from kivy.clock import Clock
from Main import SudokuApp


def test_library_visual():
    """Run the app and automatically navigate to library for visual inspection"""
    app = SudokuApp()

    def navigate_to_library(dt):
        print("\n=== Visual Test: Puzzle Library ===")
        print("Navigating to library screen...")
        app.root.current = "library"

        def show_info(dt2):
            library_screen = app.root.get_screen("library")
            images = library_screen.get_sudoku_images()
            gallery_grid = library_screen.ids.gallery_grid

            print(f"\nLibrary Screen Info:")
            print(f"  - Sudoku images found: {len(images)}")
            print(f"  - Gallery cards: {len(gallery_grid.children)}")

            if gallery_grid.children:
                print(f"\nThe library screen is displaying!")
                print(f"You should see {len(gallery_grid.children)} puzzle card(s)")
            else:
                print("\nNote: Cards might not be visible yet")

            print("\nThe app will automatically close in 5 seconds...")

            def close_app(dt3):
                print("Closing app...")
                app.stop()

            Clock.schedule_once(close_app, 5)

        Clock.schedule_once(show_info, 1)

    Clock.schedule_once(navigate_to_library, 0.5)

    try:
        app.run()
    except:
        pass


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Manual Visual Test")
    print("="*50)
    print("\nThis will:")
    print("1. Launch the app")
    print("2. Navigate to the library screen")
    print("3. Display the puzzle gallery")
    print("4. Close after 5 seconds")
    print("\nStarting in 2 seconds...")
    print("="*50 + "\n")

    import time
    time.sleep(2)

    test_library_visual()
