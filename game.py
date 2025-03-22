from board import MinesweeperBoard

def get_board_settings(max_rows=24, max_cols=30):
    while True:
        try:
            user_input = input(f"Enter board size as 'rows columns' (max {max_rows} rows, {max_cols} columns): ")
            row_str, col_str = user_input.strip().split()
            rows, cols = int(row_str), int(col_str)

            if not (1 <= rows <= max_rows and 1 <= cols <= max_cols):
                print(f"Invalid size. Rows must be 1 to {max_rows}, columns must be 1 to {max_cols}. Try again.")
                continue

            max_mines = rows * cols - 1  # Leave space for at least one safe cell
            mine_input = input(f"Enter number of mines (1 to {max_mines}): ")
            num_mines = int(mine_input)

            if not (1 <= num_mines <= max_mines):
                print(f"Invalid mine count. Must be between 1 and {max_mines}. Try again.")
                continue

            return rows, cols, num_mines

        except ValueError:
            print("Invalid input. Please enter numbers only, separated by spaces.")
            
        
def game():
    amassed_risk = 0
    num_iterations = 50
    
    times_won = 0
    
    for i in range(num_iterations):
        # rows, cols, mine_count = get_board_settings()
        board = MinesweeperBoard(16, 30, 99)
        won =board.play_game_ai()
        if won:
            times_won += 1
        amassed_risk += board.amassed_risk
        
    print(f"total amassed risk: {amassed_risk / num_iterations-times_won}")
    print(f"win rate: {times_won / num_iterations}")
    
game()