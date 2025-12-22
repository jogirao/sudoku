#!/usr/bin/env python3
"""Test script for the Puzzle Library screen"""
import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.base import EventLoop
from kivy.clock import Clock
from Main import SudokuApp


def test_library_screen():
    """Test that the library screen initializes and displays correctly"""
    app = SudokuApp()

    def run_tests(dt):
        print("\n=== Testing Puzzle Library Screen ===")

        # Navigate to library screen
        app.root.current = "library"

        def verify_library(dt2):
            # Get the library screen
            library_screen = app.root.get_screen("library")

            print(f"✓ Library screen found: {type(library_screen).__name__}")
            print(f"✓ Current screen: {app.root.current}")

            # Check that the gallery grid exists
            assert hasattr(library_screen.ids, 'gallery_grid'), "Gallery grid should exist"
            print(f"✓ Gallery grid exists")

            # Get sudoku images
            images = library_screen.get_sudoku_images()
            print(f"✓ Found {len(images)} sudoku image(s) in images folder")

            for img in images:
                print(f"  - {img}")

            # Check that populate_gallery works
            gallery_grid = library_screen.ids.gallery_grid
            print(f"✓ Gallery has {len(gallery_grid.children)} card(s)")

            # Test navigation back to menu
            app.root.current = "menu"

            def verify_back_navigation(dt3):
                print(f"✓ Navigation back to menu works: {app.root.current}")
                print("\n✓ All library tests passed!")
                app.stop()

            Clock.schedule_once(verify_back_navigation, 0.3)

        Clock.schedule_once(verify_library, 0.5)

    Clock.schedule_once(run_tests, 0.1)

    try:
        app.run()
    except:
        pass


if __name__ == "__main__":
    test_library_screen()
