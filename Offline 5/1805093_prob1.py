import numpy as np

def nuclear_chain_sim(num_gen = 10, num_sim = 10000):
    
    probs = [0.2126 * 0.5893 ** i for i in range(3)]
    probs.insert(0, 1 - sum(probs))
    
    results = []
    for i in range(num_gen):
        results.append(np.zeros(5))
    
    for i in range(num_sim):
        gen_counts = []
        
        # simulate one first generation
        new_neutrons = sum(np.random.choice([0, 1, 2, 3], p=probs, size=1))
        gen_counts.append(new_neutrons)
        
        for j in range(1, num_gen):
            new_neutrons = sum(np.random.choice([0, 1, 2, 3], p=probs, size=gen_counts[-1]))
            gen_counts.append(new_neutrons)
        
        for gen in range(num_gen):
            results[gen][min(gen_counts[gen], 4)] += 1
    
    probabilities = [count / num_sim for count in results]
    
    return probabilities

N_GEMS = 10
N_SIMS = 10000
results = nuclear_chain_sim(N_GEMS, N_SIMS)
np.random.seed(0)

for i, gen_probs in enumerate(results, 1):
    print(f'Generation-{i}:')
    for j, prob in enumerate(gen_probs):
        print(f'p[{j}] = {prob:.4f}')
    print()