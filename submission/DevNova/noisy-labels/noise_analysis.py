"""
noise_analysis.py
=================
Milestone 1 (label noise quantification), Milestone 2 (confusion pattern),
Milestone 3 (accuracy ceiling), and Milestone 4/5 sizing helpers for
HelpDeskNet-50K (GitHub issue #9).

Uses only the Python standard library. Every input is a summary number from
the issue. No real ticket records are used, so all outputs are calculations
from those summaries, not measured facts about a real dataset.

Run:  python noise_analysis.py
"""

import math

Z95 = 1.96  # z-value for a two-sided 95% interval


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def wilson_ci(k, n, z=Z95):
    """Wilson score interval for a proportion k/n.

    Preferred over the simple normal (Wald) interval because it stays inside
    [0, 1] and behaves better for small p or moderate n.
    """
    p = k / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return p, centre - half, centre + half


def wald_ci(k, n, z=Z95):
    """Simple normal-approximation interval. Kept only for comparison."""
    p = k / n
    se = math.sqrt(p * (1 - p) / n)
    return p, p - z * se, p + z * se


def two_proportion_z(k1, n1, k2, n2):
    """Two-sided pooled z-test for H0: p1 == p2. Returns (z, p_value)."""
    p1, p2 = k1 / n1, k2 / n2
    pooled = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se
    p_value = math.erfc(abs(z) / math.sqrt(2))  # two-sided
    return z, p_value


def diff_ci_wald(k1, n1, k2, n2, z=Z95):
    """Unpooled Wald CI for the difference p2 - p1."""
    p1, p2 = k1 / n1, k2 / n2
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    d = p2 - p1
    return d, d - z * se, d + z * se


def stratified_estimate(strata, z=Z95):
    """Population-weighted proportion.

    strata: list of (weight, k, n). Weights must sum to 1.
    The variance uses w^2 * p(1-p)/n per stratum (standard stratified formula).
    """
    est = sum(w * k / n for w, k, n in strata)
    var = sum(w * w * (k / n) * (1 - k / n) / n for w, k, n in strata)
    se = math.sqrt(var)
    return est, est - z * se, est + z * se


def half_width(p, n, z=Z95):
    """Half-width of a Wald interval for a proportion p with sample size n."""
    return z * math.sqrt(p * (1 - p) / n)


# ---------------------------------------------------------------------------
# Input data from the issue
# ---------------------------------------------------------------------------

N_TOTAL = 50_000          # all tickets
N_EXPERT = 5_000          # expert-labelled (ASSUMED noise-free here)
N_TIER_A_POP = 20_000     # crowd tickets labelled by Tier A
N_TIER_B_POP = 25_000     # crowd tickets labelled by Tier B

AUDIT_N = 400             # randomly audited crowd tickets
AUDIT_DISAGREE = 60       # disagreements with experts
TIER_A_AUDIT = (12, 180)  # (disagreements, audited)
TIER_B_AUDIT = (48, 220)

# (crowd label, expert label, count)
DISAGREEMENTS = [
    ("Billing", "Refund", 14),
    ("Refund", "Billing", 12),
    ("Technical", "Account Access", 9),
    ("Shipping", "Other", 8),
    ("Account Access", "Technical", 6),
    ("Technical", "Other", 5),
    ("Other", "Shipping", 3),
    ("Billing", "Other", 3),
]

CLASS_SHARE = {
    "Billing": 0.30,
    "Refund": 0.15,
    "Technical": 0.25,
    "Account Access": 0.15,
    "Shipping": 0.10,
    "Other": 0.05,
}


# ---------------------------------------------------------------------------
# Milestone 1: noise rate, CI, tier comparison
# ---------------------------------------------------------------------------

def milestone_1():
    print("=" * 64)
    print("MILESTONE 1: Label noise quantification")
    print("=" * 64)

    p, lo, hi = wilson_ci(AUDIT_DISAGREE, AUDIT_N)
    _, wlo, whi = wald_ci(AUDIT_DISAGREE, AUDIT_N)
    print(f"Audit noise (pooled):  {p:.1%}   Wilson 95% CI [{lo:.1%}, {hi:.1%}]")
    print(f"  Wald for comparison:        [{wlo:.1%}, {whi:.1%}]")

    ka, na = TIER_A_AUDIT
    kb, nb = TIER_B_AUDIT
    pa, la, ha = wilson_ci(ka, na)
    pb, lb, hb = wilson_ci(kb, nb)
    print(f"Tier A noise:          {pa:.1%}   Wilson 95% CI [{la:.1%}, {ha:.1%}]")
    print(f"Tier B noise:          {pb:.1%}   Wilson 95% CI [{lb:.1%}, {hb:.1%}]")

    d, dlo, dhi = diff_ci_wald(ka, na, kb, nb)
    z, pv = two_proportion_z(ka, na, kb, nb)
    print(f"Tier B - Tier A:       {d * 100:.1f} pp, 95% CI [{dlo * 100:.1f}, {dhi * 100:.1f}] pp")
    print(f"Pooled two-proportion z-test: z = {z:.2f}, two-sided p = {pv:.2e}")

    # Population-weighted crowd estimate (the correct way to combine tiers).
    n_crowd = N_TIER_A_POP + N_TIER_B_POP
    wa = N_TIER_A_POP / n_crowd
    wb = N_TIER_B_POP / n_crowd
    est, slo, shi = stratified_estimate([(wa, ka, na), (wb, kb, nb)])
    print(f"\nTier weights: A = {wa:.3f}, B = {wb:.3f}")
    print(f"Crowd-label noise (population-weighted): {est:.1%}   95% CI [{slo:.1%}, {shi:.1%}]")

    # Whole dataset. ASSUMPTION: expert-labelled tickets are correct.
    frac = n_crowd / N_TOTAL
    print(f"Whole dataset noise (experts assumed 100% correct): "
          f"{frac * est:.1%}   CI [{frac * slo:.1%}, {frac * shi:.1%}]")

    return est


# ---------------------------------------------------------------------------
# Milestone 2: which confusions dominate?
# ---------------------------------------------------------------------------

def milestone_2():
    print()
    print("=" * 64)
    print("MILESTONE 2: Noise pattern")
    print("=" * 64)

    total = sum(c for _, _, c in DISAGREEMENTS)
    assert total == AUDIT_DISAGREE, "disagreement counts must sum to 60"

    # Unordered pair totals (A->B and B->A combined)
    pairs = {}
    for crowd, expert, c in DISAGREEMENTS:
        key = tuple(sorted((crowd, expert)))
        pairs[key] = pairs.get(key, 0) + c

    print("Confusion pairs (both directions combined):")
    for (a, b), c in sorted(pairs.items(), key=lambda kv: -kv[1]):
        print(f"  {a} <-> {b}: {c}/{total} = {c / total:.1%}")

    top2 = pairs[("Billing", "Refund")] + pairs[("Account Access", "Technical")]
    print(f"Top 2 pairs together: {top2}/{total} = {top2 / total:.1%}")
    print(f"Directed off-diagonal pairs possible: 30, observed: {len(DISAGREEMENTS)}")

    # Crowd-label error rate per class. Uses EXPECTED audited counts
    # (400 * class share) because the per-class audit counts are not given.
    errors_by_label = {}
    for crowd, _, c in DISAGREEMENTS:
        errors_by_label[crowd] = errors_by_label.get(crowd, 0) + c

    print("\nApproximate crowd-label error rate by class (ESTIMATE):")
    for label, share in CLASS_SHARE.items():
        expected_n = AUDIT_N * share
        e = errors_by_label.get(label, 0)
        print(f"  {label:15s}: {e} errors / ~{expected_n:.0f} audited = ~{e / expected_n:.1%}")

    # Tier comparison from the audit
    ratio = (TIER_B_AUDIT[0] / TIER_B_AUDIT[1]) / (TIER_A_AUDIT[0] / TIER_A_AUDIT[1])
    print(f"\nTier B error rate is about {ratio:.1f}x Tier A's (audit-based).")


# ---------------------------------------------------------------------------
# Milestone 3: accuracy ceiling under uniform label flips
# ---------------------------------------------------------------------------

def observed_accuracy(true_acc, flip, k=6):
    """Forward model.

    observed = P(label correct) * P(model correct)
             + P(label flipped) * P(model's prediction equals the flipped label)
             = (1 - e) * t + (e / (k-1)) * (1 - t)
    """
    q = flip / (k - 1)
    return (1 - flip) * true_acc + q * (1 - true_acc)


def true_accuracy_from_observed(obs, flip, k=6):
    """Inverse of observed_accuracy. Solves obs = (1-e)t + q(1-t) for t.

    t = (obs - q) / ((1 - e) - q)
    """
    q = flip / (k - 1)
    return (obs - q) / ((1 - flip) - q)


def milestone_3():
    print()
    print("=" * 64)
    print("MILESTONE 3: Accuracy ceiling")
    print("=" * 64)

    obs = 0.82
    _, flo, fhi = wilson_ci(AUDIT_DISAGREE, AUDIT_N)
    flip_point = AUDIT_DISAGREE / AUDIT_N

    print("Model: observed = (1 - e) * t + (e/5) * (1 - t)")
    print("Solve: t = (observed - e/5) / ((1 - e) - e/5)")
    print(f"Observed test accuracy = {obs:.2f}, flip rate e = {flip_point:.3f}")
    print(f"Feasibility: t <= 1 requires observed <= 1 - e, so e must be <= {1 - obs:.3f}\n")

    for label, e in [("lower CI", flo), ("point", flip_point), ("upper CI", fhi)]:
        if obs > 1 - e:
            print(f"  {label:9s} e = {e:.3f}: INFEASIBLE (observed {obs:.2f} > 1 - e = {1 - e:.3f})")
        else:
            t = true_accuracy_from_observed(obs, e)
            print(f"  {label:9s} e = {e:.3f}: true accuracy t = {t:.4f}")

    t_point = true_accuracy_from_observed(obs, flip_point)
    check = observed_accuracy(t_point, flip_point)
    print(f"\nCheck: plugging t = {t_point:.4f} back in gives observed = {check:.4f}")


# ---------------------------------------------------------------------------
# Milestone 4: review budget for exactly 2,000 tickets
# ---------------------------------------------------------------------------

def milestone_4_budget():
    print()
    print("=" * 64)
    print("MILESTONE 4: Expert review budget (2,000 tickets)")
    print("=" * 64)

    budget = {
        "Model uncertainty (lowest margin, out-of-fold)": 600,
        "Confident model-label disagreement (out-of-fold)": 500,
        "Suspicious / influential (high loss, Tier B, confusable pairs)": 500,
        "Minority and class coverage (Other, Shipping)": 200,
        "Random baseline (evaluation only)": 200,
    }
    total = sum(budget.values())
    assert total == 2000, "review budget must total exactly 2,000"
    for name, n in budget.items():
        print(f"  {n:5d}  ({n / total:5.1%})  {name}")
    print(f"  {total:5d}  TOTAL")


# ---------------------------------------------------------------------------
# Milestone 5: sizing the expert-labelled evaluation set
# ---------------------------------------------------------------------------

def milestone_5_sizing():
    print()
    print("=" * 64)
    print("MILESTONE 5: Evaluation set sizing")
    print("=" * 64)

    n_per_class = 200
    p = 0.90  # assumed per-class recall (a planning guess, not a result)
    hw = half_width(p, n_per_class)
    print(f"Per-class n = {n_per_class}, recall ~{p:.0%}: 95% half-width = +/- {hw * 100:.1f} pp")

    target_hw = 0.03
    n_needed = math.ceil(Z95 ** 2 * p * (1 - p) / target_hw ** 2)
    print(f"Samples needed for +/- 3 pp at {p:.0%} accuracy: {n_needed}")


if __name__ == "__main__":
    milestone_1()
    milestone_2()
    milestone_3()
    milestone_4_budget()
    milestone_5_sizing()