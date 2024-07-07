import random
import matplotlib.pyplot as plt
import numpy as np

def secretary_problem(n, s, m, num_iter=1000):
    success = 0
    for i in range(num_iter):
        data = random.sample(range(1, n+1), n)
        current_best = max(data[:m])
        chosen = None
        for j in range(m, n):
            # choose the first one that is greater than the current best
            if data[j] > current_best:
                chosen = data[j]
                break
        # if no one is chosen, then choose the last one
        if chosen is None:
            chosen = data[-1]
        
        # if the chosen one is the is in top s, then it is a success
        if chosen in sorted(data, reverse=True)[:s]:
            success += 1
            
    return success/num_iter*100

n = 100
s_values = [1, 3, 5, 10]
num_iter = 10000
random.seed(0)

for s in s_values:
    success_rate = []
    for m in range(1, n+1):
        success_rate.append(secretary_problem(n, s, m, num_iter))
        
    plt.plot(range(n), success_rate)
    plt.title(f'For n = {n}, s = {s}')
    plt.yticks(np.arange(0, 101, 10))
    plt.xlabel('Sample Size (m)')
    plt.ylabel('Success Rate')
    plt.savefig(f's_{s}.png')
    plt.clf()