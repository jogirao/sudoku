"""
Sudoku scanner module - image processing and digit recognition
Adapted from SudokuScanner.py (commit 2f7f3c7)
"""
import os
import platform
import numpy as np
import cv2
import imutils
from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border
from kivy.logger import Logger


class SudokuScanner:
    """Sudoku puzzle scanner using OpenCV and TensorFlow"""

    def __init__(self, model_path=None):
        """
        Initialize scanner with optional model path
        Args:
            model_path: Path to model file (h5 or tflite). Auto-detects if None.
        """
        self.model = None
        self.interpreter = None
        self.use_tflite = False

        # Auto-detect platform and choose appropriate model
        self.is_mobile = (platform.system() == 'Linux' and
                         'ANDROID_BOOTLOGO' in os.environ)

        if model_path is None:
            # Auto-detect model format based on platform
            if self.is_mobile:
                model_path = "output/digit_classifier.tflite"
            else:
                model_path = "output/digit_classifier.h5"

        self.model_path = model_path
        self.input_details = None
        self.output_details = None

    def load_model(self):
        """Lazy load model - TFLite for Android, Keras for desktop"""
        if self.model is not None or self.interpreter is not None:
            return  # Already loaded

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        try:
            if self.is_mobile or self.model_path.endswith('.tflite'):
                # Use TensorFlow Lite for mobile
                import tensorflow as tf
                Logger.info(f"Scanner: Loading TFLite model from {self.model_path}")
                self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                self.use_tflite = True
                Logger.info("Scanner: TFLite model loaded successfully")
            else:
                # Use full Keras model for desktop
                from tensorflow import keras
                Logger.info(f"Scanner: Loading Keras model from {self.model_path}")
                self.model = keras.models.load_model(self.model_path)
                self.use_tflite = False
                Logger.info("Scanner: Keras model loaded successfully")
        except Exception as e:
            Logger.error(f"Scanner: Failed to load model: {e}")
            raise

    def predict_digit(self, roi):
        """
        Predict digit using loaded model
        Args:
            roi: Preprocessed image region (1, 32, 32, 1)
        Returns:
            predictions: Model output array
        """
        if self.use_tflite:
            # TFLite inference
            self.interpreter.set_tensor(
                self.input_details[0]['index'],
                roi.astype(np.float32)
            )
            self.interpreter.invoke()
            predictions = self.interpreter.get_tensor(
                self.output_details[0]['index']
            )
        else:
            # Keras inference
            predictions = self.model.predict(roi, verbose=0)

        return predictions

    def extract_digit(self, cell, debug=False):
        """
        Extract digit from cell image
        Args:
            cell: Grayscale cell image
            debug: Show debug visualizations
        Returns:
            digit: Binary image of digit, or None if empty
        """
        # Apply automatic thresholding and clear borders
        thresh = cv2.threshold(
            cell, 0, 255,
            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )[1]
        thresh = clear_border(thresh)

        # Find contours in the thresholded cell
        contours = cv2.findContours(
            thresh.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        contours = imutils.grab_contours(contours)

        # If no contours, this is an empty cell
        if len(contours) == 0:
            return None

        # Find the largest contour and create a mask
        main_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros(thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [main_contour], -1, 255, -1)

        # Compute percentage of masked pixels
        (height, width) = thresh.shape
        percent_filled = cv2.countNonZero(mask) / float(width * height)

        # If less than 3% filled, this is noise
        if percent_filled < 0.03:
            return None

        # Apply the mask to extract digit
        digit = cv2.bitwise_and(thresh, thresh, mask=mask)

        return digit

    def find_puzzle(self, image, debug=False):
        """
        Find and extract Sudoku puzzle from image
        Args:
            image: Input image (BGR format)
            debug: Show debug visualizations
        Returns:
            (puzzle_rgb, warped_gray): Warped puzzle images
        Raises:
            Exception: If puzzle outline not found
        """
        # Convert to grayscale and blur
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Check if image is too dark and enhance if needed
        if np.mean(gray) < 50:
            Logger.info("Scanner: Low light detected, applying CLAHE enhancement")
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)

        blurred = cv2.GaussianBlur(gray, (7, 7), 3)

        # Apply adaptive thresholding and invert
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        thresh = cv2.bitwise_not(thresh)

        # Find contours and sort by size
        image_contours = cv2.findContours(
            thresh.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        image_contours = imutils.grab_contours(image_contours)
        image_contours = sorted(
            image_contours,
            key=cv2.contourArea,
            reverse=True
        )

        # Find puzzle outline (4-sided contour)
        puzzle_contour = None
        for contour in image_contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            if len(approx) == 4:
                puzzle_contour = approx
                break

        if puzzle_contour is None:
            raise Exception(
                "Could not find Sudoku puzzle outline. "
                "Ensure good lighting and clear puzzle edges."
            )

        # Apply perspective transform
        puzzle_rgb = four_point_transform(image, puzzle_contour.reshape(4, 2))
        warped_gray = four_point_transform(gray, puzzle_contour.reshape(4, 2))

        return puzzle_rgb, warped_gray

    def scan_image(self, image_data, debug=False):
        """
        Scan image and extract Sudoku puzzle
        Args:
            image_data: numpy array (BGR format from camera or file)
            debug: Show debug visualizations
        Returns:
            board: 9x9 numpy array with detected digits (0 for empty)
        Raises:
            Exception: If processing fails
        """
        # Ensure model is loaded
        self.load_model()

        # Resize for processing
        image = imutils.resize(image_data, width=600)

        # Check minimum image size
        if image.shape[0] < 100 or image.shape[1] < 100:
            raise Exception("Image resolution too low. Please move closer.")

        # Find and extract puzzle
        Logger.info("Scanner: Detecting puzzle outline...")
        puzzle_image, warped = self.find_puzzle(image, debug=debug)

        # Initialize 9x9 board
        board = np.zeros((9, 9), dtype="int")

        # Compute cell dimensions
        step_x = warped.shape[1] // 9
        step_y = warped.shape[0] // 9

        Logger.info("Scanner: Extracting and classifying digits...")

        # Extract and classify each cell
        for y in range(9):
            for x in range(9):
                # Compute cell coordinates
                start_x, start_y = x * step_x, y * step_y
                end_x, end_y = (x + 1) * step_x, (y + 1) * step_y

                # Extract cell
                cell = warped[start_y:end_y, start_x:end_x]
                digit = self.extract_digit(cell, debug=debug)

                # If cell has a digit, classify it
                if digit is not None:
                    # Prepare for classification (32x32, normalized)
                    roi = cv2.equalizeHist(cv2.resize(digit, (32, 32)))
                    roi = (255 - roi) / 255.0
                    roi = roi.reshape(1, 32, 32, 1)

                    # Predict digit
                    predictions = self.predict_digit(roi)
                    digit_value = predictions.argmax() + 1
                    board[y, x] = digit_value

        Logger.info(f"Scanner: Detected {np.count_nonzero(board)} filled cells")
        return board

    def validate_board(self, board):
        """
        Check if board has minimum viable cells for a valid puzzle
        Args:
            board: 9x9 numpy array
        Returns:
            bool: True if valid puzzle detected
        """
        filled_cells = np.count_nonzero(board)
        # Typical Sudoku has at least 17 clues minimum
        is_valid = filled_cells >= 17

        if not is_valid:
            Logger.warning(
                f"Scanner: Only {filled_cells} cells detected "
                "(minimum 17 required for valid puzzle)"
            )

        return is_valid
