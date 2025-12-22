"""Scanner screen with camera functionality"""
import os
import numpy as np
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

from src.utils.scanner import SudokuScanner


class ScannerWidget(Screen):
    """Camera screen for scanning Sudoku puzzles"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scanner = SudokuScanner()
        self.camera = None
        self.is_processing = False

    def on_enter(self):
        """Initialize camera when screen is entered"""
        if platform == 'android':
            self.request_android_permissions()
        else:
            self.initialize_camera()

    def request_android_permissions(self):
        """Request camera permission on Android"""
        try:
            from android.permissions import request_permissions, Permission

            def callback(permissions, results):
                if all(results):
                    Logger.info("Scanner: Camera permission granted")
                    self.initialize_camera()
                else:
                    Logger.warning("Scanner: Camera permission denied")
                    self.show_error("Camera permission is required to scan puzzles")
                    self.ids.capture_btn.text = "Grant Permission"
                    self.ids.capture_btn.on_press = self.request_android_permissions

            request_permissions([Permission.CAMERA], callback)
        except ImportError:
            # android.permissions not available (desktop)
            self.initialize_camera()

    def initialize_camera(self):
        """Initialize camera widget"""
        try:
            # Camera widget will be created in KV file
            if not hasattr(self.ids, 'camera'):
                raise Exception("Camera widget not found in layout")

            self.camera = self.ids.camera
            self.camera.play = True
            Logger.info("Scanner: Camera initialized successfully")
        except Exception as e:
            Logger.error(f"Scanner: Camera initialization failed: {e}")
            self.show_camera_unavailable_ui()

    def show_camera_unavailable_ui(self):
        """Show alternative UI when camera is unavailable"""
        self.ids.status_label.text = "Camera not available on this device"
        self.ids.capture_btn.text = "Back to Menu"
        self.ids.capture_btn.on_press = lambda: setattr(
            self.manager, 'current', 'menu'
        )

    def on_leave(self):
        """Stop camera when leaving screen"""
        if self.camera:
            self.camera.play = False
            Logger.info("Scanner: Camera stopped")

    def capture_image(self):
        """Capture image from camera and process it"""
        if self.is_processing:
            Logger.info("Scanner: Already processing, ignoring capture request")
            return

        if not self.camera or not self.camera.texture:
            self.show_error("Camera not ready")
            return

        self.is_processing = True
        self.ids.status_label.text = "Processing image..."
        self.ids.capture_btn.disabled = True

        Logger.info("Scanner: Image captured, starting processing")

        # Schedule processing in next frame to update UI
        Clock.schedule_once(self._process_capture, 0.1)

    def _process_capture(self, dt):
        """Process captured image (runs asynchronously)"""
        try:
            Logger.info("Scanner: Converting camera texture to numpy array")
            # Convert Kivy texture to numpy array
            image_array = self._texture_to_numpy(self.camera.texture)

            Logger.info("Scanner: Scanning image for Sudoku puzzle")
            # Process with scanner
            board = self.scanner.scan_image(image_array, debug=False)

            # Validate puzzle detection
            if not self.scanner.validate_board(board):
                raise Exception("No valid Sudoku puzzle detected")

            Logger.info("Scanner: Puzzle detected successfully")

            # Save puzzle to file
            puzzle_path = self._save_puzzle(board)

            # Navigate to puzzle screen with new puzzle
            self._load_puzzle_and_navigate(puzzle_path)

        except Exception as e:
            Logger.error(f"Scanner: Processing failed: {e}")
            self.show_error(str(e))
            self.is_processing = False
            self.ids.capture_btn.disabled = False

    def _texture_to_numpy(self, texture):
        """
        Convert Kivy texture to OpenCV-compatible numpy array
        Args:
            texture: Kivy texture object
        Returns:
            numpy array in BGR format (OpenCV compatible)
        """
        # Get pixel data from texture
        pixels = texture.pixels
        size = texture.size

        # Convert to numpy array (RGBA format)
        arr = np.frombuffer(pixels, dtype=np.uint8)
        arr = arr.reshape(size[1], size[0], 4)

        # Convert RGBA to BGR (OpenCV format)
        # Drop alpha channel and swap R and B
        arr = arr[:, :, [2, 1, 0]]

        # Flip vertically (Kivy texture is upside down)
        arr = np.flip(arr, axis=0)

        return arr.copy()

    def _save_puzzle(self, board):
        """
        Save board to puzzle file
        Args:
            board: 9x9 numpy array
        Returns:
            str: path to saved puzzle file
        """
        # Flatten board to 81-element list
        puzzle_list = board.flatten().tolist()

        # Generate unique filename with timestamp
        import time
        timestamp = int(time.time())
        filename = f"scanned_puzzle_{timestamp}.txt"
        filepath = os.path.join("data", "puzzles", filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Write puzzle
        with open(filepath, "w") as f:
            f.write(str(puzzle_list))

        Logger.info(f"Scanner: Puzzle saved to {filepath}")
        return filepath

    def _load_puzzle_and_navigate(self, puzzle_path):
        """
        Load puzzle into puzzle screen and navigate
        Args:
            puzzle_path: Path to puzzle file
        """
        try:
            # Access puzzle screen
            puzzle_screen = self.manager.get_screen("puzzle")

            # Get the SudokuGrid widget (nested in the widget tree)
            # MainWidget -> MainBoxLayout -> BoxLayout -> SudokuGridLayout -> BoxLayout -> SudokuGrid
            main_box = puzzle_screen.children[0]

            # Find SudokuGridLayout
            from src.widgets.sudoku_grid import SudokuGridLayout, SudokuGrid

            sudoku_grid = None
            for child in main_box.children:
                if isinstance(child, SudokuGridLayout):
                    # Navigate to find SudokuGrid
                    for sub_child in child.children:
                        for grid_child in sub_child.children:
                            if isinstance(grid_child, SudokuGrid):
                                sudoku_grid = grid_child
                                break
                        if sudoku_grid:
                            break
                    break

            if sudoku_grid:
                # Load the puzzle
                sudoku_grid.puzzle_file = puzzle_path
                sudoku_grid.load_puzzle()
                Logger.info("Scanner: Puzzle loaded into grid")
            else:
                Logger.error("Scanner: Could not find SudokuGrid widget")

            # Navigate to puzzle screen
            self.manager.current = "puzzle"

            # Reset scanner state
            self.is_processing = False
            self.ids.capture_btn.disabled = False
            self.ids.status_label.text = "Position puzzle in frame"

            Logger.info("Scanner: Navigated to puzzle screen")

        except Exception as e:
            Logger.error(f"Scanner: Navigation failed: {e}")
            self.show_error(f"Failed to load puzzle: {str(e)}")
            self.is_processing = False
            self.ids.capture_btn.disabled = False

    def show_error(self, message):
        """
        Display error message to user
        Args:
            message: Error message string
        """
        # Show helpful, user-friendly messages
        if "outline" in message.lower() or "not find" in message.lower():
            error_msg = ("No puzzle detected.\n\n"
                        "Tips:\n"
                        "• Ensure good lighting\n"
                        "• Position puzzle clearly in frame\n"
                        "• Avoid glare and shadows\n"
                        "• Use a flat surface")
        elif "resolution too low" in message.lower():
            error_msg = "Image quality too low.\nPlease move closer to the puzzle."
        elif "valid" in message.lower():
            error_msg = ("Puzzle detection incomplete.\n\n"
                        "Please ensure:\n"
                        "• All grid lines are visible\n"
                        "• Numbers are clear and legible\n"
                        "• Good contrast between paper and numbers")
        else:
            error_msg = f"Scan failed: {message}"

        self.ids.status_label.text = error_msg
        Logger.info(f"Scanner: Showing error to user: {error_msg}")

    def retry_scan(self):
        """Reset and allow retry"""
        self.ids.status_label.text = "Position puzzle in frame"
        self.ids.capture_btn.disabled = False
        self.is_processing = False
        Logger.info("Scanner: Ready for new scan")
