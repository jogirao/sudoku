# import the necessary packages
from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border
from keras.models import load_model
import numpy as np
import imutils
import cv2


def extract_digit(cell, debug=False):
    # apply automatic thresholding to the cell and then clear any
    # connected borders that touch the border of the cell
    thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    thresh = clear_border(thresh)
    # check to see if we are visualizing the cell thresholding step
    if debug:
        cv2.imshow("Cell Thresh", thresh)
        cv2.waitKey(0)

    # find contours in the thresholded cell
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    # if no contours were found than this is an empty cell
    if len(contours) == 0:
        return None
    # otherwise, find the largest contour in the cell and create a
    # mask for the contour
    main_contour = max(contours, key=cv2.contourArea)
    mask = np.zeros(thresh.shape, dtype="uint8")
    cv2.drawContours(mask, [main_contour], -1, 255, -1)

    # compute the percentage of masked pixels relative to the total area of the image
    (height, weight) = thresh.shape
    percent_filled = cv2.countNonZero(mask) / float(weight * height)
    # if less than 3% of the mask is filled then we are looking at
    # noise and can safely ignore the contour
    if percent_filled < 0.03:
        return None
    # apply the mask to the thresholded cell
    digit = cv2.bitwise_and(thresh, thresh, mask=mask)
    # check to see if we should visualize the masking step
    if debug:
        cv2.imshow("Digit", digit)
        cv2.waitKey(0)
    # return the digit to the calling function
    return digit


def find_puzzle(image, debug=False):
    # convert the image to grayscale and blur it slightly
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 3)

    # apply adaptive thresholding and then invert the threshold map
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.bitwise_not(thresh)

    # check to see if we are visualizing each step of the image
    # processing pipeline (in this case, thresholding)
    if debug:
        cv2.imshow("Puzzle Thresh", thresh)
        cv2.waitKey(0)

    # find contours in the thresholded image and sort them by size in
    # descending order
    image_contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_contours = imutils.grab_contours(image_contours)
    image_contours = sorted(image_contours, key=cv2.contourArea, reverse=True)

    # initialize a contour that corresponds to the puzzle outline
    puzzle_contour = None

    # loop over the contours
    for contour in image_contours:
        # approximate the contour
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        # if our approximated contour has four points, then we can
        # assume we have found the outline of the puzzle
        if len(approx) == 4:
            puzzle_contour = approx
            break

    # if the puzzle contour is empty then our script could not find
    # the outline of the Sudoku puzzle so raise an error
    if puzzle_contour is None:
        raise Exception(("Could not find Sudoku puzzle outline. "
                         "Try debugging your thresholding and contour steps."))
    # check to see if we are visualizing the outline of the detected
    # Sudoku puzzle
    if debug:
        # draw the contour of the puzzle on the image and then display
        # it to our screen for visualization/debugging purposes
        output = image.copy()
        cv2.drawContours(output, [puzzle_contour], -1, (0, 255, 0), 2)
        cv2.imshow("Puzzle Outline", output)
        cv2.waitKey(0)

    # apply a four point perspective transform to both the original
    # image and grayscale image to obtain a top-down bird's eye view
    # of the puzzle
    sudoku = four_point_transform(image, puzzle_contour.reshape(4, 2))
    warped_image = four_point_transform(gray, puzzle_contour.reshape(4, 2))
    # check to see if we are visualizing the perspective transform
    if debug:
        # show the output warped image (again, for debugging purposes)
        cv2.imshow("Puzzle Transform", sudoku)
        cv2.waitKey(0)
    # return a 2-tuple of puzzle in both RGB and grayscale
    return sudoku, warped_image


def scan_new_puzzle(image_path, debug=False):
    # Scan an image for a puzzle and add it to the DB
    model = load_model("./output/digit_classifier.h5")
    image = cv2.imread(image_path)
    image = imutils.resize(image, width=600)

    # Find puzzle in the image
    (puzzleImage, warped) = find_puzzle(image, debug=debug)

    # Initialize 9x9 Sudoku board
    board = np.zeros((9, 9), dtype="int")
    # Compute side length of a cell
    step_x = warped.shape[1] // 9
    step_y = warped.shape[0] // 9
    # Initialize a list for the (x, y)-coordinates of each cell location
    cell_locations = []

    for y in range(0, 9):
        # Initialize current list of cell locations
        cell_coords = []
        for x in range(0, 9):
            # Compute starting and ending coordinates of current cell
            start_x, start_y = x * step_x, y * step_y
            end_x, end_y = (x + 1) * step_x, (y + 1) * step_y

            # Add coordinates to list of cell locations
            cell_coords.append((start_x, start_y, end_x, end_y))

            # Crop cell from warped image and extract digit from cell
            cell = warped[start_y:end_y, start_x:end_x]
            digit = extract_digit(cell, debug=debug)

            # Verify that cell is not empty
            if digit is not None:
                # Resize cell to 32x32 pixels and prepare cell for classification
                roi = cv2.equalizeHist(cv2.resize(digit, (32, 32)))
                roi = (255 - roi)/255
                roi = roi.reshape(1, 32, 32, 1)
                # Classify digit and update Sudoku board with prediction
                predictions = model.predict(roi)
                board[y, x] = predictions.argmax() + 1

        # Add the coordinates to our cell locations
        cell_locations.append(cell_coords)

    return board
