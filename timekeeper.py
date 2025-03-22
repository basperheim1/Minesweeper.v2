from typing import Dict

class TimeKeeper():
    
    def __init__(self):
        self.times: Dict[str, float] = {}
        self.times["determine_cells"] = 0
        self.times["reduce_rules"] = 0
        self.times["generate_frontiers"] = 0
        self.times["generate_frontiers_counts"] = 0
        self.times["generate_global_counts"] = 0
        self.times["generate_frequencies"] = 0
        
    def increment_times(self, func: str, time: float):
        self.times[func] += time
        
    def merge(self, other: "TimeKeeper"):
        for key in other.times:
            self.times[key] += other.times[key]
            
    def __repr__(self):
        return str(self.times)