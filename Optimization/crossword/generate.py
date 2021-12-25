import sys

from crossword import *


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()  # Works good
        self.ac3()  # works good
        return self.backtrack(dict())   # something is wrong

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision_made = False
        overlaps = self.crossword.overlaps[x, y]
        to_be_removed = []

        if overlaps is None:
            return False
        else:
            for w1 in self.domains[x]:
                conflict = True
                for w2 in self.domains[y]:
                    if w1[overlaps[0]] == w2[overlaps[1]]:
                        conflict = False
                if conflict:
                    to_be_removed.append(w1)
                    revision_made = True

        for word in to_be_removed:
            self.domains[x].remove(word)

        return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = []
            for var in self.crossword.variables:
                for neighbour in self.crossword.neighbors(var):
                    if (var, neighbour) not in queue:
                        queue.append((var, neighbour))
        else:
            queue = arcs

        while len(queue) != 0:
            (x, y) = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):  # Adding new arcs in case they might be not arc consistent
                    if z != y:
                        queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.crossword.variables):
            return True
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Each value is unique
        values = []
        for key, word in assignment.items():
            values.append(word)

        for i, val in enumerate(values):
            if i != len(values):
                if val in values[i+1:]:
                    return False

        # Each value is the correct length
        for var in assignment.keys():
            if var.length != len(assignment[var]):
                return False

        # No Conflicts between variables
        keys = list(assignment.keys())
        for i, key in enumerate(keys):
            if i != len(keys):
                for key1 in keys[i+1:]:
                    overlaps = self.crossword.overlaps[key, key1]
                    if overlaps is None:
                        continue
                    else:
                        if assignment[key][overlaps[0]] != assignment[key1][overlaps[1]]:
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbours of `var`.
        """
        values = list(self.domains[var])
        eliminate_count = []
        neighbours = self.crossword.neighbors(var)

        # avoid computing already assigned variables
        for neighbour in neighbours.copy():
            if neighbour in assignment.keys():
                neighbours.remove(neighbour)

        for val in values:
            n = 0

            for neighbour in neighbours:
                # Eliminating the same values
                if val in self.domains[neighbour]:
                    n += 1
                # Eliminating overlapped values
                overlaps = self.crossword.overlaps[var, neighbour]
                for val1 in self.domains[neighbour]:
                    if val != val1:
                        if val[overlaps[0]] != val1[overlaps[1]]:
                            n += 1

            eliminate_count.append(n)

        sorted_values = []

        for i in range(len(values)):
            if len(sorted_values) == len(values):
                break
            minim = min(eliminate_count)
            for j, val in enumerate(eliminate_count):
                if val == minim:
                    sorted_values.append(values[j])
                    eliminate_count[j] = float('inf')

        return sorted_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        variables = self.crossword.variables.copy()
        var_to_be_removed = []

        # Enforcing a list of unused variables
        for var in variables:
            if var in assignment.keys():
                var_to_be_removed.append(var)

        for var in var_to_be_removed:
            variables.remove(var)

        # Sorting variables
        number_of_options = {}  # len(options) : var
        for var in variables:
            options = len(self.domains[var])
            number_of_options[options] = var

        options = sorted(number_of_options)
        sorted_variables = []
        for i, number in enumerate(options):
            if i == 0:
                sorted_variables.append(number_of_options[number])
            else:
                if number == options[i-1]:
                    sorted_variables.append(number_of_options[number])
                else:
                    break

        # there is a tie between number of remaining values
        if len(sorted_variables) != 1:
            maxi = float('-inf')
            # Calculating the most neighbours
            for var in sorted_variables:
                number_of_neighbours = len(self.crossword.neighbors(var))
                if number_of_neighbours > maxi:
                    maxi = number_of_neighbours

            for var in sorted_variables:
                if len(self.crossword.neighbors(var)) == maxi:
                    return var
        else:
            return sorted_variables[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        # print(f'Var = {var}')
        values = self.order_domain_values(var, assignment)
        # print(f'Val = {values}')
        for value in values:
            assignment_copy = assignment.copy()
            assignment_copy[var] = value
            if self.consistent(assignment_copy):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            if var in assignment.keys():
                assignment[var] = [val for val in assignment[var] if val != value]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)

    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
