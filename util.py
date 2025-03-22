from typing import Tuple, List
from rule import Rule

def encode(row: int, column: int, num_columns: int) -> str:
    """
    Encode some position on the board to a string 
    
    The encode function uses a tile's row and column, as well as 
    the number of columns in the board to determine what string 
    should represent the tile. Note, that the encoder uses a base 
    26 encoding scheme; this means that A = 0, ..., Z = 25, BA = 26, 
    BZ = 51, etc. 
    """
    id = ""
    idx = row*num_columns + column
        
    if idx == 0:
        return "a"
    
    while (idx != 0):
        remainder = idx % 26
        id += chr(remainder + ord('a'))
        idx //= 26
        
    return id[::-1]
    

def decode(encoded_value: str, num_columns: int) -> Tuple[int, int]:
    """
    Decodes a base-26 string back into (row, column).
    """
    index = 0
    for char in encoded_value:
        index = index *26 + (ord(char) - ord('a'))
    row = index // num_columns
    col = index % num_columns

    return row, col

def decode_int(encoded_value: str, num_columns: int) -> Tuple[int, int]:
    """
    Decodes a base-26 string back into (row, column).
    """
    index = 0
    for char in encoded_value:
        index = index *26 + (ord(char) - ord('a'))
        
    return index


def transform_board_to_ruleset(board: List[List[int]], num_mines: int) -> List[Rule]:
    """
    A function that generates the axiomatic rules for the current state of a board 
    
    Note, that a cell can fall into any one of the following 5 cases:
    
    1) Uncovered Cell: These are the cells that end up generating the ruleset 
       for our board.
        
    2) Frontier Cell (undetermined): These are the cells that are covered and adjacent to
       an uncovered cell, and their state is undetermined, i.e. before doing any heavy 
       checks, they could be a mine, or they could be safe. 
       
    3) Mine Frontier Cell (determined, mine): These are the cells that are covered and adjacent to 
       an uncovered cell, but their state is determined. i.e. although covered, based on the 
       information given by some uncovered cell, we can determine that the cell is a mine. For 
       example, if we had an uncovered cell that was an 8, then we could determine that every 
       mine around it is a mine frontier cell, as although covered, it must be a mine 
       
    4) Safe Frontier Cell (determined, safe): These are the cells that are covered and adjacent to 
       an uncovered cell, but their state is determined. i.e. although covered, based on the 
       information given by some uncovered cell, we can determine that the cell is safe. For example,
       consider if we had an uncovered cell that was a 1, and we knew there was a mine in the top left 
       corner, then we could determine that every mine around it is a safe frontier cell, as although 
       covered, it must be safe. 
       
    5) Uninformed Cell: These are the cells that are not adjacent to any uncovered cell. We essentially 
       have no information on what these cells are, besides looking at global counts, and thus, we call
       these cells uninformed cells. 
       
    Initially, each cell will start out as 1, 2, or 5. Note, that if we are in state 1 or 5, then our 
    state cannot change. However, our goal will be to convert as many 2s as we can into 3s and 4s. To 
    do this, we will add all of our uncovered cells to a queue. We will then iterate through them, and 
    determine if we can turn the #2 type cells into #3s and #4s. To do this, for each #1 cell, we will 
    look at it's value, and we will check to see how many #2 cells are around it. If the number of #2 
    cells around it is equal to it's value, then all the cells around it must be #3 cells. Additionally,
    we will also look at the number of #3 cells around the #1 cell, and if they are equal, then each #2 
    cell around the #1 cell must be a #4 cell. Note, that we do not actually use the value of the #1 cell,
    instead we use the value of the #1 cell minus the number of #2 cells around the #1 cell, to determine 
    the number of mines left to be seen in the #2 cells around the #1 cell. If we change a #2 cell to a #3 
    or a #4 cell, then we need to add any #1 cells adjacent to that changed #2 cell to the queue, as we 
    have new information, possibly making it so that new cell can determine more of the #2 cells around it
    """
    
    
    pass