import math

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

NONE = 0
ARRIVAL = 1
DEPARTURE = 2

class SingleServerQueue:
    def __init__(self, num_events=2):
        self.q_limit = 100
        self.next_event_type = NONE
        self.num_custs_delayed = 0
        self.num_delays_required = 0
        self.num_events = num_events
        self.num_in_q = 0
        self.server_busy = False
        self.event_count = 0

        self.input_file = "in.txt"
        self.results_file = "results.txt"
        self.event_orders_file = "event_orders.txt"

        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.mean_interarrival = 0.0
        self.mean_service = 0.0
        self.time = 0.0
        self.time_last_event = 0.0
        self.total_of_delays = 0.0

        self.time_arrival = [0.0] * (self.q_limit + 1)
        self.time_next_event = [0.0] * 3

        self.event_count = 0
        self.num_custs_arrived = 0
        self.num_custs_departed = 0
        # self.lcgrand = lcgrand.lcgrand(stream=1)

    def read_input(self):
        with open(self.input_file) as f:
            line = f.readline()

        self.mean_interarrival, self.mean_service, self.num_delays_required = map(float, line.split())

        with open(self.results_file, "w") as f:
            f.write("----Single-Server Queueing System----\n\n")
            f.write("Mean inter-arrival time: {:.6f} minutes\n".format(self.mean_interarrival))
            f.write("Mean service time: {:.6f} minutes\n".format(self.mean_service))
            f.write("Number of customers: {}\n".format(int(self.num_delays_required)))

        with open(self.event_orders_file, "w") as f:
            pass

    def init_simulation(self):
        self.time_next_event[ARRIVAL] = self.time + self.expon(self.mean_interarrival)
        self.time_next_event[DEPARTURE] = 1.0e+30

    def timing(self):
        min_time_next_event = 1.0e+29
        self.next_event_type = NONE

        for i in range(1, self.num_events + 1):
            if self.time_next_event[i] < min_time_next_event:
                min_time_next_event = self.time_next_event[i]
                self.next_event_type = i

        if self.next_event_type == NONE:
            print("Event list empty at time {}".format(self.time))
            exit(1)

        self.event_count += 1
        with open(self.event_orders_file, "a") as f:
            f.write("{}. Next event: ".format(self.event_count))
            if self.next_event_type == ARRIVAL:
                self.num_custs_arrived += 1
                f.write("Customer {} Arrival\n".format(self.num_custs_arrived))
            elif self.next_event_type == DEPARTURE:
                self.num_custs_departed += 1
                f.write("Customer {} Departure\n".format(self.num_custs_departed))

        self.time = min_time_next_event

    def arrive(self):
        self.time_next_event[ARRIVAL] = self.time + self.expon(self.mean_interarrival)

        if self.server_busy:
            self.num_in_q += 1
            if self.num_in_q > self.q_limit:
                print("Overflow of the array time_arrival at time {}".format(self.time))
                exit(2)
            self.time_arrival[self.num_in_q] = self.time
        else:
            self.num_custs_delayed += 1
            with open(self.event_orders_file, "a") as f:
                f.write("\n---------No. of customers delayed: {}--------\n\n".format(self.num_custs_delayed))
            self.server_busy = True
            self.time_next_event[DEPARTURE] = self.time + self.expon(self.mean_service)

    def depart(self):
        if self.num_in_q == 0:
            self.server_busy = False
            self.time_next_event[DEPARTURE] = 1.0e+30
        else:
            self.num_in_q -= 1
            delay = self.time - self.time_arrival[1]
            self.total_of_delays += delay

            self.num_custs_delayed += 1
            with open(self.event_orders_file, "a") as f:
                f.write("\n---------No. of customers delayed: {}--------\n\n".format(self.num_custs_delayed))

            self.time_next_event[DEPARTURE] = self.time + self.expon(self.mean_service)

            for i in range(1, self.num_in_q + 1):
                self.time_arrival[i] = self.time_arrival[i + 1]

    def update_time_avg_stats(self):
        time_since_last_event = self.time - self.time_last_event
        self.time_last_event = self.time

        self.area_num_in_q += self.num_in_q * time_since_last_event
        self.area_server_status += self.server_busy * time_since_last_event

    def report(self):
        with open(self.results_file, "a") as f:
            f.write("\nAvg delay in queue: {:.6f} minutes\n".format(self.total_of_delays / self.num_custs_delayed))
            f.write("Avg number in queue: {:.6f}\n".format(self.area_num_in_q / self.time))
            f.write("Server utilization: {:.6f}\n".format(self.area_server_status / self.time))
            f.write("Time simulation ended: {:.6f} minutes\n".format(self.time))

    def expon(self, mean):
        return -mean * math.log(lcgrand(stream=1))

    def simulate(self):
        self.read_input()
        self.init_simulation()

        while self.num_custs_delayed < self.num_delays_required:
            self.timing()
            self.update_time_avg_stats()

            if self.next_event_type == ARRIVAL:
                self.arrive()
            elif self.next_event_type == DEPARTURE:
                self.depart()

        self.report()

if __name__ == "__main__":
    SingleServerQueue().simulate()