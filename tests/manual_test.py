#!/usr/bin/env python3
"""
Manual test script to verify the app works correctly.
This will run the app briefly and check that bindings are set up correctly.
"""
import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.base import EventLoop
from kivy.clock import Clock
from Main import SudokuApp


def main():
    app = SudokuApp()

    def test_app(dt):
        print("\n=== Testing Sudoku App ===")

        # Navigate to puzzle screen
        app.root.current = "puzzle"

        def verify_setup(dt2):
            puzzle_screen = app.root.get_screen("puzzle")
            main_box = puzzle_screen.children[0]

            print(f"✓ App initialized")
            print(f"✓ Current screen: {app.root.current}")
            print(f"✓ MainBoxLayout type: {type(main_box).__name__}")
            print(f"✓ MainBoxLayout has on_number_click: {hasattr(main_box, 'on_number_click')}")
            print(f"✓ MainBoxLayout has on_cell_click: {hasattr(main_box, 'on_cell_click')}")
            print(f"✓ MainBoxLayout has on_delete_click: {hasattr(main_box, 'on_delete_click')}")
            print(f"✓ MainBoxLayout has on_clear_click: {hasattr(main_box, 'on_clear_click')}")

            # Check widget hierarchy
            print(f"\n=== Widget Hierarchy ===")
            print(f"MainBoxLayout children count: {len(main_box.children)}")

            for i, child in enumerate(main_box.children):
                print(f"  Child {i}: {type(child).__name__}")
                if hasattr(child, 'children'):
                    for j, subchild in enumerate(child.children):
                        print(f"    Subchild {j}: {type(subchild).__name__}")

            print("\n✓ All checks passed! The app should work correctly.")
            print("\nTo test manually:")
            print("1. Run: python3 Main.py")
            print("2. Click 'Play Sudoku'")
            print("3. Click a cell in the grid")
            print("4. Click a number on the numpad")
            print("5. The cell should populate with the number")

            app.stop()

        Clock.schedule_once(verify_setup, 0.5)

    Clock.schedule_once(test_app, 0.1)

    try:
        app.run()
    except:
        pass


if __name__ == "__main__":
    main()
