import copy
import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)  # Remove mine from sentence
            self.count -= 1
            return None

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            return None


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        self.board = []
        for i in range(self.height):
            for j in range(self.width):
                self.board.append((i, j))

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_neighbours(self, cell):
        neighbours = []
        for neighbour_x in range(cell[0] - 1, cell[0] + 2):
            for neighbour_y in range(cell[1] - 1, cell[1] + 2):
                if (neighbour_x != cell[0] or neighbour_y != cell[1]) and (neighbour_x, neighbour_y) in self.board:
                    neighbours.append((neighbour_x, neighbour_y))
        # Check if neighbours were already clicked
        new_neighbours = []
        for neighbour in neighbours:
            if neighbour in self.moves_made:
                continue
            else:
                new_neighbours.append(neighbour)

        return new_neighbours

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)  # 1
        self.mark_safe(cell)  # 2

        neighbours = self.get_neighbours(cell)
        if Sentence(neighbours, count) not in self.knowledge:  # 3
            self.knowledge.append(Sentence(neighbours, count))

        for sentence in self.knowledge:  # 4
            if sentence.known_mines():
                for mine in sentence.known_mines().copy():
                    self.mark_mine(mine)
            if sentence.known_safes():
                for safe in sentence.known_safes().copy():
                    self.mark_safe(safe)

        known_knowledge = copy.deepcopy(self.knowledge)
        for sentence in known_knowledge:  # 5
            known_knowledge.remove(sentence)  # to avoid infinite loop
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)
                continue
            for sentence1 in known_knowledge:
                if len(sentence.cells) == len(sentence1.cells):
                    continue
                elif len(sentence.cells) > len(sentence1.cells):
                    bigger = sentence
                    smaller = sentence1
                else:
                    bigger = sentence1
                    smaller = sentence

                if bigger.cells >= smaller.cells:
                    diff_count = bigger.count - smaller.count
                    diff_cells = bigger.cells - smaller.cells
                    if len(diff_cells) == 1:
                        if diff_count == 0:
                            self.mark_safe(diff_cells.pop())
                        elif diff_count == 1:
                            self.mark_mine(diff_cells.pop())
                    else:
                        if Sentence(diff_cells, diff_count) not in self.knowledge:
                            self.knowledge.append(Sentence(diff_cells, diff_count))

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move in self.moves_made:
                continue
            else:
                self.moves_made.add(move)
                return move

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        potential_move = []
        board = set()
        for row in range(self.height):
            for cell in range(self.width):
                board.add((row, cell))

        for cell in board:
            if cell not in self.mines and cell not in self.moves_made:
                potential_move.append(cell)
        if len(potential_move) == 0:
            print(f'No more moves, Game over!')
        else:
            random_move = random.choice(potential_move)
            self.moves_made.add(random_move)
            return random_move
