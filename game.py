from board import MinesweeperBoard
from timekeeper import TimeKeeper

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
            
        
def game(ai_player: bool = True, num_iterations: int =1, return_stats: bool = False, difficulty: str = "b"):
    amassed_risk = 0    
    times_won = 0
    
    time_keeper = TimeKeeper()
    
    for i in range(num_iterations):
        # rows, cols, mine_count = get_board_settings()
        
        if difficulty == "b":
            board = MinesweeperBoard(9, 9, 10)
            
        elif difficulty == "i":
            board = MinesweeperBoard(16, 16, 40)
            
        elif difficulty == "e":
            board = MinesweeperBoard(16, 30, 99)
            
        else:
            board = MinesweeperBoard(24, 30, 200)    
        
        if ai_player:
            won, times = board.play_game_ai()
        else:
            won, times = board.play_game()
            
        if won:
            times_won += 1
            
        time_keeper.merge(times)
        amassed_risk += board.amassed_risk
        
    if return_stats:
        print(f"total amassed risk: {amassed_risk / (num_iterations-times_won)}")
        print(f"win rate: {times_won / num_iterations}")
        print(f"times: {time_keeper}")
    
game(True, 1000, True, "iasdf")