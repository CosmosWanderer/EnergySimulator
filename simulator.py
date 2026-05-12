import json
from itertools import combinations

class Generator:
    def __init__(self, name : str, gen_type : str, cost : float, output):
        self.name = name
        self.type = gen_type
        self.cost = cost
        if gen_type == "constant":
            self.output = [output] * 24
        if gen_type == "variable":
            self.output = output

class Consumer:
    def __init__(self, name : str, demand : list):
        self.name = name
        self.demand = demand

class DataPerHour:
    pass

# Парсер для загрузки тестов
class Simulator:
    def __init__(self, testname: str):
        self.consumers = []
        self.generators = []
        self.testname = ""
        
    def simulate(self, testname : str):
        self.testname = testname
        self.parse_info()
        for hour in range(24):
            self.simulate_hour(hour)
   
        # Работа с результирующими данными
                
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
        # Максимальное кол-во энергии
        max_output = 0.0
        for gen in self.generators:
            max_output += gen.output[h]
        
        # Отбор потребителей
        consumers_sorted = sorted(self.consumers, key=lambda c: c.demand[h])
        consumers_sorted = [c for c in consumers_sorted if c.demand[h] != 0]
        
        if not consumers_sorted:
            # Обработка такого случая
            pass
        
        consumers_served = []
        hour_demand = 0.0
        for consumer in consumers_sorted:
            if hour_demand + consumer.demand[h] <= max_output:
                consumers_served.append(consumer)
                hour_demand += consumer.demand[h]
            else:
                break
        
        if not consumers_served:
            # Обработка такого случая
            pass
                
        # Отбор генераторов
        gen_data = self.select_generators(h, hour_demand)
        
        # Возврат данных
    
    def select_generators_brute(self, h: int, energy_needed: float):
        pass        

    def select_generators_dp(self, h: int, energy_needed: float):
        pass

    def select_generators(self, h: int, energy_needed: float):
        if len(self.generators) <= 20:
            return self.select_generators_brute(h, energy_needed)
        else:
            return self.select_generators_dp(h, energy_needed)