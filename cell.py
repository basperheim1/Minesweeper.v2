from util import encode, decode 


class GameStrings:
    MINE = '💣'
    FLAG = '🚩'
    UNREVEALED = '■'
    EMPTY = ' '
    COVERED_STATE = "covered"
    EXPLODED_STATE = "exploded"
    


class Cell:
    def __init__(self, row: int, column: int, num_columns: int, is_mine: bool = False):
        self.is_mine = is_mine
        self.revealed = False
        self.flagged = False
        
        # Determined is any of the 3 following states:
        # Uncovered, covered (100% mine), covered (0% mine)
        self.determined = False
        
        self.some_information = False 
        self.adjacent_mine_count = 0
        self.adjacent_cell_count = 0
        self.adjacent_undetermined_mine_count = 0
        self.adjacent_undetermined_cell_count = 0
        self.state = GameStrings.COVERED_STATE
        self.row = row 
        self.column = column 
        self.num_columns = num_columns
        self.encoded_value = encode(row, column, num_columns)
        self.probability = 0

        
    def change_state(self, new_state: str):
        self.state = new_state

    def __repr__(self):
        if self.revealed:
            if self.is_mine:
                return "[ M ]"
            
            else:
                return f"[ {self.adjacent_mine_count} ]"
            
        else:
            
            # We have some probability associated with the value
            if self.some_information:
                if self.probability == 0.0:
                    return "[00%]"
                
                elif self.probability == 1.0:
                    return "[ M ]"
                
                else: 
                    return f"[{int(self.probability*100)}%]"
            
            else:
                return '[   ]'