"""
synthetic_flip_demo.py
======================
SYNTHETIC demo. These are NOT real HelpDeskNet-50K results.

It simulates a model with true accuracy t = 0.963 and labels flipped with
probability e = 0.15 to a uniformly random other class, then checks that the
observed agreement is close to 0.82, as the derivation in Milestone 3 predicts.

Run:  python synthetic_flip_demo.py
"""

import random

random.seed(0)

K = 6          # number of classes
N = 200_000    # simulated tickets
T = 0.963      # model's true accuracy (assumed)
E = 0.15       # flip rate (assumed)

correct = 0
for _ in range(N):
    y = random.randrange(K)                       # true class (uniform here)

    # Model: correct with probability T, otherwise a uniformly random wrong class
    if random.random() < T:
        pred = y
    else:
        pred = random.choice([c for c in range(K) if c != y])

    # Noisy label: flipped with probability E to a uniformly random other class
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