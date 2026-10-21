import math


def proportion_ci(k, n, z=1.96):
    """Proportion aur 95% normal-approximation confidence interval."""
    p = k / n
    se = math.sqrt(p * (1 - p) / n)
    return p, p - z * se, p + z * se


def two_proportion_test(k1, n1, k2, n2):
    """Do proportions ka two-sided z-test."""
    p1, p2 = k1 / n1, k2 / n2
    p_pool = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se
    p_value = math.erfc(abs(z) / math.sqrt(2))
    return p1, p2, z, p_value


print("=== Milestone 1: Noise rate ===")
p, lo, hi = proportion_ci(60, 400)
print(f"Overall audit noise: {p:.3f}, 95% CI: [{lo:.3f}, {hi:.3f}]")

# Crowd-labeled data = 90% of 50,000 tickets. Experts assumed correct.
print(f"Overall dataset noise (approx): {0.9 * p:.3f}, CI: [{0.9 * lo:.3f}, {0.9 * hi:.3f}]")

p_a, lo_a, hi_a = proportion_ci(12, 180)
p_b, lo_b, hi_b = proportion_ci(48, 220)
print(f"Tier A: {p_a:.3f}, CI: [{lo_a:.3f}, {hi_a:.3f}]")
print(f"Tier B: {p_b:.3f}, CI: [{lo_b:.3f}, {hi_b:.3f}]")

_, _, z, pv = two_proportion_test(12, 180, 48, 220)
print(f"Tier A vs B: diff = {p_b - p_a:.3f}, z = {z:.2f}, p-value = {pv:.5f}")

print("\n=== Milestone 3: Accuracy ceiling ===")
e = 0.15          # assumed flip rate
acc_obs = 0.82    # observed accuracy on noisy test set
# Observed acc = (1-e)*t + (e/5)*(1-t), where t = true accuracy
# Solving for t:
t = (acc_obs - e / 5) / ((1 - e) - e / 5)
print(f"Estimated true accuracy: {t:.3f}")