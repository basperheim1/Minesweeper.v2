from typing import List
from typing import FrozenSet

class NewRule():
    """
    A class that represents a single axiom in our board 
    
    Each rule will represent the information given by a revealed
    tile in our board. For example, consider the following
    state of our board:
    
    1A
    BC
    
    Then in this case, the rule that refers to the single uncovered 
    tile, is as follows Rule(1, ['A', 'B', 'C']). This states 
    that of the three tiles, 'A', 'B', and 'C', that only one 
    of those will be a mine. 
    """
    def __init__(self, num_mines: int, cells: List[str]):
        self.num_undetermined_mines: int = num_mines
        self.undetermined_cells: FrozenSet[str] = frozenset(cells)
        
    def __repr__(self):
        return f"{self.num_undetermined_mines}: {self.undetermined_cells}"
        
    # Overwritten function to test for equality of rules.
    # Written as there is no point adding a duplicate rule 
    # to the list of rules. 
    def __eq__(self, other):
        if not isinstance(other, NewRule):
            return False
        return self.num_undetermined_mines == other.num_undetermined_mines and set(self.undetermined_cells) == set(other.undetermined_cells)
    
    def __hash__(self):
        return hash((self.num_undetermined_mines, self.undetermined_cells))