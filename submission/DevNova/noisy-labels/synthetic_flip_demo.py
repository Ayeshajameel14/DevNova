import random

random.seed(0)

K = 6
N = 200_000
T = 0.963
E = 0.15

correct = 0
for _ in range(N):
    y = random.randrange(K)

    if random.random() < T:
        pred = y
    else:
        pred = random.choice([c for c in range(K) if c != y])

    if random.random() < E:
        noisy = random.choice([c for c in range(K) if c != y])
    else:
        noisy = y

    correct += (pred == noisy)

observed = correct / N
predicted = (1 - E) * T + (E / (K - 1)) * (1 - T)

print("SYNTHETIC demo (not real data)")
print(f"Simulated observed agreement:  {observed:.4f}")
print(f"Formula prediction:            {predicted:.4f}")
print("Expected: both close to 0.82.")