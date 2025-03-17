from typing import Tuple, List, Dict, Set
from math import comb

class Rule():
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
        self.num_mines: int = num_mines
        self.cells: List[str] = cells
        
class Frontier():
    """
    A frontier represents a collection of covered adjacent tiles with 
    some given information
    
    For example, consider the following board state that we might have:
    
    123E F123L
    ABCD GHIJK 
    
    In this case, there are a total of two frontiers in the current state 
    of our board. This is because the groups 'A' - 'E' and 'F' - 'L' are 
    both collections of covered adjacent cells with some given information. 
    We can also see that the possible configurations of mines within the 
    groups are independent of one another, i.e. if there was a mine in the
    first frontier, perhaps at C, then this would tell us nothing about the 
    possible configurations of mines in the second frontier. Due to this reason,
    we split our rules into frontiers, as we can vastly reduce redundant 
    computation by not taking these independent frontiers into account. Let X 
    be the time it takes to permute through the first frontier, and let Y be the 
    time it takes to permute through the second frontier; with our treatment of 
    these frontiers as independent, our time complexity is roughly X + Y, however, 
    if we did not treat them as independent, then our time compelxity would be XY 
    """
    
    def __init__(self, rule: Rule=None):
        self.cells: Set[str] = {}
        self.rules: List[Rule] = []
        
        # Dictionary to allow lookup of all rules for a given cell
        self.rule_lookup = Dict[str: List[Rule]]
        
        # If the frontier is initialized with a rule, then add 
        # all the cells in that rule to the frontier 
        if rule:
            for cell in rule.cells:
                self.cells.add(cell)
                self.rule_lookup[cell] = rule
                
            
                
        self.rules.append(rule)

        
    def add_rule(self, rule: Rule):
        for cell in rule.cells:
            self.cells.add(cell)
            
            
            if cell in self.rule_lookup:
                self.rule_lookup[cell].append(rule)
                
            else:
                self.rule_lookup[cell] = rule
                
            
        self.rules.append(rule)
        
    def union_frontiers(self, frontier: "Frontier") -> "Frontier":
        """
        Returns a new Frontier that is the union of this frontier and another.
        """
        new_frontier = Frontier()
        new_frontier.cells = self.cells | frontier.cells  # Union of sets
        new_frontier.rules = self.rules + frontier.rules
        new_frontier.rule_lookup = {**self.rule_lookup, **frontier.rule_lookup}
        return new_frontier  # Return a new merged frontier
    
    
    def determine_combinations(self) -> "FrontierCounts":
        """
        This function will determine the possible configurations of mines 
        within the frontier based on the rules given for the frontier. 
        
        
        The output of this function is a dictionary, with the integer 
        keys referring to the number of mines in some valid frontier 
        combination. The value is another dictionary, with the keys being 
        the string representation of the cells, and the value being the 
        number of times that cell occured in a valid combination of that 
        number of mines. 
        So for example, if our valid combinations of mines were as follows: 

        {'A', 'B' and 'C', 'C' and 'A'}, then our output would be as follows:

        {1: {'A': 1}, 2: {'A': 1, 'B': 1, 'C': 2}}
        """
        cells: List[str] = list(self.cells)
        
        # Make a lookup table so we can find exactly what index a 
        # given cell is at in our cells and mines lists 
        cell_lookup: Dict[str, int] = {}
        for i in range(len(cells)):
            cell_lookup[cells[i]] = i
            
        
        # Value will be true if mine, false otherwise
        mines: List[bool] = []
        counts: FrontierCounts = {}
        self._determine_combinations(cells, cell_lookup, mines, 0, True, counts)
        self._determine_combinations(cells, cell_lookup, mines, 0, False, counts)

        return counts
        
    # Recursive helper function
    def _determine_combinations(self, cells: List[str], cell_lookup: Dict[str, int], mines: List[bool], current_index: int, is_mine: bool, frontier_counts: "FrontierCounts"):
        
        cell = cells[current_index]
        
        # Base case
        if current_index == len(cells):
            
            frontier_counts.add_valid_combination(cells, mines)
            
            return 
           
        # Recursive case     
        # Ensure that the current list of mines we're working with is valid 
        # For this recursive step, we will only be looking at the first <index> + 1
        # elements of the mines list. For example, if our mines list is [T, T, F, F], 
        # but the index is 2, then we will only consider [T, T, F]. Next, we will consider 
        # all rules associated with the current cell we are looking at in the recurisve 
        # step. We will check to see if there are any logical inconsistencies with the 
        # current configuration of the board, and if so, we will return, which is this 
        # algorithms implementation of backtracking.         
        else:
            
            # Set the correct value in the mines list for the current recursive step 
            mines[current_index] = is_mine
            
            
            if is_mine:
                for rule in self.rule_lookup[cell]:
                    
                    # If we have seen more mines than are available 
                    # for the given rule, then the current branch 
                    # that we're looking at is logically infeasible
                    # and we should backtrack
                    num_mines_left = rule.num_mines -1
                    
                    for cell in rule.cells:
                        cell_index = cell_lookup[cell]
                        if cell_index < current_index and mines[cell_index]:
                            num_mines_left -= 1
                            
                    if num_mines_left < 0:
                        return 
            
            else:
                for rule in self.rule_lookup[cell]:
                    
                    # We need to ensure that we can add enough mines.
                    # We can look at the total number of mines we have 
                    # seen thus far, and then not including our current
                    # index, we can assume that the rest of the cells are 
                    # mines. If, even under this assumption, the number of 
                    # mines we have is less than the number of mines for 
                    # the given rule, then we will know that the current 
                    # branch is logically infeasible given the current 
                    # configuration of mines and we should backtrack 
                    
                    num_mines_left = rule.num_mines
                    
                    for cell in rule.cells:
                        cell_index = cell_lookup[cell]
                        if cell_index < current_index and mines[cell_index]:
                            num_mines_left -= 1
                            
                        elif cell_index > current_index:
                            num_mines_left -= 1
                            
                    if num_mines_left > 0:
                        return 
                    
        # We have made it out of the checks, and the current branch of our tree 
        # is viable, and we should continue. 
        
        self._determine_combinations(cells, cell_lookup, mines, current_index+1, True, frontier_counts)
        self._determine_combinations(cells, cell_lookup, mines, current_index+1, False, frontier_counts)
                        
            
class FrontierCounts():
    
    def __init__(self):
        self.counts = Dict[int, Dict[str, int]]   
        
    def add_valid_combination(self, cells: List[str], mines: List[bool]):
        number_of_mines: int = sum(mines)
            
        # Updates the counts in the count dict 
        if number_of_mines in self.counts.keys():
            for i in range(len(cells)):
                if mines[i]:  
                    if cells[i] in self.counts[number_of_mines].keys():
                        self.counts[number_of_mines][cells[i]] += 1
                        
                    else:
                        self.counts[number_of_mines][cells[i]] = 1   
                        
            self.counts[number_of_mines]["local_combinations"] += 1
            
        else:
            self.counts[number_of_mines] = {}
            for i in range(len(cells)):
                if mines[i]:
                    self.counts[number_of_mines][cells[i]] = 1
                    
            self.counts[number_of_mines]["local_combinations"] = 1
            self.counts[number_of_mines]["global_combinations"] = 0
                        
class MinesweeperSolver:
    def __init__(self, rules: List[Rule], num_mines_left: int, num_uninformed_cells: int):
        self.rules = rules 
        self.num_mines_left = num_mines_left
        self.num_uninformed_cells = num_uninformed_cells
        
        
    def generate_frontiers(self, rules: List[Rule]) -> List[Frontier]:
        frontiers: List[Frontier] = []
        
        for rule in rules:
            
            # We want to add the cells in our current rule to the cells in the 
            # appropriate frontier(s). There are three cases that can occur.
            #
            # 1) The cells in the rule are not in any of the frontiers. In this case,
            #    we will want to make a new frontier that contains the cells in the 
            #    current rule
            # 
            # 2) The cells in the rule are in one of the frontiers. In this case, we 
            #    will want to add the cells in the rule to the frontier's cells. 
            #
            # 3) The cells in the rule are in multiple frontiers. In this case, we will 
            #    merge the collection of frontiers, and then add the cells from the rule 
            #    to that new frontier.     
                
            # Find the indexes of the frontiers (if any) that contain at least one of 
            # the cells in the current rule 
            indexes = []
            for cell in rule.cells:
                for i in range(len(frontiers)):
                    if cell in frontiers[i].cells:
                        indexes.append(i)
                        
            # (Case 1) The cells in the current rule were not in any of the frontiers   
            if not indexes:
                frontiers.append(Frontier(rule))
                
            # (Case 2) The cells in the current rule are in exactly one of the frontiers 
            elif len(indexes) == 1:
                frontiers[indexes[0]].add_rule(rule)
                
            # (Case 3) The cells in the current rule are in more than one of the frontiers 
            else:
                
                # Create a new frontier which is the union of the frontiers that contain at 
                # least one cell in the rule 
                new_frontier = frontiers[indexes[0]]
                for i in range(1, len(indexes)):
                    new_frontier = frontiers[indexes[i]].union_frontiers(new_frontier)
                    
                new_frontier.add_rule(rule)
                
                # Remove the frontiers from the list of frontiers that were used to create 
                # new_frontier  
                for index in reversed(indexes):
                    del frontiers[index]
                    
                frontiers.append(new_frontier)
                
    def generate_frontiers_counts(frontiers: List[Frontier]) -> List[FrontierCounts]:
        
        frontiers_counts: List[FrontierCounts] = []
        for frontier in frontiers:
            frontiers_counts.append(frontier.determine_combinations())
            
        return frontiers_counts

    def generate_global_counts(self, frontiers_counts: List[FrontierCounts], num_mines_left: int, num_uninformed_cells: int) -> int:
        
        total_combinations_count = 0 
        frontiers_indexes = [0]*len(frontiers_counts)
        
        # Determines how many unique parities there are in each frontier's possible combinations 
        termination_indexes = [len(i.counts.keys())-1 for i in frontiers_counts]
        
        while True: 
            
            global_count = 1
            mine_count = 0
            for i in range(len(frontiers_counts)):
                
                # The key is the number of mines for all combinations in the associated value
                key = list(frontiers_counts[i].counts.keys())[frontiers_indexes[i]]
                global_count *= frontiers_counts[i].counts[key]["local_combinations"]
                mine_count += key
                
            if mine_count <= num_mines_left:
                global_count*comb(num_uninformed_cells, num_mines_left-mine_count)
                total_different_combinations += global_count
                
                for i in range(len(frontiers_counts)):
                    key = list(frontiers_counts[i].counts.keys())[frontiers_indexes[i]]
                    frontiers_counts[i].counts[key]["global_combinations"] += global_count
                
                
            
            if frontiers_indexes == termination_indexes:
                break
            
            # TODO: Add comment, doing this on no sleep, hard to explain what I'm doing
            # pretty sure it's right tho 
            for i in range(len(frontiers_counts)):
                if frontiers_indexes[i] == len(frontiers_counts[i].keys()) - 1:
                    frontiers_indexes[i] = 0
                    
                else:
                    frontiers_indexes[i] += 1
                    break
                
        return total_combinations_count
                
            
    def generate_frequencies(self, frontiers_counts: List[FrontierCounts], total_combination_count: int):
        
        counts: Dict[str, float] = {}
        
        # TODO: Add comments 
        for frontier in frontiers_counts:
            for num_mines in frontier.counts.keys():
                for cell in frontier.counts[num_mines].keys():
                    if cell not in counts:
                        counts[cell] = frontier.counts[num_mines]["local_combinations"]*(frontier.counts[num_mines][cell] / frontier.counts[num_mines]["local_combinations"])
                        
                    else:
                        counts[cell] += frontier.counts[num_mines]["local_combinations"]*(frontier.counts[num_mines][cell] / frontier.counts[num_mines]["local_combinations"])
                        
        frequencies: Dict[str, float] = {}
        
        for cell in counts.keys():
            frequencies[cell] = counts[cell] / total_combination_count
            
        return frequencies
                            

    def solve(self) -> Dict[str, float]:
        
        frontiers: List[Frontier] = self.generate_frontiers(self.rules)
        frontiers_counts: List[FrontierCounts] = self.generate_frontiers_counts(frontiers)
        total_combinations_count = self.generate_global_counts(frontiers_counts, self.num_mines_left, self.num_uninformed_cells)
        frequencies: Dict[str, float] = self.generate_frequencies(frontiers_counts, total_combinations_count)
        
        return frequencies