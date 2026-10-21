# Noisy Labels: HelpDeskNet-50K: Analysis

**Scope and sources.** Every number below comes from the summary statistics in issue #9. No real ticket records or model predictions were available. Values come from `noise_analysis.py`. Items marked **ESTIMATE** are approximations or assumption-dependent. Items marked **MEASURED** are direct calculations from given counts.

## Summary of results

| Quantity | Value | Type |
|---|---|---|
| Audit noise (60/400) | 15.0%, Wilson 95% CI [11.8%, 18.8%] | MEASURED (sample) |
| Tier A noise (12/180) | 6.7%, CI [3.9%, 11.3%] | MEASURED (sample) |
| Tier B noise (48/220) | 21.8%, CI [16.9%, 27.7%] | MEASURED (sample) |
| Tier B minus Tier A | 15.2 pp, z = 4.22, p ≈ 2.4e-5 | MEASURED (test) |
| Crowd-label noise, population-weighted | 15.1%, CI [11.6%, 18.5%] | ESTIMATE |
| Whole dataset noise (experts assumed correct) | 13.6%, CI [10.5%, 16.7%] | ESTIMATE |
| Implied true accuracy (uniform flips) | 96.3% (range about 92.8% to 100%) | ESTIMATE |

## 1. Label Noise Quantification

**Sampling.** Experts relabelled 400 randomly selected crowd tickets: 180 from Tier A and 220 from Tier B. Expert labels are treated as the reference. A disagreement means the crowd label differs from the expert label. This is not proof that the crowd is wrong, since experts can also err.

**Overall noise.** The point estimate is 60/400 = 15.0%. I used a Wilson interval, which gives [11.8%, 18.8%]. The simple Wald interval gives [11.5%, 18.5%], which is slightly narrower and less reliable for this sample. The interval means that if the same audit were repeated many times under the same assumptions, about 95% of such intervals would contain the true audit rate. It does not say that the true noise has a 95% chance of being in this range for this one sample.

**Tier comparison.** Tier A's noise is 6.7% with CI [3.9%, 11.3%]. Tier B's is 21.8% with CI [16.9%, 27.7%]. The two intervals do not overlap, which already suggests a real difference. The formal test is a pooled two-proportion z-test. The pooled proportion (60/400 = 15%) is used because under the null hypothesis both tiers share one noise rate, so the standard error should be estimated from the combined data. The result is z = 4.22, two-sided p ≈ 2.4 × 10⁻⁵. This p-value is the probability of seeing a gap at least this large if both tiers truly had the same noise rate. It is very small, so chance alone is an unlikely explanation. The difference is 15.2 percentage points, with an unpooled 95% CI of [8.6, 21.7] pp.

**Whole-crowd estimate.** The audit has 45% Tier A and 55% Tier B, while the population is 20,000/45,000 = 44.4% Tier A and 55.6% Tier B. These are close, but I weighted by population anyway, which is the correct approach:

- Crowd noise = 0.444 × 6.7% + 0.556 × 21.8% ≈ 15.1%.
- Normal-approximation CI using stratified variance: [11.6%, 18.5%].

The earlier shortcut of 0.9 × 15% = 13.5% was not the right way to do this. For the whole dataset, 45,000 of 50,000 tickets are crowd-labelled, so 0.9 × 15.1% ≈ **13.6%**, CI [10.5%, 16.7%]. This assumes the 5,000 expert-labelled tickets are correct, which is an assumption.

**Assumptions and uncertainty.**
- Simple random sampling within each tier.
- Expert labels are the reference, and experts may themselves be wrong.
- The 5,000 expert tickets are treated as clean.
- The audit sample is only 400 tickets, so the intervals are wide.
- The finite-population correction is negligible here (400 of 45,000 is under 1%).
- The Tier B result depends on whether the 220 audited tickets are representative of all 25,000 Tier B tickets.

## 2. Noise Characterization

**Observed pattern (MEASURED counts, ESTIMATE of rates).**

| Pair (both directions) | Count | Share of 60 |
|---|---|---|
| Billing ↔ Refund | 26 (14 + 12) | 43.3% |
| Technical ↔ Account Access | 15 (9 + 6) | 25.0% |
| Shipping ↔ Other | 11 (8 + 3) | 18.3% |
| Technical ↔ Other | 5 | 8.3% |
| Billing ↔ Other | 3 | 5.0% |

Two pairs account for 41 of 60 disagreements (68%). Only 8 of the 30 possible directed confusions appear at all. If errors were random, they would spread across many class pairs, and each directed pair would have a count of about 2. Instead, a few pairs dominate, which means the errors are **systematic**.

**Directional patterns.**
- Billing → Refund (14) and Refund → Billing (12) are nearly symmetric. Workers confuse these two classes in both directions, which points to an unclear boundary, not one worker's habit.
- Shipping → Other (8) is much larger than Other → Shipping (3). Workers sometimes label a ticket as Shipping when the expert calls it Other, and this is asymmetric.
- Billing → Other (3) has no reverse counterpart in the table.

**Per-class error rates (ESTIMATE).** The audit does not give per-class counts, so I used expected counts (400 × class share):
- Refund: 12 / ~60 ≈ 20%
- Shipping: 8 / ~40 ≈ 20%
- Billing: 17 / ~120 ≈ 14%
- Technical: 14 / ~100 ≈ 14%
- Other: 3 / ~20 ≈ 15%
- Account Access: 6 / ~60 ≈ 10%

Refund and Shipping have the highest rates, but these numbers come from only 400 tickets, so they are rough.

**Most likely root cause.** The main cause is probably **ambiguous class boundaries combined with incomplete guidelines**. A ticket such as "I was charged twice and want my money back" can be a Billing issue or a Refund request. Similarly, "my package never arrived and I want a refund" can be Shipping or Refund, and "something is broken with my payment" can be Technical or Billing. Workers without a clear precedence rule will pick differently. Tier B is about 3.3 times as noisy as Tier A (21.8% vs 6.7%), so inexperience, weaker training, or less familiarity with the guidelines probably adds to the problem. Tier A's low noise suggests the task is learnable with good instructions, so the problem is more likely guideline clarity and training than the task being impossible.

**What to check or change.**
1. **Guidelines:** write a precedence rule for multi-intent tickets (for example, "the action the customer is asking the company to take decides the label"). Add a library of boundary examples for each confusable pair.
2. **Other class:** tighten its definition, because a catch-all class often absorbs ambiguous tickets. Track how often workers choose it.
3. **Worker training:** require a qualification test for Tier B workers against gold-standard tickets before they label live data. Give feedback on the confused pairs specifically.
4. **Quality checks:** insert gold-standard tickets (about 5–10% of each batch) and track per-worker accuracy and per-worker confusion matrices.
5. **Agreement measurement:** have multiple workers label an overlapping sample and compute Cohen's kappa (or Fleiss' kappa for more than two workers) by pair of classes.
6. **Adjudication:** send tickets with disagreement, or those in the confusable pairs, to an expert adjudicator. Use the outcomes to update the guidelines.
7. **Interface:** make sure workers see the full ticket conversation, not just the first message, since missing context may explain some boundary errors.

## 3. Accuracy Ceiling

**Model.** Let t be the model's true accuracy against the hidden true label, and e = 0.15 the probability that a label is flipped. A flipped label is replaced by one of the other 5 classes uniformly.

**Derivation.** The observed label agrees with the model prediction in two ways:

1. **Label is correct (probability 1 − e = 0.85) and the model is correct (probability t).** Then the prediction equals the label, so the observation is correct. Contribution: 0.85 × t.
2. **Label is flipped (probability e = 0.15) and the model is wrong (probability 1 − t).** The model predicts one of the 5 wrong classes uniformly. The flipped label is also one of the 5 non-true classes, uniformly. The chance they match is 1/5. Contribution: 0.15 × (1 − t) × (1/5) = 0.03 × (1 − t).

Other cases (label correct and model wrong, or label flipped and model correct) make the observed label disagree with the prediction.

So:
observed = 0.85 t + 0.03 (1 − t) = 0.03 + 0.82 t

Setting observed = 0.82:
0.82 = 0.03 + 0.82 t, so t = 0.79 / 0.82 ≈ **0.963 (96.3%)**

**Check.** Plugging t = 0.9634 back in: 0.85 × 0.9634 + 0.03 × 0.0366 ≈ 0.8189 + 0.0011 = 0.8200. ✓

**Sensitivity.** The flip rate itself is uncertain. Using the 95% CI for e:
- e = 11.8%: t ≈ 92.8%
- e = 15.0%: t ≈ 96.3%
- e = 18.0%: t = 100% (the upper limit, since observed cannot exceed 1 − e)
- e above 18.0%: the observed accuracy of 82% is impossible under this model.

So the plausible range is roughly **93% to 100%**, and the point estimate is only one of many possibilities.

**Why the estimate is unreliable.**
1. **The uniform assumption is contradicted by the data.** Errors concentrate on Billing ↔ Refund and Technical ↔ Account Access. A flipped Billing label is much more likely to become Refund than Shipping. This affects the chance that the model's wrong predictions match the noisy label.
2. **Model errors and label errors may be correlated.** If a model and the crowd both tend to say "Refund" for the same ambiguous Billing tickets, the model's mistakes will look correct against the noisy labels. This makes the observed accuracy higher than the true accuracy, so the true accuracy is likely lower than 96%. The direction is what matters here: the more often wrong predictions match the noisy label, the lower the implied true accuracy.
3. **The test set is noisy too.** The test labels come from the same crowd process, but the 15% flip rate was estimated from the training audit. Without a measured test-set noise rate, the estimate depends on an assumption.
4. **Expert truth is not perfect.** The "true" label is itself the expert label, which can be wrong.
5. **Class imbalance is ignored.** The 82% is overall accuracy. A model could score well on Billing and Refund (30% and 15% of data) while doing poorly on Other (5%). Per-class recall is needed for a full picture.
6. **Independence is assumed.** The formula assumes model errors and label flips are independent, which may not hold for hard examples.

## 4. Expert Review Plan (2,000 Tickets)

**Budget allocation.**

| Stream | Tickets | Selection rule |
|---|---|---|
| Model uncertainty | 600 | Lowest margin (top-1 minus top-2 probability) from out-of-fold predictions |
| Confident model-label disagreement | 500 | Model predicts a different class with high confidence (e.g., ≥ 0.8), using out-of-fold predictions |
| Suspicious or influential | 500 | High loss on held-out folds, cross-model disagreement, Tier B labels, labels in confusable pairs |
| Minority and class coverage | 200 | Stratified: about 100 Other and 100 Shipping tickets |
| Random baseline | 200 | Simple random sample from the non-audited pool; used only for evaluation |
| **Total** | **2,000** | |

**Why this mix.** Uncertainty and disagreement find tickets the model is unsure about or confidently contradicts. Suspicious and influential tickets target the systematic confusion pairs from Milestone 2. Minority coverage makes sure Other and Shipping, which have few tickets, are represented. The random baseline is kept separate so the review can be judged fairly.

**Deduplication.** Customer-support tickets often repeat templates or are near-duplicates. Before selection:
- Remove exact duplicates.
- Cluster near-duplicates (for example, with MinHash or TF-IDF cosine similarity above a chosen threshold).
- Select at most one or a few representatives per cluster, so the review budget is not spent on the same pattern many times.
- Do the same before the train/validation/test split, so duplicates do not leak across splits.

**Overlap control.** A ticket can be selected by more than one stream. Count it once and backfill from the next-ranked ticket in the same stream, so the total stays at exactly 2,000.

**Minority-class coverage.** Other and Shipping make up 15% of the data together. Without stratification, a model-driven selection might ignore them. Reserving 200 tickets for them guarantees some review in those classes.

**Evaluating whether the selection method works.**
- Let r be the error rate found in the random baseline (for example, 30 errors in 200 would be 15%).
- Let p_flag be the error rate found among the model-selected tickets (the precision of flagged errors).
- The lift is p_flag / r. A lift above 1 means the selection is better than random.
- Compare the two groups with a two-proportion test or Fisher's exact test. Report the lift with a CI.
- Compare error rates by stream. This shows which stream is most useful.
- Caveat: the random baseline is small, so the CI on r will be wide. A clear lift needs a large difference in precision.

**Precision and efficiency metrics.**
- Precision of flagged errors = confirmed corrections / flagged tickets reviewed.
- Errors found per expert-review hour = confirmed corrections / hours logged. Log expert time per ticket. Do not assume a time value until it is measured.

**Correction records.** Keep one record per reviewed ticket with: ticket ID, original label, expert label, reviewer ID, timestamp, selection stream, reason code (for example, "Billing vs Refund boundary"), confidence (if the expert records it), and adjudication status. Keep the selection stream tag so precision can be computed per stream later.

**Using the corrected labels.**
1. Apply corrections only to the training pool, and only for tickets that went through expert review and adjudication.
2. Retrain the model with the same hyperparameters and at least three random seeds.
3. Evaluate on the expert-labelled evaluation set (Milestone 5). Do not evaluate on tickets used in training.
4. Keep the reviewed tickets in one of two places: training data (corrected) or evaluation data (expert-labelled), but not both. If some reviewed tickets are used in evaluation, exclude them from training.
5. Optionally repeat the process: use the retrained model to find new suspicious tickets, and review another batch. Check whether precision drops, which would mean the easy errors are already found.

## 5. Noise-Robust Training and Trustworthy Evaluation

**Method 1: Generalized Cross-Entropy (GCE).** GCE uses the loss L_q = (1 − p_y^q) / q, where p_y is the predicted probability of the labelled class and q is between 0 and 1 (often around 0.7). Standard cross-entropy (q → 0) heavily penalises samples where the model gives the labelled class a low probability, which is exactly what mislabelled samples do. GCE caps this penalty, so the gradient from one wrong label cannot dominate training. q = 1 becomes mean absolute error, which is very noise-tolerant but learns slowly. GCE is a middle ground between the two.

**Method 2: Co-teaching.** Two networks start with different random initialisations. In each mini-batch, each network selects the samples with the smallest loss (the samples it finds easiest), and passes those to its peer for the gradient update. The idea is that clean samples usually have lower loss early in training, while noisy samples have high loss. Because the two networks make different mistakes, they filter each other's noise. In the original method the fraction of samples discarded (the "forget rate") grows from 0 to the estimated noise rate over the first several epochs. The noise estimate here would come from Milestone 1 (about 15%), and it should be refined with the corrected labels.

Other options (not required): symmetric cross-entropy and label smoothing.

**Expert-labelled evaluation set.**

- **Source:** tickets from a held-out pool that is excluded from training, from the review selection, and from early stopping. Deduplicate and split by cluster (for example, by customer or thread ID) so near-duplicates do not appear on both sides.
- **Size and coverage:** 200 tickets per class, for 1,200 total, so all six classes have enough tickets for per-class metrics. Each class has at least 200 samples, which gives a 95% half-width of about ±4.2 pp for a per-class recall near 90%.
- **Labelling:** two experts label each ticket independently. Disagreements go to an adjudicator. Record Cohen's kappa between the two experts.
- **Population weighting:** stratified sampling over-represents small classes. To estimate overall accuracy for the real distribution, weight each class by its population share (for example, Billing 30%, Other 5%) divided by its sample share (1/6). Report both the weighted and unweighted numbers.

**Weaknesses of the crowd-labelled test set.**
1. **Noise lowers measured accuracy.** With about 15% noise, the measured accuracy of a perfect model would be well below 100%, and small improvements are hidden.
2. **Rewards copying crowd bias.** If the crowd systematically labels ambiguous tickets one way, a model that copies that bias scores higher. This can make the wrong model look better.
3. **Cannot measure the key confusions.** The Billing/Refund error cannot be measured on noisy labels.
4. **Unknown and changing noise.** Tier composition and noise may change over time, so the test noise rate is unknown.
5. **Possible leakage.** The test set uses the same process as training, so duplicates and template tickets may appear on both sides.

**Preventing leakage.**
- Deduplicate and cluster before splitting.
- Fit preprocessing (tokenisers, vocabularies, scalers) on training data only.
- Apply label corrections only to training data.
- Freeze the evaluation set and record its file hash. Access it only for final reporting.
- Use the validation set for hyperparameters, early stopping, and threshold choices.
- Keep the 200-ticket random baseline separate from the evaluation set, or document any overlap explicitly.

**Metrics and confidence intervals.**
- **Overall accuracy (population-weighted):** report with a Wilson or bootstrap CI.
- **Macro-F1:** the average of per-class F1 scores. Report a stratified bootstrap CI (resample within each class).
- **Per-class recall and precision:** especially for Billing and Refund, and for Other.
- **Confusion matrix:** check the Billing/Refund and Technical/Account Access cells.
- **Cohen's kappa** between model and expert gold labels.
- **Expected calibration error (ECE):** check whether predicted probabilities are reliable. This is relevant if the model's confidence is used for review selection.
- **Model comparison:** when comparing two models on the same test items, use McNemar's test on paired correct/incorrect outcomes, not an unpaired test.

**Sample size check.** For overall accuracy near 90%, a ±3 pp half-width needs about 385 tickets. The 1,200-ticket evaluation set gives a comfortable margin for that target.

## Estimates vs. Measured Facts

**Measured (direct calculation from given counts):**
- Audit noise 60/400 = 15.0%, Wilson CI [11.8%, 18.8%].
- Tier A 6.7%, Tier B 21.8%, and their CIs.
- Tier B minus Tier A = 15.2 pp, z = 4.22, p ≈ 2.4e-5.
- The 8 disagreement counts and their pair totals.

**Estimates (depend on assumptions):**
- Crowd noise 15.1% and whole-dataset noise 13.6%. These assume the audit is representative within each tier and that experts are correct.
- Per-class error rates. These use expected audited counts because actual per-class counts were not given.
- True accuracy 96.3% (range about 93% to 100%). This assumes uniform random label flips, independent of the model.
- The review-budget allocation. It is a design choice, not a measured result.

**Not yet known (must be measured with real data):**
- The precision of any selection method.
- How many errors the 2,000-ticket review actually finds.
- The expert time per ticket.
- The effect of corrections on model accuracy.
- The actual test-set noise rate.

## Limitations

- All numbers come from summary statistics, not ticket-level data.
- Audit samples are small, so per-class and per-tier estimates are wide.
- Expert labels are treated as the reference, but they may be wrong.
- The uniform flip assumption is contradicted by the observed confusion pattern.
- No model predictions or training runs were available, so no training results are reported.