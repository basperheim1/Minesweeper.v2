import random
from util import encode, decode 
from typing import List, Tuple, Dict
from rule import Rule 
from minesweeper import MinesweeperSolver
from cell import Cell

class GameStrings:
    MINE = '💣'
    FLAG = '🚩'
    UNREVEALED = '■'
    EMPTY = ' '
    COVERED_STATE = "covered"
    EXPLODED_STATE = "exploded"

class MinesweeperBoard:
    def __init__(self, rows, cols, mine_count):
        
        # Static
        self.rows = rows
        self.cols = cols
        self.mine_count = mine_count
        self.cell_count = rows*cols
        self.safe_count = self.cell_count - self.mine_count
        
        # Dyanmic
        self.undetermined_mine_count = mine_count
        self.cells_with_no_information = self.cell_count
        self.uncovered_cell_count = 0
        
        # State variables for win / loss
        self.continue_playing = True
        self.lost = False 
        
        # Board
        self.board: List[Cell, Cell] = [[Cell(row, col, cols) for col in range(cols)] for row in range(rows)]
        
    
    def get_first_guess(self) -> Tuple[int, int]:
        print("Make your first guess! (This spot will be safe)")
        return self.get_valid_coordinates()
        
        
    def get_board_size(max_rows=24, max_cols=30) -> Tuple[int, int]:
        while True:
            try:
                user_input = input(f"Enter board size as 'rows columns' (max {max_rows} rows, {max_cols} columns): ")
                row_str, col_str = user_input.strip().split()
                rows, cols = int(row_str), int(col_str)

                if 1 <= rows <= max_rows and 1 <= cols <= max_cols:
                    return rows, cols
                else:
                    print(f"Invalid size. Rows must be 1 to {max_rows}, columns must be 1 to {max_cols}. Try again.")
            except ValueError:
                print("Invalid input. Please enter two numbers separated by a space.")
        
        
    def print_board(self):
        """
        Prints the board 
        """
        
        top_row = "     "
        for col_index in range(len(self.board[0])):
            if col_index > 9:
                
                top_row += f"{col_index}    "
            
            else:
                top_row += f"{col_index}     "
        print(top_row)
        
        for row_index in range(len(self.board)):
            row = ' '.join(str(cell) for cell in self.board[row_index])
            if row_index > 9:
                print(f"{row_index} {row}")
            else:
                print(f" {row_index} {row}")

            # print(' '.join(str(cell) for cell in self.board[row_index]))
            
            
    def get_valid_coordinates(self):
        """
        Ensures that the guess the user is making is within the 
        bounds of the board. 
        """
        
        rows = self.rows
        cols = self.cols
        
        while True:
            try:
                user_input = input(f"Enter row and column (0 to {rows - 1} and 0 to {cols - 1}) separated by a space: ")
                row_str, col_str = user_input.strip().split()
                row, col = int(row_str), int(col_str)

                if 0 <= row < rows and 0 <= col < cols:
                    return row, col
                else:
                    print(f"Coordinates out of bounds. Please enter values between 0 and {rows - 1} for rows, and 0 and {cols - 1} for columns.")
            except ValueError:
                print("Invalid input. Please enter two numbers separated by a space.")

    
    def place_mines_safe(self, safe_row, safe_col):
        """
        Places mines around the board, but makes sure to avoid the user's first guess.
        """
        rows = self.rows
        cols = self.cols
        
        # Create a set of positions excluding the safe cell
        all_positions = [(r, c) for r in range(rows) for c in range(cols) if (r, c) != (safe_row, safe_col)]
        
        # Randomly sample mine positions
        mine_positions = random.sample(all_positions, self.mine_count)

        # Place the mines
        for r, c in mine_positions:
            self.board[r][c].is_mine = True
            
    def determine_outcome(self):
        """
        Function that is ran when the game terminates, right now 
        just prints either you win or you lose 
        """
        if self.lost:
            print("You lost, better luck next time")
            
        else:
            print("Congratulations, you won the game!")
            
    def reveal_all(self):
        """
        Function that reveals all the cells in the board, called 
        when game is over 
        """
        for row in range(self.rows):
            for col in range(self.cols):
                self.board[row][col].revealed = True
            
    def count_board_adjacent_mines_and_cells(self):
        """
        Function that is ran once to get a count of the adjacent 
        mines and cells for all cells in the board 
        
        Each cell in our grid has a number of cells around it and 
        also a number of mines around it. These values will never 
        change, and that is why we only need to calculate them once. 
        This is ran at the beginning of our play_game function, and 
        gives us important info needed in the solving process
        """
        for row in range(self.rows):
            for col in range(self.cols):
                self.count_adjacent_mines_and_cells(row, col)
                

    def count_adjacent_mines_and_cells(self, row, col):
        """
        This function counts the number of mines and cells 
        adjacent to some cell in our board
        
        This function is called many times by the count_board_adjacent_mines_and_cells
        at the start of our code. This function only counts the number of adjacent 
        mines and cells for one cell in our code, and that is why it is ran many times
        """
        
        cell = self.board[row][col]
        
        cell_count = 0
        mine_count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    cell_count += 1
                    if self.board[nr][nc].is_mine:
                        mine_count += 1
                        
        cell.adjacent_cell_count = cell_count
        cell.adjacent_undetermined_cell_count = cell_count
        cell.adjacent_mine_count = mine_count
        cell.adjacent_undetermined_mine_count = mine_count

            
    def click_cell(self, row: int, col: int) -> bool:
        
        clicked_cell: Cell = self.board[row][col]

        # Cell has already been clicked, no need to proceed
        if clicked_cell.revealed:
            return True 
        
        self.uncovered_cell_count += 1
        
        # If before being clicked the cell had no information as 
        # to whether or not it was a mine, now it does, and we 
        # need to modify the class level counter 
        if not clicked_cell.some_information:
            self.cells_with_no_information -= 1
        
        # Cell has not been clicked, meaning we need to update the cells adjacent to it 
        self.update_adjacent_cells(row, col, clicked_cell.is_mine, True, clicked_cell.determined)
        
        clicked_cell.some_information = True
        clicked_cell.determined = True
        clicked_cell.revealed = True
        clicked_cell.probability = float(clicked_cell.is_mine)

        
        if clicked_cell.is_mine:
            clicked_cell.state = GameStrings.EXPLODED_STATE
            self.continue_playing = False
            self.lost = True
            self.reveal_all()
            return False
            
        else:
            if clicked_cell.adjacent_mine_count == 0:
                
                # Click all of the adjacent cells as well 
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            self.click_cell(nr, nc)
                            
        return True     
    
                    
    def update_adjacent_cells(self, row: int, col: int, is_mine: bool, clicked: bool, previously_determined: bool):
        """
        This function is called when a cell is determined to be a mine or safe
        
        There are two different ways a cell can be determined, either it is 
        determined because it is clicked, or it is determined because of our 
        probabilistic analysis. Either way, if we know a cell's state, then we 
        need to update the cells adjacent to it. Specifically, we need to 
        change the adjacent_undetermined_cell_count variable and possibly the
        adjacent_undetermined_mine_count as well if the determined cell is a 
        mine. 
        
        One slight difference between this function being called by a click,
        and it being called as a result of our analysis, is whether or not 
        the cells adjacent to it now have "some information." Note, we use 
        this variable to determine how we should render the cell to the 
        screen, i.e. should it be a blank cell or should it be a probability.
        If the cell is clicked, then all it's adjacent cells should not be 
        blank, and thus, we need to set the some_information bool true. 
        """
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    
                    adjacent_cell: Cell = self.board[nr][nc]
                    
                    # Edits information status of Cell and of 
                    # overall board counter 
                    if not adjacent_cell.some_information and clicked:
                        self.cells_with_no_information -= 1
                        adjacent_cell.some_information = True
                    
                    if is_mine and not previously_determined:
                        adjacent_cell.adjacent_undetermined_cell_count -= 1
                        adjacent_cell.adjacent_undetermined_mine_count -= 1
            
                    elif not is_mine and not previously_determined:
                        adjacent_cell.adjacent_undetermined_cell_count -= 1
                            
                        
    def update_probabilities(self, probabilities: Dict[str, float]):
        """
        Takes the dict from the solve function and updates the state of the 
        keys in the dictionary, as well as the cells adjacent to the keys
        
        """
        
        # Note, that keys in the dictionary will never be intially determined
        for cell_encoded_value in probabilities.keys():
            row, col = decode(cell_encoded_value, self.cols)

            
            cell = self.board[row][col]
            cell.probability = probabilities[cell_encoded_value]
            
            if probabilities[cell_encoded_value] == 0.0:
                cell.determined = True
                self.update_adjacent_cells(row, col, False, False, False)
                
            elif probabilities[cell_encoded_value] == 1.0:
                cell.determined = True
                self.undetermined_mine_count -= 1
                self.update_adjacent_cells(row, col, True, False, False)
             
                
    def generate_rules(self):
        """
        Generates the rules for the current state of the game
        
        A cell only generates a rule, if it is a non_mine cell, and it is 
        revealed, i.e. it has been clicked by the user. In this case, it 
        will have a certain number of mines around it, and this must hold, 
        creating an axiom for our game. If all the cells around it are also 
        determined, then we will not create a rule, as there is no point, as 
        we already know everything around the cell. However, if there are 
        some cells that are not determined adjacent to the cell, then these 
        will generate a rule. Note, that we do not use the adjacent_mine_count
        variable for the mine count, we instead use the adjacent_undetermined_mine_count
        varibale, as this limits the amount of redundant computation we need 
        to do. Since we are only considering the undetermined mines, then we 
        also need to only consider the undetermined cells, which is why we check 
        to see if a cell is undetermined before adding it to the list which will 
        ultimately make the rule. 
        
        """
        
        rules: List[Rule] = []
        
        for row in range(self.rows):
            for col in range(self.cols):
                cell: Cell = self.board[row][col]
                
                if cell.revealed and not cell.is_mine:
                    
                    adjacent_undetermined_cells: List[str] = []
                    
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                
                                adjacent_cell: Cell = self.board[nr][nc]
                                if not adjacent_cell.determined:
                                    adjacent_undetermined_cells.append(adjacent_cell.encoded_value)
                                    
                    # There are some cells around the revealed cell that are not yet determined, meaning 
                    # that we have a rule
                    if adjacent_undetermined_cells:
                        rules.append(Rule(cell.adjacent_undetermined_mine_count, adjacent_undetermined_cells))
                        
        return rules
                                                        
            
    def play_game(self):
        first_row, first_col = self.get_first_guess()
        self.place_mines_safe(first_row, first_col)
        self.count_board_adjacent_mines_and_cells()
        self.click_cell(first_row, first_col)
        rules: List[Rule] = self.generate_rules()
        
        print(f"initial unreduced rules: {rules}")
        ms = MinesweeperSolver(rules, self.undetermined_mine_count, self.cells_with_no_information)
        probabilities: Dict[str, float] = ms.solve()
        self.update_probabilities(probabilities)
        
        self.print_board()
                
        while True:
            row, col = self.get_valid_coordinates()
            self.click_cell(row, col)
            
            # Breaks out of the loop if we lose or win
            if not self.continue_playing:
                break
            
            rules: List[Rule] = self.generate_rules()
            ms = MinesweeperSolver(rules, self.undetermined_mine_count, self.cells_with_no_information)
            probabilities: Dict[str, float] = ms.solve()
            self.update_probabilities(probabilities)

            self.print_board()
            
        self.print_board()
        self.determine_outcome()
            
            
