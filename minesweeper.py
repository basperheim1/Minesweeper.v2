from typing import Tuple, List, Dict, Set, Deque
from math import comb

from collections import deque
from rule import Rule



    
class RuleReducer():
    """
    Class that reduces rule set to set of rules that cannot be trivially solved
    
    Some rules, are trivial, and should not be used to populate our frontiers 
    down the line. For example, if the number of undetermined mines for some 
    cell is equal to the number of undetermined cells adjacent to that cell, then 
    every undetermined adjacent cell is a mine. 
    
    Likewise, if the number of undetermined mines for some cell is zero, then 
    each undetermined cell adjacent to that cell is safe. 
    """
    def __init__(self):
        self.rules: List[Rule] = set()
        self.rule_lookup: Dict[str, Set[Rule]] = {}
        self.mines: List[str] = []
        self.safes: List[str] = []
        
    def add_rules(self, rules: List[Rule]):
        for rule in rules:
            self.add_rule(rule)
        
    def add_rule(self, rule: Rule):
        
        # Don't add duplicate rules to the list of rules
        if rule in self.rules:
            return
        
        self.rules.add(rule)
        for cell in rule.undetermined_cells:
            if cell not in self.rule_lookup:
                self.rule_lookup[cell] = set()
                
            self.rule_lookup[cell].add(rule)
            
    def reduce_rules(self):
        queue: Deque[Rule] = deque()
        
        # Add all the rules to the queue 
        for rule in self.rules:
            queue.append(rule)
            
        while queue:
            current_rule = queue.popleft()
            
            # Possible rule is in the queue but was already removed, in this 
            # case, we want to ignore the rule 
            print(f"current rule: {current_rule}")
            print(f"rules: {self.rules}")
            if current_rule in self.rules:
                print("IN RULES")

                # Any rule that was modified by the current rule should be added to the queue 
                # to see if it can be removed 
                rules_to_be_added: Set[Rule] = set()
                
                # All the undetermined cells in this rule must be mines 
                if current_rule.num_undetermined_mines == len(current_rule.undetermined_cells):
                    
                    self.rules.remove(current_rule)
                    for cell in current_rule.undetermined_cells:
                        
                        # add them to mine list 
                        self.mines.append(cell)
                        
                        # Decrement the # of undetermined_mines for all rules that contain this cell,
                        # also remove the cell itself from the list of undetermined_cells 
                        for rule in self.rule_lookup[cell]:
                            
                            # Create a new rule and add it to the lookup table 
                            # new_undetermined_cells = rule.undetermined_cells()
                            # new_undetermined_cells.remove(cell)
                            # new_rule: Rule = Rule(rule.num_undetermined_mines - 1, new_undetermined_cells)
                            
                            # self.rule_lookup[]
                            rule.num_undetermined_mines -= 1
                            rule.undetermined_cells.remove(cell)
                            rules_to_be_added.add(rule)
                            
                        # remove the cell from the rule_lookup table
                        del self.rule_lookup[cell]
                    
                # All the undetrmined cells in this rule must be safes        
                elif current_rule.num_undetermined_mines == 0:
                    
                    self.rules.remove(current_rule)
                    for cell in current_rule.undetermined_cells:
                        
                        # Add them to the safe list 
                        self.safes.append(cell)
                        
                        # For all rules that contain this cell, remove the cell from the list of 
                        # undetermined_cells
                        for rule in self.rule_lookup[cell]:
                            rule.undetermined_cells.remove(cell)
                            rules_to_be_added.add(rule)
                            
                    # remove the cell from the rule_lookup table
                        del self.rule_lookup[cell]
                            
                for rule in rules_to_be_added:
                    queue.append(rule)   
                    print(rule)
        
        
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
        self.cells: Set[str] = set()
        self.rules: Set[Rule] = set()
        
        # Dictionary to allow lookup of all rules for a given cell
        self.rule_lookup: Dict[str: Set[Rule]] = {}
        
        # If the frontier is initialized with a rule, then add 
        # all the cells in that rule to the frontier 
        if rule:
            for cell in rule.undetermined_cells:
                self.cells.add(cell)
                
                if cell not in self.rule_lookup:
                    self.rule_lookup[cell] = set()
                    
                self.rule_lookup[cell].add(rule)
                
            
                
        self.rules.add(rule)

        
    def add_rule(self, rule: Rule):
        for cell in rule.undetermined_cells:
            self.cells.add(cell)
            
            
            if cell in self.rule_lookup:
                self.rule_lookup[cell].add(rule)
                
            else:
                self.rule_lookup[cell] = set([rule])
                
            
        self.rules.add(rule)
        
    def union_frontiers(self, frontier: "Frontier") -> "Frontier":
        """
        Returns a new Frontier that is the union of this frontier and another.
        """
        new_frontier = Frontier()
        new_frontier.cells = self.cells | frontier.cells  # Union of sets
        new_frontier.rules = self.rules | frontier.rules
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
        mines: List[bool] = [False]*len(cells)
        counts: FrontierCounts = FrontierCounts()
        self._determine_combinations(cells, cell_lookup, mines, 0, True, counts)
        self._determine_combinations(cells, cell_lookup, mines, 0, False, counts)

        return counts
        
    # Recursive helper function
    def _determine_combinations(self, cells: List[str], cell_lookup: Dict[str, int], mines: List[bool], current_index: int, is_mine: bool, frontier_counts: "FrontierCounts"):
        
        
        # Base case
        if current_index == len(cells):
            
            # Only add the combination in the is_mine branch, note that 
            # If a combination is valid, it will call _determine_combinations 
            # twice, and we only want to add the combination once 
            if is_mine:
                frontier_counts.add_valid_combination(cells, mines)
            
            return 
        
        cell = cells[current_index]

           
        # Recursive case     
        # Ensure that the current list of mines we're working with is valid 
        # For this recursive step, we will only be looking at the first <index> + 1
        # elements of the mines list. For example, if our mines list is [T, T, F, F], 
        # but the index is 2, then we will only consider [T, T, F]. Next, we will consider 
        # all rules associated with the current cell we are looking at in the recurisve 
        # step. We will check to see if there are any logical inconsistencies with the 
        # current configuration of the board, and if so, we will return, which is this 
        # algorithms implementation of backtracking.         
            
        # Set the correct value in the mines list for the current recursive step 
        mines[current_index] = is_mine
                
        
        if is_mine:
            for rule in self.rule_lookup[cell]:
                
                # If we have seen more mines than are available 
                # for the given rule, then the current branch 
                # that we're looking at is logically infeasible
                # and we should backtrack
                num_mines_left = rule.num_undetermined_mines - 1
                
                for cell in rule.undetermined_cells:
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
                
                num_mines_left = rule.num_undetermined_mines
                
                for cell in rule.undetermined_cells:
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
        
    def __repr__(self):
        return f"{self.rules}"
                        
            
class FrontierCounts():
    
    def __init__(self):
        self.counts: Dict[int, Dict[str, int]] = {} 
        
    def add_valid_combination(self, cells: List[str], mines: List[bool]):
        number_of_mines: int = sum(mines)
            
        # Updates the counts in the count dict 
        if number_of_mines in self.counts:
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
            
    def __repr__(self):
        return f"{self.counts}"
                        
class MinesweeperSolver:
    def __init__(self, rules: List[Rule], num_mines_left: int, num_uninformed_cells: int):
        self.rules = rules 
        self.num_mines_left = num_mines_left
        self.num_uninformed_cells = num_uninformed_cells
        self.mines: List[str] = []
        self.safes: List[str] = []
        
        
    def generate_frontiers(self) -> List[Frontier]:
        frontiers: List[Frontier] = []
        
        for rule in self.rules:
            
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
            indexes = set()
            for cell in rule.undetermined_cells:
                for i in range(len(frontiers)):
                    if cell in frontiers[i].cells:
                        indexes.add(i)
                        
            indexes = list(indexes)
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
                
                indexes.sort(reverse=True)
                # Remove the frontiers from the list of frontiers that were used to create 
                # new_frontier  
                for index in indexes:
                    # print(f"index: {index}")
                    # print(f"frontiers: {frontiers}")
                    del frontiers[index]
                    
                frontiers.append(new_frontier)
                
        return frontiers
                
    def generate_frontiers_counts(self, frontiers: List[Frontier]) -> List[FrontierCounts]:
        
        frontiers_counts: List[FrontierCounts] = []
        for frontier in frontiers:
            frontiers_counts.append(frontier.determine_combinations())
            
        return frontiers_counts

    def generate_global_counts(self, frontiers_counts: List[FrontierCounts]) -> int:
        
        total_combinations_count = 0 
        frontiers_indexes = [0]*len(frontiers_counts)
        num_mines_left = self.num_mines_left
        num_uninformed_cells = self.num_uninformed_cells
        
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
                global_count *= comb(num_uninformed_cells, num_mines_left-mine_count)
                total_combinations_count += global_count
                
                for i in range(len(frontiers_counts)):
                    key = list(frontiers_counts[i].counts.keys())[frontiers_indexes[i]]
                    frontiers_counts[i].counts[key]["global_combinations"] += global_count
                
                
            
            if frontiers_indexes == termination_indexes:
                break
            
            # TODO: Add comment, doing this on no sleep, hard to explain what I'm doing
            # pretty sure it's right tho 
            for i in range(len(frontiers_counts)):
                if frontiers_indexes[i] == len(frontiers_counts[i].counts.keys()) - 1:
                    frontiers_indexes[i] = 0
                    
                else:
                    frontiers_indexes[i] += 1
                    break
                
        return total_combinations_count
                
            
    def generate_frequencies(self, frontiers_counts: List[FrontierCounts], total_combination_count: int):
        
        # Counts will be a dictionary representing the number of combinations associated 
        # with each cell that is in a reduced rule 
        counts: Dict[str, float] = {}
        
        # TODO: Add comments 
        for frontier in frontiers_counts:
            for num_mines in frontier.counts.keys():
                for cell in frontier.counts[num_mines].keys():
                    if cell == "local_combinations" or cell == "global_combinations":
                        continue
                    
                    fraction_of_frontier_parity_with_cell: float = frontier.counts[num_mines][cell] / frontier.counts[num_mines]["local_combinations"]
                    if cell not in counts:
                        counts[cell] = fraction_of_frontier_parity_with_cell*frontier.counts[num_mines]["global_combinations"]
                        
                    else:
                        counts[cell] += fraction_of_frontier_parity_with_cell*frontier.counts[num_mines]["global_combinations"]
                        
        frequencies: Dict[str, float] = {}
        
        for cell in counts.keys():
            frequencies[cell] = counts[cell] / total_combination_count
            
        for mine in self.mines:
            frequencies[mine] = 1
        
        for safe in self.safes:
            frequencies[safe] = 0
            
        return frequencies
    
    def reduce_rules(self):
        rr: RuleReducer = RuleReducer()
        rr.add_rules(self.rules)
        rr.reduce_rules()
        
        self.mines = rr.mines
        self.num_mines_left -= len(rr.mines)
        self.safes = rr.safes
        self.rules = rr.rules
                                    

    def solve(self) -> Dict[str, float]:
        
        print(f"rules: {self.rules}")
        self.reduce_rules()
        print(f"reduced rules: {self.rules}")
        frontiers: List[Frontier] = self.generate_frontiers()
        print(f"frontiers: {frontiers}")
        frontiers_counts: List[FrontierCounts] = self.generate_frontiers_counts(frontiers)
        print(f"frontiers counts: {frontiers_counts}")
        total_combinations_count = self.generate_global_counts(frontiers_counts)
        print(f"total combinations count: {total_combinations_count}")
        frequencies: Dict[str, float] = self.generate_frequencies(frontiers_counts, total_combinations_count)
        print(f"frequencies: {frequencies}")
        
        return frequencies