# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 22:20:19 2021

@author: joaom
"""

from tkinter import Canvas, Frame, Button, BOTH, LEFT, RIGHT


BOARDS = ['debug', 'n00b', 'l33t', 'error']  # Available sudoku boards
MARGIN = 20  # Pixels around the board
SIDE = 50  # Width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9  # Width and height of the whole board
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 40

class SudokuError(Exception):
    """
    An application specific error.
    """
    pass


class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """
    def __init__(self, parent, game):
        self.game = game
        self.parent = parent
        Frame.__init__(self, parent)
        self.row, self.col = 0, 0

        self.__init_ui()

    # Set up UI
    def __init_ui(self):
        self.parent.title("Sudoku")
        self.parent.geometry("%dx%d" % (WIDTH + 3.5 * BUTTON_WIDTH, HEIGHT))
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(side=LEFT)
        self.buttons_frame = Frame(self, width=4 * BUTTON_WIDTH, height=4 * BUTTON_HEIGHT)
        self.buttons_frame.pack(side=RIGHT)
        one_button = Button(self.buttons_frame, text="1", font=("Bold", 20), command=lambda: self.__insert_number(1))
        one_button.place(x=0, y=0, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        two_button = Button(self.buttons_frame, text="2", font=("Bold", 20), command=lambda: self.__insert_number(2))
        two_button.place(x=BUTTON_WIDTH, y=0, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        three_button = Button(self.buttons_frame, text="3", font=("Bold", 20), command=lambda: self.__insert_number(3))
        three_button.place(x=2 * BUTTON_WIDTH, y=0, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        four_button = Button(self.buttons_frame, text="4", font=("Bold", 20), command=lambda: self.__insert_number(4))
        four_button.place(x=0, y=BUTTON_HEIGHT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        five_button = Button(self.buttons_frame, text="5", font=("Bold", 20), command=lambda: self.__insert_number(5))
        five_button.place(x=BUTTON_WIDTH, y=BUTTON_HEIGHT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        six_button = Button(self.buttons_frame, text="6", font=("Bold", 20), command=lambda: self.__insert_number(6))
        six_button.place(x=2 * BUTTON_WIDTH, y=BUTTON_HEIGHT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        seven_button = Button(self.buttons_frame, text="7", font=("Bold", 20), command=lambda: self.__insert_number(7))
        seven_button.place(x=0, y=2 * BUTTON_HEIGHT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        eight_button = Button(self.buttons_frame, text="8", font=("Bold", 20), command=lambda: self.__insert_number(8))
        eight_button.place(x=BUTTON_WIDTH, y=2 * BUTTON_HEIGHT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        nine_button = Button(self.buttons_frame, text="9", font=("Bold", 20), command=lambda: self.__insert_number(9))
        nine_button.place(x=2 * BUTTON_WIDTH, y=2 * BUTTON_HEIGHT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        delete_button = Button(self.buttons_frame, text="Del", font=("Bold", 20), command=lambda: self.__insert_number(0))
        delete_button.place(x=0, y=3 * BUTTON_HEIGHT, width=1.5 * BUTTON_WIDTH, height=BUTTON_HEIGHT)
        clear_button = Button(self.buttons_frame, text="Clear", font=("Bold", 20), command=self.__clear_answers)
        clear_button.place(x=1.5 * BUTTON_WIDTH, y=3 * BUTTON_HEIGHT, width=1.5 * BUTTON_WIDTH, height=BUTTON_HEIGHT)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    def __cell_clicked(self, event):
        if self.game.game_over:
            return

        x, y = event.x, event.y
        if MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN:
            self.canvas.focus_set()

            # Get row and col numbers from x,y coordinates
            row, col = (y - MARGIN) // SIDE, (x - MARGIN) // SIDE

            # If cell was already selected, deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.start_state[row][col] == 0:
                self.row, self.col = row, col

        self.__draw_cursor()

    def __clear_answers(self):
        self.game.reset_sudoku()
        self.canvas.delete("victory")
        self.canvas.delete("winner")
        self.__draw_puzzle()

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", tags="cursor")

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(10):
            color = "black" if i % 3 == 0 else "gray"

            # Draw vertical lines
            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            # Draw horizontal lines
            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.state[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.game.start_state[i][j]
                    color = "black" if answer == original else "slate gray"
                    self.canvas.create_text(x, y, text=answer, tags="numbers", fill=color, font=("Bold", 20))

    def __draw_victory(self):
        # create a oval (which will be a circle)
        x0 = y0 = MARGIN + SIDE * 2
        x1 = y1 = MARGIN + SIDE * 7
        self.canvas.create_oval(x0, y0, x1, y1, tags="victory", fill="dark orange", outline="orange")
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(x, y, text="You win!", tags="winner", fill="white", font=("Arial", 32))

    def __insert_number(self, number):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and self.game.start_state[self.row][self.col] == 0:
            self.game.state[self.row][self.col] = number
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_solution():
                self.__draw_victory()

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890" and \
                self.game.start_state[self.row][self.col] == 0:
            self.game.state[self.row][self.col] = int(event.char)
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_solution():
                self.__draw_victory()
