import json
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
        if gen_type == "variable":
            self.output = output

class Consumer:
    def __repr__(self):
        return self.name
    def __init__(self, name : str, demand : list):
        self.name = name
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
        
        

# Парсер для загрузки тестов
class Simulator:
    def __init__(self):
        self.consumers = []
        self.generators = []
        self.testname = ""
        
    def simulate(self, testname : str) -> list:
        self.testname = testname
        self.parse_info()
        all_data = []
        for hour in range(24):
            all_data.append(self.simulate_hour(hour))
        return all_data
   
    def parse_info(self):
        self.consumers.clear()
        self.generators.clear()
        
        with open(f"tests/{self.testname}", "r", encoding="utf-8") as f:
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
        
        # Максимальное кол-во энергии
        max_output = 0.0
        for gen in self.generators:
            max_output += gen.output[h]
        
        # Отбор потребителей
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
                
        # Отбор генераторов
        hour_data = self.select_generators(h, hour_demand)
        hour_data.minimal_demand = consumers_sorted[0].demand[h]
        hour_data.max_output = max_output
        hour_data.full_demand = sum(c.demand[h] for c in consumers_sorted)
        hour_data.consumers_served = consumers_served
        
        # Возврат данных
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
        hour_data.anybody_served = True
        return hour_data  

    def select_generators(self, h: int, energy_needed: float) -> DataPerHour:
        if len(self.generators) <= 8:
            return self.select_generators_brute(h, energy_needed)
        else:
            return self.select_generators_dp(h, energy_needed)
        
    def show_results(self, data : list[DataPerHour]) -> None:
        for h, hour_data in enumerate(data):
            print(f"Hour {h} -------------------------")
            if (hour_data.anybody_served):
                print(f"Full demand: {hour_data.full_demand}, max possible output: {hour_data.max_output}")
                print(f"Consumers served: {hour_data.consumers_served}")
                print(f"Generators used: {hour_data.used_gens}")
                print(f"Optimal cost: {hour_data.optimal_cost}")
            elif (hour_data.full_demand > 0):
                print(f"Full demand: {hour_data.full_demand}, max possible output: {hour_data.max_output}")
                print(f"Minimal demand ({hour_data.minimal_demand}) > max possible output ({hour_data.max_output}) ")
            else:
                print(f"Full demand: {hour_data.full_demand}, max possible output: {hour_data.max_output}")
                print(f"No demand")
            print("------------------------------------")
            
if __name__ == "__main__":
    sim = Simulator()
    all_data = sim.simulate("test.json")
    sim.show_results(all_data)