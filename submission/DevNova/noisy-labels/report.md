# Noisy Labels: HelpDeskNet-50K Analysis

## 1. Introduction

HelpDeskNet-50K is a fictional set of 50,000 customer-support tickets across 6 categories. Adding more training to the model has not further increased its test accuracy of 82%. A possible explanation could be mistakes in the data labels.

This report summarizes the audit statistics available, discusses typical labeling mistakes, and quantifies their potential impact on model accuracy, and suggests a strategy to review models by experts, train models robustly and evaluate models reliably.

**Scope:** This analysis is based on the statistics from GitHub Issue 9, and the results from running noise_analysis.py. The original ticket records and model predictions were not available. Thus, statistics based on the audit count are measured, noise and true accuracy are estimated.

Label noise is quantified.Label noise is quantified in Milestone 1.

Out of 400 tickets that were randomly selected and labeled by the crowd, 60 disagreed with the experts.Of 400 randomly selected crowd labeled tickets, 60 disagreed with the experts.

\[
\text{Noise rate}=\frac{60}{400}\times100=15\%
\]

The Wilson 95% confidence interval is 11.8%–18.8%.

### Tier comparison

| Crowd tier | Disagreements | Noise rate | 95% confidence interval |
|---|---:|---:|---:|
| Tier A | 12/180 | 6.7% | 3.9%–11.3% |
| Tier B | 48/220 | 21.8% | 16.9%–27.7% |

The error rate of Tier B is about 3.3 times the error rate of Tier A. The difference is 15.2 percentage points and has a 95% confidence interval of 8.6–21.7 percentage points.

A pooled two-proportion z-test gives \(z=4.22\) and \(p=2.42\times10^{-5}\). The p-value is very small, so if the audit samples are representative, the difference is not likely to be due to random sampling variation alone.

### Estimating noise in the entire data set

The crowd labelled population has 20,000 Tier A tickets and 25,000 Tier B tickets. Population weights of their:

\[
w_A=\frac{20000}{45000}=0.444
\]

\[
w_B=\frac{25000}{45000}=0.556
\]

Discuss the advantages/disadvantages of using the tier-specific noise rates:

\[
\text{Crowd noise}=0.444(6.7\%)+0.556(21.8\%)
\]

The noise rate estimated from the crowd is 15.1% (95% CI 11.6%–18.5%).

50,000 tickets were labeled by crowdworkers, of which 45,000 were labeled. If the remaining 5000 (expert labeled) tickets are assumed correct:

\[
\text{Overall noise}=0.9(15.1\%)\approx13.6\%
\]

The noise estimated for the whole-dataset is 13.6%, and the approximate confidence interval for the noise is 10.5%–16.7%.

These estimates are based on the assumption that the audit is representative of each of the tiers and that the expert labels are accurate. Even expert personnel can make errors, and the actual noise rate might not match.

## Milestone 2: Characterizing Label Noise.

Errors are localized in certain pairs of categories, as indicated by the disagreement counts.

| Share of confusions | Confusion pair | Share of disagreements | Errors |
|---|---|---:|---:|
| Billing ↔ Refund | 26 | 43.3% | |
| Technical ↔ Account Access | 15 | 25.0% | |
| Shipping ↔ Other | 11 | 18.3% | |
| Technical ↔ Other | 5 | 8.3% | |
| Billing ↔ Other | 3 | 5.0% | |

Two of the largest pairs each have 41 of the 60 disagreements (68.3%). The audit shows only 8 of the 30 possible pairs of directed class-confusion. This pattern is indicative of systematic mislabeling and not of uniformly random errors.

A ticket relating to a duplicate payment or a refund could be called Billing/Refund. Likewise, if a package is missing and a refund request is included then it can be considered Shipping or Refund.

Are the approximate class-wise error rates obtained from `noise_analysis.py` as follows:

| Class | Error rate of % |
|---|---:|
| Billing | 14.2% |
| Refund | 20.0% |
| Technical | 14.0% |
| Account Access | 10.0% |
| Shipping | 20.0% |
| Other | 15.0% |

These are approximate counts, as the audit is not giving exact audited counts for each class and expected counts based on the distribution of the size of the dataset were used.

### Probable causes/improvements

The potential sources are: unclear boundaries between categories, lack of complete guidelines for annotation, and experience of the workers. But the audit can't determine the exact cause.

**Recommended actions:**

To explain the difference between Billing and Refund as well as Technical and Account Access.

2. Use the Other category when it is appropriate and include some examples of tickets that could fall into more than one category.

3. Have Tier B workers complete a qualification test based on expert-labelled samples.

4. Place gold standard tickets into annotation batches and keep an eye on the accuracy of each individual worker.

Cohen's kappa or Fleiss' kappa for two or more annotators, respectively, to measure agreement.

6. Refer disputed tickets to an expert for adjudication and revise and adjust guidelines based on the findings.

7. Make sure that the whole conversation is available to the workers and not just the first message.

## 4. Milestone 3 — Estimate the Accuracy Ceiling

The model performs at 82% accuracy on a separate test set which was labeled using the same crowd process. How close do you think it might be to the correct labels, using the assumption that 15% of the labels are tossed up, uniformly across the remaining 5 classes?

Assume the model is actually accurate with accuracy parameter \(t\) and that the number of label flipouts is 0.15 with parameter \(e\).

In the case of the observed prediction matching the noisy label, the two situations that can occur are: either the original label is correct and the model is correct, or the original label is incorrect but the model's prediction is correct.

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

### The reason why this estimate might not be accurate.

- Label flips are not necessarily random: Systematic errors – Billing and Refund are often mixed up.
- Biases learned as a group: The model could learn the same biases as crowdworkers.
- The following are unknown test noise: The overall rating of crowd noise is the audit estimate, not the exact noise rate from the test set.
- Imperfect expert labels: The audit assumes that the expert labels are the standards, but they may also be incorrect.
- Class imbalance: It can be very difficult to be accurate on the smaller classes (e.g., Other).

Under this model, the noise confidence interval for the audit also yields an infeasible upper endpoint: The maximum amount of accuracy that can be observed in the audit for this flip rate is 81.2%, which is less than the reported 82%. The true accuracy is 100% when the implied accuracy is 18.0%. Therefore, the approximate range of this sensitivity is 92.8% to 100% and this does not constitute a formal Confidence interval of the true accuracy.

The percentage of 96.3% is a theoretical estimate, and not the performance of the verified model. Evaluation to expert labeled data is required.

For Milestone 4 you will have to select 2000 tickets to be evaluated by the expert.At Milestone 4 you need to choose 2,000 tickets to look at in detail by the expert.

With only 2,000 additional tickets being able to be handled by the experts, the selection process must be a compromise between the possibility of mistakes and taking a sample for comparison with the others.

| Selection strategy | Tickets | Description |
|---|---:|---|
| A 10 pound note is issued for each ticket | 10 | To pay for the prizes |
| Model uncertainty | 600 | Choose tickets that are as close together as possible between the highest two predictions. |
| Identify tickets where there is a strong disagreement between the model and current label | 500 | |
| Known confusion pairs | Suspicious or influential examples | 500 | |
| Minority class coverage | 200 | Add around 100 Other and 100 Shipping tickets. |
| Without model based selection estimate error rate | 200 | Random baseline |
| Total | 2,000 | |

Use out of fold prediction for model-based selection, when possible.

### Planning the selection process,

Each of the labels to be reviewed is to be noted if they are incorrect by an expert. Suppose that the error rate in a random sample is r, and the error rate in flagged tickets is p_flag.Suppose the percentage of errors in a random sample is r and the percentage of errors in flagged tickets is p_flag.Suppose that we let \(r\) be the error rate in a random sample, and let \(p_{\text{flag}}\) be the error rate among the flagged tickets.

\[
\text{Selection lift}=\frac{p_{\text{flag}}}{r}
\]

If there are more errors on the flagged tickets than there are in a "random sample", it will be a lift greater than 1. Evaluate and report intervals; compare error rates using a two-proportion test or Fisher's exact test; and calculate confirmed corrections/expert-review hour.

The error-rate estimate for the baseline is not necessarily accurate as only 200 tickets are in the random baseline. This uncertainty should be considered when analysing the results.

### Using corrected labels

For each ticket, enter the ticket number, original label, expert label, reason for correction, the person who corrected it and the date.

2. Settle disputes by arbitration.

3. Only label training data.

Retrain using the same hyper parameters and 3 or more random seeds.

5. Evaluate performance on an independent set of experts to which is the data of experts that is not part of the training set.

8. Use the same test examples to evaluate original and trained model.

This process will show whether the label correction process will yield better performance or not – as opposed to assuming it will.

## Milestone 5 — Noise Robust Training and Reliable Evaluation

### Noise-robust training methods

#### 1. Generalized Cross-Entropy (GCE)

GCE uses the loss:

\[
L_q=\frac{1-p_y^q}{q}
\]

The label \(p_y\) represents the likelihood that the label is supplied and \(q\) is a number between 0 and 1. Unlike standard cross entropy, GCE does not suffer from the effect of some of the examples of high losses, like mislabeled tickets. A value, like \(q=0.7\) can be tried.

#### 2. Co-teaching

Training two networks, which are initialized differently. Each network chooses the examples which have small loss with mini-batch and feeds them to the other network for training. This can be a way to mitigate the effects of noisy labels, since clean examples might not suffer as much from losses early in training. The forget rate can be incrementally increased to the estimated noise rate, and fine-tuned based on expert reviewed results.

Both solutions have to be tested in the real world; and indeed, their behavior in HelpDeskNet-50K is unknown.

### Constructing a trustworthy evaluation set

Create an independent evaluation set for 6 classes: 1200 expert vetted tickets.

- Get two experts to independently mark each ticket.
- Handle conflicts between annotations, and test inter-annotator agreement (Cohen's kappa).
- Separate the evaluation ticket from the training and label correction and hyperparameter tuning.
- Do not split or duplicate any tickets before the deduplication, preferably assign related tickets, or conversation threads to one group.
- Due to the number of examples in each class (200), the approximate 95% margin of error for a class recall near 90% is ±4.2 percentage points.
- An evaluation set is balanced by class: Report unweighted and population-weighted accuracy to reflect the actual class distribution of the evaluation set.

### Existing crowd labeled test set is problematic because:

The test set is also labeled by the crowds in the same manner as the training set. Errors can compromise measured accuracy, can lead to category modeling of errors, and can mask important errors in categories. The actual noise rate is also not known and duplicate/ticket template tickets can result in noise leaking between data splits.

Deduplicate before splitting, only do preprocessing on the training set, and freeze the evaluation set (caution) Tune hyperparameters, select models and use early stopping on a validation set. Do not split the labeled evaluation set and remove exact/near duplicate tickets from the evaluation set prior to splitting.

### Recommended metrics

Report:

- Accuracies weighted by population and with a confidence interval.
- Stratified bootstrap confidence interval, Macro-F1.
- Other per class precision and recall for per class Billing, Refund, Other.
- A confusion matrix to see frequent category errors.
- Cohen's kappa statistic for predicted and expert labels.
- Expected Calibration Error (ECE): To assess how confident the prediction is.
- McNemar's test is used for comparing two models using the same test examples.

The script determines this to be approximately 385 independent examples with 90% confidence and a margin of error of ±3%. There are more supports for wider classes for the proposed 1,200 ticket evaluation set, and stratification and sampling design may have to be considered when calculating uncertainty.

## Conclusion and Limitations

The audit shows 15.0% disagreement rate between the sampled crowd-labeled tickets. Most of the errors observed are between a limited set of related categories, and Tier B is significantly noisier than Tier A. These results can help to provide guidance for better annotation guidelines, expert review, and quality checks by workers.

The developed 2000 ticket review is a mix between model-based selection and a random baseline. Another path to minimize the effect of the leftover noise is via a generalized Cross-Entropy loss and Co-teaching, and a separate set of data would be more reliable for assessing the performance of the model.

The analysis is based on summary statistics instead of original tickets and model predictions. Population noise, class-specific rates and true-accuracy of 96.3% are based on assumptions and are not experimentally confirmed. To date, the effect of label correction and training under noisy conditions have not been quantified.