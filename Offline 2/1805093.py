import math, sys

################################################################

MODLUS = 2147483647
MULT1 = 24112
MULT2 = 26143

zrng = [1,
        1973272912, 281629770, 20006270, 1280689831, 2096730329, 1933576050,
        913566091, 246780520, 1363774876, 604901985, 1511192140, 1259851944,
        824064364, 150493284, 242708531, 75253171, 1964472944, 1202299975,
        233217322, 1911216000, 726370533, 403498145, 993232223, 1103205531,
        762430696, 1922803170, 1385516923, 76271663, 413682397, 726466604,
        336157058, 1432650381, 1120463904, 595778810, 877722890, 1046574445,
        68911991, 2088367019, 748545416, 622401386, 2122378830, 640690903,
        1774806513, 2132545692, 2079249579, 78130110, 852776735, 1187867272,
        1351423507, 1645973084, 1997049139, 922510944, 2045512870, 898585771,
        243649545, 1004818771, 773686062, 403188473, 372279877, 1901633463,
        498067494, 2087759558, 493157915, 597104727, 1530940798, 1814496276,
        536444882, 1663153658, 855503735, 67784357, 1432404475, 619691088,
        119025595, 880802310, 176192644, 1116780070, 277854671, 1366580350,
        1142483975, 2026948561, 1053920743, 786262391, 1792203830, 1494667770,
        1923011392, 1433700034, 1244184613, 1147297105, 539712780, 1545929719,
        190641742, 1645390429, 264907697, 620389253, 1502074852, 927711160,
        364849192, 2049576050, 638580085, 547070247]

def lcgrand(stream):
    zi = zrng[stream]
    lowprd = (zi & 65535) * MULT1
    hi31 = (zi >> 16) * MULT1 + (lowprd >> 16)
    zi = ((lowprd & 65535) - MODLUS) + ((hi31 & 32767) << 16) + (hi31 >> 15)
    if zi < 0:
        zi += MODLUS
    lowprd = (zi & 65535) * MULT2
    hi31 = (zi >> 16) * MULT2 + (lowprd >> 16)
    zi = ((lowprd & 65535) - MODLUS) + ((hi31 & 32767) << 16) + (hi31 >> 15)
    if zi < 0:
        zi += MODLUS
    zrng[stream] = zi
    return (zi >> 7 | 1) / 16777216.0

################################################################

# Single Product Inventory System

NONE = 0
ORDER_ARRIVAL = 1
DEMAND = 2
END_SIMULATION = 3
EVALUATE = 4

STREAM = 1

class SingleProductInventorySystem:
    def __init__(self, input_file, output_file="out.txt"):
        self.input_file = input_file
        self.output_file = output_file
        
    def read_input(self):
        self.policies = []
        with open(self.input_file) as f:
            self.initial_inv_level, self.num_months, self.num_policies = map(int, f.readline().split())
            num_values_demand, self.mean_interdemand = map(float, f.readline().split())
            self.num_values_demand = int(num_values_demand)
            self.setup_cost, self.incremental_cost, self.holding_cost, self.shortage_cost = map(float, f.readline().split())
            self.minlag, self.maxlag = map(float, f.readline().split())
            self.prob_distrib_demand = [0.0] + list(map(float, f.readline().split()))
            
            for _ in range(self.num_policies):
                self.policies.append(map(int, f.readline().split()))
                
    def initialize(self):
        self.time = 0.0
        
        self.inv_level = self.initial_inv_level
        self.time_last_event = 0.0
        
        self.total_ordering_cost = 0.0
        self.area_holding = 0.0
        self.area_shortage = 0.0
        
        self.time_next_event = [0.0] * 5
        self.time_next_event[ORDER_ARRIVAL] = 1.0e+30
        self.time_next_event[DEMAND] = self.time + self.expon(self.mean_interdemand)
        self.time_next_event[END_SIMULATION] = self.num_months
        self.time_next_event[EVALUATE] = 0.0  
        
        self.next_event_type = NONE
        
    def expon(self, mean):
        return -mean * math.log(lcgrand(stream=STREAM))
    
    def random_integer(self, prob_distrib):
        u = lcgrand(stream=STREAM)
        for i in range(1, self.num_values_demand + 1):
            if u < prob_distrib[i]:
                break        
        return i
            
    def uniform(self, a, b):
        return a + lcgrand(stream=STREAM) * (b - a)
        
    def timing(self):
        min_time_next_event = 1.0e+29
        self.next_event_type = NONE
        
        for i in range(1, 5): # 1 to 4 as in 4 types of events
            if self.time_next_event[i] < min_time_next_event:
                min_time_next_event = self.time_next_event[i]
                self.next_event_type = i
                
        if self.next_event_type == NONE:
            print("Event list empty at time {}".format(self.time))
            sys.exit()
        
        self.time = min_time_next_event
        
    def order_arrival(self):
        self.inv_level += self.amount
        self.time_next_event[ORDER_ARRIVAL] = 1.0e+30
        
    def demand(self):
        self.inv_level -= self.random_integer(self.prob_distrib_demand)
        self.time_next_event[DEMAND] = self.time + self.expon(self.mean_interdemand)
        
    def evaluate(self):
        if self.inv_level < self.smalls:
            self.amount = self.bigs - self.inv_level
            self.total_ordering_cost += self.setup_cost + self.incremental_cost * self.amount
            self.time_next_event[ORDER_ARRIVAL] = self.time + self.uniform(self.minlag, self.maxlag)
            
        self.time_next_event[EVALUATE] = self.time + 1.0
        
    def report(self):
        avg_ordering_cost = self.total_ordering_cost / self.num_months
        avg_holding_cost = self.holding_cost * self.area_holding / self.num_months
        avg_shortage_cost = self.shortage_cost * self.area_shortage / self.num_months
        
        with open("out.txt", "a") as f:
            f.write(f"({self.smalls}, {self.bigs}) \t\t\t{avg_ordering_cost+avg_holding_cost+avg_shortage_cost:.2f}")
            f.write(f"\t\t\t\t{avg_ordering_cost:.2f}\t\t\t\t{avg_holding_cost:.2f}\t\t\t\t{avg_shortage_cost:.2f}\n\n")
        
    def update_time_avg_stats(self):
        time_since_last_event = self.time - self.time_last_event
        self.time_last_event = self.time
        
        if self.inv_level < 0:
            self.area_shortage -= self.inv_level * time_since_last_event
        elif self.inv_level > 0:
            self.area_holding += self.inv_level * time_since_last_event            
        
    def run(self):
        self.read_input()
        
        with open(self.output_file, "w") as f:
            f.write("------Single-Product Inventory System------\n\n")
            f.write(f"Initial inventory level: {self.initial_inv_level} items\n\n")
            f.write(f"Number of demand sizes: {self.num_values_demand}\n\n")
            f.write("Distribution function of demand sizes: ")
            for i in range(1, self.num_values_demand + 1):
                f.write(f"{self.prob_distrib_demand[i]:.2f} ")
            f.write("\n\n")
            f.write(f"Mean inter-demand time: {self.mean_interdemand:.2f} months\n\n")
            f.write(f"Delivery lag range: {self.minlag:.2f} to {self.maxlag:.2f} months\n\n")
            f.write(f"Length of simulation: {self.num_months} months\n\n")
            f.write("Costs:\n")
            f.write(f"K = {self.setup_cost:.2f}\n")
            f.write(f"i = {self.incremental_cost:.2f}\n")
            f.write(f"h = {self.holding_cost:.2f}\n")
            f.write(f"pi = {self.shortage_cost:.2f}\n\n")
            f.write(f"Number of policies: {self.num_policies}\n\n")
            f.write("Policies:\n")
            f.write("--------------------------------------------------------------------------------------------------\n")
            f.write(" Policy\t\t\tAvg_total_cost\t\tAvg_ordering_cost\tAvg_holding_cost\tAvg_shortage_cost\n")
            f.write("--------------------------------------------------------------------------------------------------\n\n")
            
        for smalls, bigs in self.policies:
            self.smalls, self.bigs = smalls, bigs
            self.initialize()
            while self.next_event_type != END_SIMULATION:
                self.timing()
                self.update_time_avg_stats()
                if self.next_event_type == ORDER_ARRIVAL:
                    self.order_arrival()
                elif self.next_event_type == DEMAND:
                    self.demand()
                elif self.next_event_type == EVALUATE:
                    self.evaluate()
                elif self.next_event_type == END_SIMULATION:
                    self.report()
                    
        with open(self.output_file, "a") as f:
            f.write("--------------------------------------------------------------------------------------------------\n")
    
    
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:    
    input_file = "in.txt"
    
if len(sys.argv) > 2:
    output_file = sys.argv[2]
else:
    output_file = "out.txt"
    
SingleProductInventorySystem(input_file, output_file).run()