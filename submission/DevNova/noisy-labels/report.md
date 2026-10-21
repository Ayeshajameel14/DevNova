# Noisy Labels: HelpDeskNet-50K – Analysis

## 1. Label Noise Quantification
**Overall noise rate:** 60/400 = 0.15 (15%)
**95% CI:** [0.114, 0.186]
Formula: p ± 1.96 × √(p(1−p)/n)

**Tier A vs Tier B:** Tier A = 12/180 (6.7%), Tier B = 48/220 (21.8%)
**Z-test:** z ≈ 4.22, p < 0.001
- Yahan likhein: difference chance ki wajah se kyun nahi lagta, aur iska matlab kya hai.

## 2. Noise Characterization
- Disagreement table dekh kar pattern likhein (Billing↔Refund, Technical↔Account Access).
- Root cause ka apna guess likhein.
- Annotation process mein kya check ya change karna chahiye.

## 3. Accuracy Ceiling
- Calculation: t = (0.82 − 0.15/5) / (0.85 − 0.15/5) ≈ 0.963
- Yeh estimate kyun unreliable hai: noise uniform nahi, test set bhi noisy hai, etc.

## 4. Expert Review Plan (2,000 tickets)
- Selection strategy aap ki apni hogi (model confidence, loss, Tier B, confusing classes).
- Evaluation: selection method random se behtar hai ya nahi, kaise check karein.
- Corrected labels training mein kaise use honge.

## 5. Noise-Robust Training & Evaluation
- Do training methods (jaise Co-teaching, Generalized Cross-Entropy) aur kyun.
- Trustworthy test set kaise banayein.
- Crowd test set problematic kyun hai.