# Noisy Labels: HelpDeskNet-50K Analysis

## 1. Introduction

HelpDeskNet-50K is a fictional set of 50,000 customer-support tickets across 6 categories. Adding more training to the model has not further increased its test accuracy of 82%. A possible explanation could be mistakes in the data labels.

This report summarizes the available audit statistics, discusses typical labeling mistakes, and quantifies their potential impact on model accuracy. It also suggests a strategy to review labels by experts, train models robustly, and evaluate models reliably.

**Scope:** This analysis is based on the statistics from GitHub Issue 9 and the results from running `noise_analysis.py`. The original ticket records and model predictions were not available. Thus, statistics based on the audit counts are measured statistics, while population-level noise and true accuracy are estimates.

## 2. Milestone 1 — Quantifying Label Noise

Out of 400 randomly selected crowd-labeled tickets, 60 disagreed with the experts.

\[
\text{Noise rate}=\frac{60}{400}\times100=15\%
\]

The Wilson 95% confidence interval is 11.8%–18.8%.

### Tier comparison

| Crowd tier | Disagreements | Noise rate | 95% confidence interval |
|---|---:|---:|---:|
| Tier A | 12/180 | 6.7% | 3.9%–11.3% |
| Tier B | 48/220 | 21.8% | 16.9%–27.7% |

The error rate of Tier B is about 3.3 times the error rate of Tier A. The difference is 15.2 percentage points, with a 95% confidence interval of 8.6–21.7 percentage points.

A pooled two-proportion z-test gives \(z=4.22\) and \(p=2.42\times10^{-5}\). The p-value is very small, so if the audit samples are representative, the difference is unlikely to be due to random sampling variation alone.

### Estimating noise in the entire dataset

The crowd-labeled population has 20,000 Tier A tickets and 25,000 Tier B tickets. Their population weights are:

\[
w_A=\frac{20000}{45000}=0.444
\]

\[
w_B=\frac{25000}{45000}=0.556
\]

Using the tier-specific noise rates:

\[
\text{Crowd noise}=0.444(6.7\%)+0.556(21.8\%)
\]

The estimated noise rate for crowd-labeled tickets is 15.1%, with a 95% confidence interval of 11.6%–18.5%.

Crowdworkers labeled 45,000 of the 50,000 tickets. If the remaining 5,000 expert-labeled tickets are assumed correct:

\[
\text{Overall noise}=0.9(15.1\%)\approx13.6\%
\]

The estimated noise for the whole dataset is 13.6%, with an approximate confidence interval of 10.5%–16.7%.

These estimates are based on the assumption that the audit is representative of each tier and that the expert labels are accurate. Even experts can make errors, so the actual noise rate might differ.

## 3. Milestone 2 — Characterizing Label Noise

Errors are concentrated in certain pairs of categories, as indicated by the disagreement counts.

| Confusion pair | Errors | Share of disagreements |
|---|---:|---:|
| Billing ↔ Refund | 26 | 43.3% |
| Technical ↔ Account Access | 15 | 25.0% |
| Shipping ↔ Other | 11 | 18.3% |
| Technical ↔ Other | 5 | 8.3% |
| Billing ↔ Other | 3 | 5.0% |

The two largest pairs account for 41 of the 60 disagreements (68.3%). The audit shows only 8 of the 30 possible directed class-confusion pairs. This pattern suggests systematic mislabeling rather than uniformly random errors.

A ticket relating to a duplicate payment or a refund could be labeled Billing or Refund. Likewise, if a package is missing and a refund request is included, it could be classified as Shipping or Refund.

The approximate class-wise error rates obtained from `noise_analysis.py` are:

| Class | Estimated error rate |
|---|---:|
| Billing | 14.2% |
| Refund | 20.0% |
| Technical | 14.0% |
| Account Access | 10.0% |
| Shipping | 20.0% |
| Other | 15.0% |

These are approximate estimates because the audit does not provide exact audited counts for each class. Expected counts based on the dataset's class distribution were used.

### Probable causes and improvements

The potential causes are unclear boundaries between categories, incomplete annotation guidelines, and differences in workers' experience. However, the audit cannot determine the exact cause.

**Recommended actions:**

1. Explain the difference between Billing and Refund, as well as Technical and Account Access.
2. Define when the Other category should be used and include examples of tickets that could fall into more than one category.
3. Have Tier B workers complete a qualification test based on expert-labeled samples.
4. Place gold-standard tickets into annotation batches and monitor each individual worker's accuracy.
5. Use Cohen's kappa for two annotators or Fleiss' kappa for multiple annotators to measure agreement.
6. Refer disputed tickets to an expert for adjudication and revise the guidelines based on the findings.
7. Make sure the full conversation is available to workers and not just the first message.

## 4. Milestone 3 — Estimating the Accuracy Ceiling

The model performs at 82% accuracy on a test set labeled using the same crowd process. To estimate how close it might be to the correct labels, assume that 15% of the labels are independently flipped, uniformly across the remaining five classes.

Let \(t\) represent the model's true accuracy and \(e=0.15\) represent the label-flip rate.

The observed prediction can match the noisy label in two cases: the original label is correct and the model prediction is correct, or the label is flipped and the model prediction matches that incorrect label.

Therefore:

\[
A_{\text{observed}}=(1-e)t+\frac{e}{5}(1-t)
\]

Substituting the values:

\[
0.82=0.85t+0.03(1-t)
\]

\[
t=\frac{0.82-0.03}{0.85-0.03}
=\frac{0.79}{0.82}
\approx0.9634
\]

Given this assumption, the estimated true accuracy is about 96.3%.

### Why this estimate might not be accurate

- **Label flips are not necessarily random:** Billing and Refund are often mixed up.
- **Shared biases:** The model could learn the same biases as crowdworkers.
- **Unknown test noise:** The overall crowd-noise estimate from the audit is not the exact noise rate in the test set.
- **Imperfect expert labels:** The audit assumes expert labels are correct, but experts may also make mistakes.
- **Class imbalance:** Overall accuracy can hide poor performance on smaller classes such as Other.

The audit's noise confidence interval also produces an infeasible upper endpoint under this model. At a flip rate of 18.8%, the maximum possible observed accuracy would be 81.2%, which is below the reported 82%. At a noise rate of 18.0%, the implied true accuracy reaches 100%. Therefore, the approximate feasible sensitivity range is 92.8%–100%, but this is not a formal confidence interval for true accuracy.

The 96.3% result is a theoretical estimate, not verified model performance. Evaluation against expert-labeled data is required.

## 5. Milestone 4 — Selecting Tickets for Expert Review

Milestone 4 requires selecting 2,000 tickets to be reviewed by an expert.

With only 2,000 additional tickets that experts can handle, the selection process must balance the possibility of finding mistakes with a random sample for comparison.

| Selection strategy | Tickets | Description |
|---|---:|---|
| Model uncertainty | 600 | Choose tickets where the two highest predicted probabilities are close. |
| Confident model-label disagreement | 500 | Identify tickets where the model strongly disagrees with the current label. |
| Suspicious or influential examples | 500 | Prioritize known confusion pairs, Tier B tickets, and high-loss examples. |
| Minority-class coverage | 200 | Add around 100 Other and 100 Shipping tickets. |
| Random baseline | 200 | Estimate the error rate without model-based selection. |
| **Total** | **2,000** | |

Use out-of-fold predictions for model-based selection where possible.

### Planning the selection process

An expert should record whether each reviewed label is incorrect. Let \(r\) be the error rate in a random sample and \(p_{\text{flag}}\) be the error rate among flagged tickets.

\[
\text{Selection lift}=\frac{p_{\text{flag}}}{r}
\]

If there are more errors among flagged tickets than in the random sample, the selection lift will be greater than 1. Report confidence intervals, compare error rates using a two-proportion test or Fisher's exact test, and calculate confirmed corrections per expert-review hour.

The error-rate estimate for the baseline may not be precise because it contains only 200 tickets. This uncertainty should be considered when interpreting the results.

### Using corrected labels

1. For each ticket, enter the ticket number, original label, expert label, reason for correction, the person who corrected it, and the date.
2. Settle disputes through expert adjudication.
3. Correct labels only in the training data.
4. Retrain using the same hyperparameters and at least three random seeds.
5. Evaluate performance on an independent expert-labeled set that is not part of training or label correction.
6. Evaluate the original and retrained models on the same evaluation examples.

This process will show whether label correction improves performance rather than assuming it will.

## 6. Milestone 5 — Noise-Robust Training and Reliable Evaluation

### Noise-robust training methods

#### 1. Generalized Cross-Entropy (GCE)

GCE uses the loss:

\[
L_q=\frac{1-p_y^q}{q}
\]

Here, \(p_y\) represents the model's predicted probability for the provided label, and \(q\) is a value between 0 and 1. Unlike standard cross-entropy, GCE can reduce the influence of some high-loss examples, such as mislabeled tickets. A value such as \(q=0.7\) can be tried.

#### 2. Co-teaching

Two networks are initialized differently and trained together. Each network selects examples with small losses from a mini-batch and feeds them to the other network for training. This can help reduce the impact of noisy labels because clean examples may have lower losses during the early stages of training. The forget rate can be increased toward the estimated noise rate and fine-tuned using expert-reviewed results.

Both approaches need to be tested in practice; their performance on HelpDeskNet-50K is not yet known.

### Constructing a trustworthy evaluation set

Create an independent evaluation set of 1,200 expert-vetted tickets, with 200 tickets for each of the six classes.

- Get two experts to label each ticket independently.
- Resolve conflicts between annotations and measure inter-annotator agreement using Cohen's kappa.
- Keep the evaluation set separate from training, label correction, and hyperparameter tuning.
- Remove exact and near-duplicate tickets before splitting the remaining data. Keep related tickets or conversation threads in the same split to reduce data leakage.
- Use the validation set for hyperparameter tuning, model selection, and early stopping.
- With 200 examples per class, the approximate 95% margin of error for a class recall near 90% is ±4.2 percentage points.
- Since the evaluation set is balanced by class, report both unweighted metrics and population-weighted accuracy to reflect the actual class distribution.

### Why the existing crowd-labeled test set is problematic

The test set is labeled by the crowd in the same manner as the training set. Errors can compromise measured accuracy, encourage the model to learn annotation errors, and hide important errors in particular categories. The actual noise rate in the test set is also unknown, and duplicate or template-based tickets can cause leakage between data splits.

Deduplicate before splitting, fit preprocessing steps on the training set only, and keep the expert-labeled evaluation set separate and fixed for final reporting.

### Recommended metrics

Report:

- Population-weighted accuracy with a confidence interval.
- Macro-F1 with a stratified bootstrap confidence interval.
- Per-class precision and recall, especially for Billing, Refund, and Other.
- A confusion matrix to identify frequent category errors.
- Cohen's kappa statistic between predicted and expert labels.
- Expected Calibration Error (ECE) to assess prediction confidence.
- McNemar's test to compare two models on the same test examples.

At an expected accuracy of 90%, approximately 385 independent samples are needed for a ±3 percentage-point margin of error at 95% confidence, using a normal approximation. The proposed 1,200-ticket evaluation set provides 200 examples per class, but stratification and the sampling design should be considered when calculating uncertainty.

## 7. Conclusion and Limitations

The audit shows a 15.0% disagreement rate among the sampled crowd-labeled tickets. Most of the observed errors occur between a limited set of related categories, and Tier B is significantly noisier than Tier A. These results can help guide better annotation guidelines, expert review, and quality checks for workers.

The proposed 2,000-ticket review combines model-based selection with a random baseline. Another way to reduce the effect of remaining noise is to try Generalized Cross-Entropy loss and Co-teaching. A separate expert-labeled evaluation set would provide a more reliable assessment of model performance.

The analysis is based on summary statistics rather than original tickets and model predictions. Population noise, class-specific rates, and the 96.3% true-accuracy estimate rely on assumptions and have not been experimentally confirmed. The effects of label correction and training under noisy conditions have not yet been quantified.