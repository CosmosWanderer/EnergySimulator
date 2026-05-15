import json
import math
import argparse
from itertools import combinations

class Generator:
    def __repr__(self):
        return self.name
    def __init__(self, name : str, gen_type : str, cost : float, output):
        self.name = name
        self.type = gen_type
        self.cost = cost
        if gen_type == "constant":
            self.output = [output] * 24
        elif gen_type == "variable":
            if len(output) != 24:
                raise ValueError(f"Generator {name}: wrong amount of values for 'output': {len(output)}")
            self.output = output
        else:
            raise ValueError(f"Unknown generator type: {gen_type}")

class Consumer:
    def __repr__(self):
        return self.name
    def __init__(self, name : str, demand : list):
        self.name = name
        if len(demand) != 24:
            raise ValueError(f"Consumer {name}: wrong amount of values for 'demand': {len(demand)}")
        self.demand = demand

class DataPerHour:
    def __init__(self):
        self.anybody_served = False
        self.used_gens = []
        self.consumers_served = []
        self.optimal_cost = 0.0
        self.max_output = 0.0
        self.full_demand = 0.0
        self.minimal_demand = 0.0
        self.consumers_not_served = []
        
class Simulator:
    def __init__(self):
        self.consumers = []
        self.generators = []
        self.testname = ""
        
    def simulate(self, testname : str, method="brute") -> list:
        self.method = method
        self.testname = testname
        self.parse_info()
        all_data = []
        for hour in range(24):
            all_data.append(self.simulate_hour(hour))
        return all_data
   
    def parse_info(self):
        self.consumers.clear()
        self.generators.clear()
        
        with open(self.testname, "r", encoding="utf-8") as f:
            data = json.load(f) 
            
        for gen in data["generators"]:
            name = gen["name"]
            gen_type = gen["gen_type"]
            cost = gen["cost"]
            output = gen["output"]
            self.generators.append(Generator(name, gen_type, cost, output))
        
        for cons in data["consumers"]:
            name = cons["name"]
            demand = cons["demand"]
            self.consumers.append(Consumer(name, demand))
            
    def simulate_hour(self, h : int):
        hour_data = DataPerHour()
        
        max_output = 0.0
        for gen in self.generators:
            max_output += gen.output[h]
        
        consumers_sorted = sorted(self.consumers, key=lambda c: c.demand[h])
        consumers_sorted = [c for c in consumers_sorted if c.demand[h] != 0]
        
        if not consumers_sorted:
            return hour_data
        
        consumers_served = []
        hour_demand = 0.0
        for consumer in consumers_sorted:
            if hour_demand + consumer.demand[h] <= max_output:
                consumers_served.append(consumer)
                hour_demand += consumer.demand[h]
            else:
                continue
        
        if not consumers_served:
            return hour_data
                
        hour_data = self.select_generators(h, hour_demand)
        hour_data.minimal_demand = consumers_sorted[0].demand[h]
        hour_data.max_output = max_output
        hour_data.full_demand = sum(c.demand[h] for c in consumers_sorted)
        hour_data.consumers_served = consumers_served
        hour_data.consumers_not_served = [c for c in consumers_sorted if c not in consumers_served]
    
        return hour_data

    def select_generators_brute(self, h: int, energy_needed: float) -> DataPerHour:
        hour_data = DataPerHour()
        best_cost = float('inf')  
        best_subset = []          
        
        for r in range(1, len(self.generators) + 1):
            for subset in combinations(self.generators, r):
                total_output = sum(g.output[h] for g in subset)
                total_cost = sum(g.output[h] * g.cost for g in subset)
                
                if total_output >= energy_needed and total_cost < best_cost:
                    best_cost = total_cost
                    best_subset = list(subset)

        hour_data.optimal_cost = best_cost
        hour_data.used_gens = best_subset
        hour_data.anybody_served = len(best_subset) > 0
        return hour_data  

    def select_generators_dp(self, h: int, energy_needed: float) -> DataPerHour:
        hour_data = DataPerHour()
        
        SCALE = 10
        
        outputs = [round(g.output[h] * SCALE) for g in self.generators]
        costs = [g.output[h] * g.cost for g in self.generators]
        target = math.ceil(energy_needed * SCALE)
        
        max_total = sum(outputs)
        
        INF = float('inf')
        dp = [INF] * (max_total + 1)
        dp[0] = 0.0
        
        chosen = [[] for _ in range(max_total + 1)]
        
        for i, gen in enumerate(self.generators):
            for j in range(max_total, outputs[i] - 1, -1):
                new_cost = dp[j - outputs[i]] + costs[i]
                if new_cost < dp[j]:
                    dp[j] = new_cost
                    chosen[j] = chosen[j - outputs[i]] + [gen]
        
        best_cost = INF
        best_gens = []
        for j in range(target, max_total + 1):
            if dp[j] < best_cost:
                best_cost = dp[j]
                best_gens = chosen[j]
                
        hour_data.optimal_cost = best_cost
        hour_data.used_gens = best_gens
        hour_data.anybody_served = len(best_gens) > 0
        return hour_data  

    def select_generators(self, h: int, energy_needed: float) -> DataPerHour:
        if self.method == "brute":
            return self.select_generators_brute(h, energy_needed)
        else:
            return self.select_generators_dp(h, energy_needed)
        
    def show_results(self, data : list[DataPerHour]) -> None:
        for h, hour_data in enumerate(data):
            print(f"Hour {h} ---------------------------------")
            if (hour_data.anybody_served):
                print(f"Full demand: {hour_data.full_demand}, max possible output: {hour_data.max_output}")
                print(f"Consumers served: {hour_data.consumers_served}")
                print(f"Generators used: {hour_data.used_gens}")
                print(f"Optimal cost: {hour_data.optimal_cost}")
                print(f"Consumers left: {hour_data.consumers_not_served}")
            elif (hour_data.full_demand > 0):
                print(f"Full demand: {hour_data.full_demand}, max possible output: {hour_data.max_output}")
                print(f"Minimal demand ({hour_data.minimal_demand}) > max possible output ({hour_data.max_output}) ")
                print(f"Consumers left: {hour_data.consumers_not_served}")
            else:
                print(f"Full demand: {hour_data.full_demand}, max possible output: {hour_data.max_output}")
                print(f"No demand")
            print("-----------------------------------------")
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Energy Grid Simulator")
    parser.add_argument("testfile", help="Path to test JSON file")
    parser.add_argument("--method", choices=["brute", "dp"], default="brute", help="Algorithm for generator selection")
    args = parser.parse_args()

    sim = Simulator()
    all_data = sim.simulate(args.testfile, args.method)
    sim.show_results(all_data)
