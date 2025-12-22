import os
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle


class PuzzleLibraryWidget(Screen):
    """Screen displaying a gallery of sudoku puzzles from the images folder"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        """Called when the screen is displayed - populate the gallery"""
        self.populate_gallery()

    def get_sudoku_images(self):
        """Get all sudoku images from the images folder"""
        # Try data/images first, then fall back to images for backwards compatibility
        for images_folder in ['data/images', 'images']:
            if os.path.exists(images_folder):
                sudoku_images = []
                for filename in os.listdir(images_folder):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        sudoku_images.append(os.path.join(images_folder, filename))
                if sudoku_images:
                    return sorted(sudoku_images)

        return []

    def populate_gallery(self):
        """Populate the gallery with puzzle images"""
        # Get the gallery grid
        gallery_grid = self.ids.gallery_grid

        # Clear existing children
        gallery_grid.clear_widgets()

        # Get all sudoku images
        sudoku_images = self.get_sudoku_images()

        if not sudoku_images:
            # Show a message if no images found
            label = Label(
                text="No puzzles found in the images folder",
                size_hint_y=None,
                height=100,
                color=(0.5, 0.5, 0.5, 1)
            )
            gallery_grid.add_widget(label)
            return

        # Create a card for each puzzle image
        for idx, image_path in enumerate(sudoku_images):
            card = self.create_puzzle_card(image_path, idx + 1)
            gallery_grid.add_widget(card)

    def create_puzzle_card(self, image_path, puzzle_number):
        """Create a card widget for a puzzle"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=400,
            spacing=12,
            padding=12
        )

        # Add background to card
        with card.canvas.before:
            Color(0.97, 0.99, 1, 1)  # Light blue background
            card.bg_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[12])

        card.bind(size=lambda instance, value: setattr(card.bg_rect, 'size', value))
        card.bind(pos=lambda instance, value: setattr(card.bg_rect, 'pos', value))

        # Puzzle image
        puzzle_image = Image(
            source=image_path,
            size_hint=(1, 0.85),
            allow_stretch=True,
            keep_ratio=True
        )
        card.add_widget(puzzle_image)

        # Puzzle info and button
        info_box = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.15),
            spacing=8
        )

        # Puzzle name
        filename = os.path.basename(image_path)
        puzzle_label = Label(
            text=f"Puzzle #{puzzle_number}: {filename}",
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(0.7, 1),
            halign='left',
            valign='center'
        )
        puzzle_label.bind(size=puzzle_label.setter('text_size'))

        # Play button
        play_button = Button(
            text="Play",
            size_hint=(0.3, 1),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            bold=True
        )

        # Add background to play button
        with play_button.canvas.before:
            Color(0.2, 0.6, 0.9, 1)
            play_button.bg_rect = RoundedRectangle(
                size=play_button.size,
                pos=play_button.pos,
                radius=[8]
            )

        play_button.bind(size=lambda instance, value: setattr(play_button.bg_rect, 'size', value))
        play_button.bind(pos=lambda instance, value: setattr(play_button.bg_rect, 'pos', value))
        play_button.bind(on_press=lambda x: self.play_puzzle(image_path))

        info_box.add_widget(puzzle_label)
        info_box.add_widget(play_button)
        card.add_widget(info_box)

        return card

    def play_puzzle(self, image_path):
        """Load and play the selected puzzle"""
        # For now, just navigate to the puzzle screen
        # In the future, you could load the specific puzzle from the image
        self.manager.current = "puzzle"
