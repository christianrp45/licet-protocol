---
title: "Literature Review — RMSSD Direction Reversal & Amusement False-Positive Rate in WESAD Validation"
type: scoping review
session: 25/09/2026
status: referência permanente — não modificar retroativamente
related: [../paper_vlp_outline.md Seção 6.4, ./results/wesad_summary.txt, ./wesad_experiment.py]
---

# Literature Review: RMSSD Direction Reversal & Amusement False-Positive Rate

Generated: 2026-09-25
Review type: scoping (exploratory — grounding two empirical anomalies before writing paper text, not a formal systematic protocol)
Search window: sources published up to 2026, no lower date bound
Databases: PubMed/PMC (via web search), Semantic Scholar/general web, arXiv, journal sites (Sensors, Psychophysiology, Frontiers, Biological Psychology)

## Research Question

Running `wesad_experiment.py` (LICET Layer 3 validated against the WESAD dataset,
Empatica E4 wrist device) produced two anomalies inconsistent with the protocol's
stated hypotheses (see `results/wesad_summary.txt`, H4 and H2):

1. **H4 failed in the wrong direction.** RMSSD (wrist-PPG derived) increased under
   acute stress (TSST) in 13/15 subjects (288.9ms baseline → 361.8ms stress,
   Wilcoxon p=0.0256), when literature (Thayer et al. 2012) predicts a decrease.
   A motion-artifact rejection gate (accelerometer-based, threshold = subject's
   own baseline median + 3×MAD) was implemented and did **not** fix the
   direction or reduce it — ruling out gross movement as the primary cause.
2. **H2 (specificity) underperformed.** ~48-50% of "amusement" windows (funny
   video clips — a non-coercive, positive state) were flagged as anomalous by
   the Mahalanobis D² detector, when the expected specificity was 70-85%.

Question: what does published literature say about (a) the reliability of
wrist-PPG-derived RMSSD under acute psychosocial/cognitive stress specifically
(not just gross motion), and (b) whether "amusement" is physiologically
expected to resemble "stress" in HR/HRV/EDA, i.e. whether the low specificity
is a known, documented confound rather than an implementation bug?

## Search Strategy

Exploratory web search (Google-indexed, weighted toward PubMed/PMC, Sensors,
Psychophysiology, Frontiers in Neuroscience, Biological Psychology) using the
following query lines:

- "wrist PPG photoplethysmography signal quality degradation sympathetic vasoconstriction stress heart rate variability"
- "RMSSD increase paradox wrist-worn PPG stress artifact false peak detection validation ECG"
- "RMSSD HF power systematic overestimation PPG parasympathetic effect size validation study wearable"
- "Trier Social Stress Test TSST wrist PPG wearable HRV accuracy ECG comparison RMSSD error"
- "Kreibig 2010 autonomic nervous system activity emotion review fear amusement physiological overlap"
- "How Do Amusement, Anger and Fear Influence Heart Rate and Heart Rate Variability Frontiers authors 2019"
- "Kreibig 2010 skin conductance electrodermal activity amusement joy fear anxiety comparison magnitude"
- "laughter electrodermal activity skin conductance response amusement physiological arousal burst"
- "WESAD dataset amusement stress misclassification confusion matrix Schmidt 2018 classifier accuracy"

Follow-up direct fetches were made against the highest-relevance hits to extract
exact figures and confirm citations (PMC full text, journal abstract pages).

## Inclusion / Exclusion

- Included: peer-reviewed journals, systematic reviews/meta-analyses, and the
  WESAD source paper itself.
- Excluded from citation (used only as discovery leads): patent filings,
  vendor blog posts (Medium/Analog Devices), unreviewed arXiv preprints not
  corroborated by a peer-reviewed source.
- Not independently re-verified against the primary dataset by this review —
  figures are as reported in the secondary/tertiary sources retrieved; flagged
  as such below.

## Evidence Summary

### Theme 1 — Wrist-PPG RMSSD reliability under stress/cognitive load

| Source | Design | Population/Data | Key finding | Confidence |
|---|---|---|---|---|
| Xu, Liu, Liu, Su & Gu (2026). *Sensors* 26(16):5192. "Accuracy of Photoplethysmography-Derived Pulse Rate Variability Compared with Electrocardiography-Derived Heart Rate Variability: A Systematic Review and Meta-Analysis." | Systematic review + meta-analysis | Multiple studies, PPG vs ECG-HRV | Pooled absolute standardized error for RMSSD = 0.188 (95% CI 0.066–0.309); RMSSD/HF particularly prone to error even after refined processing (δ≥0.474 in underlying studies). **Scope restricted to rest/controlled conditions — does not address acute stress.** | Medium (rest-only scope limits direct applicability) |
| Sinichi, Gevonden & Krabbendam (2025). *Psychophysiology* 62(2):e70004. "Quality in Question: Assessing the Accuracy of Four Heart Rate Wearables and the Implications for Psychophysiological Research." | Controlled multi-condition validation (rest, cognitive/arithmetic, recovery, postural, paced breathing, emotional go/no-go, ambulatory) | Empatica E4 (**same device as WESAD**) + 3 other wearables vs. ECG reference | RMSSD accuracy collapses under mental arithmetic (Empatica E4: r=0.31, MAAPE=87.98% vs. much better at rest) and emotional go/no-go (r=0.65, MAAPE=52.92%). Authors attribute this to "subtle movement, muscle contraction, and speech during verbal response" — **not gross movement**. | **High** — same hardware family as WESAD, directly analogous cognitive/arithmetic condition to the TSST arithmetic component |
| WESAD original paper — Schmidt, Reiss, Duerichen, Marberger & Van Laerhoven (2018). ACM ICMI. DOI: 10.1145/3242969.3242985 | Dataset paper | N=15, Empatica E4 (wrist) + RespiBAN (chest) | No explicit discussion found (via available excerpt) of RMSSD directionality under TSST for the wrist channel specifically; full-text access was PDF-structural only in this review pass, not fully parsed — **flagged as unverified, needs direct full-text confirmation before citing absence of discussion as a finding.** | Low (source not fully read) |

**Synthesis (Theme 1):** The most directly relevant and highest-confidence
source is Sinichi et al. (2025), because it tests the *identical* wearable
(Empatica E4) under a cognitive/arithmetic task that closely mirrors the
arithmetic component of the TSST, and explicitly attributes RMSSD error to
subtle muscular/speech artifact rather than gross motion. This is consistent
with — and explains — why our own accelerometer-magnitude motion gate
(calibrated on gross baseline movement, median+3×MAD) failed to correct the
RMSSD reversal: the artifact source described in the literature is sub-threshold
for a gross-motion detector. The broader meta-analysis (Xu et al. 2026)
independently confirms RMSSD/HF are the HRV metrics most prone to systematic
PPG error, though its scope is rest-only and does not itself establish the
stress-specific mechanism.

### Theme 2 — Physiological overlap between "amusement" and "stress/fear"

| Source | Design | Key finding | Confidence |
|---|---|---|---|
| Kreibig (2010). *Biological Psychology* 84(3):394–421. "Autonomic nervous system activity in emotion: A review." | Narrative meta-review (canonical, >2000 citations) | (a) HR/RMSSD pattern: "most negative emotions... increased HR and decreased HRV, while positive emotion had an ambivalent influence." (b) EDA/SCL/SCR: elevated by *both* positive (anticipatory pleasure, amusement) and negative (fear, anxiety, disgust, anger) high-arousal states — **EDA reflects arousal intensity, not valence.** | **High** — canonical reference, cross-corroborated by multiple secondary sources |
| Wu, Gu, Yang & Luo (2019). *Frontiers in Neuroscience* 13:1131. DOI: 10.3389/fnins.2019.01131. "How Do Amusement, Anger and Fear Influence Heart Rate and Heart Rate Variability?" | Controlled video-induction study, ECG | Amusement: HR **lower** (78.03 bpm) vs. anger/fear/neutral (82.03/82.73/83.88 bpm, not significantly different from each other); RMSSD **higher** in amusement (154.74ms) vs. fear (80.81ms), anger (111.46ms), neutral (91.42ms). Amusement activates the parasympathetic branch; on HR/RMSSD it resembles *relaxation*, not stress. | **High** — precise, recent, directly comparable emotion categories to WESAD's amusement/stress |
| Cross-domain WESAD classification literature (arXiv 2502.18733 and related; general finding echoed across multiple ML-on-WESAD papers) | ML benchmarking on WESAD | 3-class (baseline/stress/amusement) accuracy ≈80% vs. binary (stress/non-stress) ≈93% (Schmidt et al. 2018 original benchmark); amusement is explicitly noted as producing "subtle" physiological changes that drive misclassification in 3-class settings, even for population-level classifiers with far richer feature sets than LICET's 4-signal vector. | Medium — confirms amusement is a known hard case in WESAD specifically, though via a different mechanism (subtlety, not magnitude) than laid out below |

**Synthesis (Theme 2) — original hypothesis revised.** The initial working
hypothesis ("arousal ambiguity": amusement produces stress-like autonomic
*magnitude*, just with different valence) is **not well supported** on the
HR/RMSSD axis — Wu et al. (2019) shows amusement is *more* parasympathetic
than baseline/neutral, not less. The correct, better-supported mechanism is
narrower and specific to **EDA only**: Kreibig's canonical review establishes
that SCL/SCR is valence-blind by physiological design (sympathetically
innervated sweat glands respond to arousal intensity regardless of hedonic
tone). Since LICET's 4-signal Mahalanobis vector in this run includes EDA_SCL
but (absent cvxEDA) not EDA_SCR, and RMSSD — which *should* be the
valence-differentiating signal pulling amusement windows back toward baseline
— is independently unreliable via wrist-PPG under any autonomic perturbation
(Theme 1), the combination plausibly explains the observed ~48-50%
false-positive rate on amusement: the one signal that would correctly exonerate
amusement (RMSSD) is not functioning, while the one signal that cannot
distinguish it from stress by design (EDA) is functioning normally and
contributing genuine separation from baseline.

## Gaps and Limitations of This Review

- Not a formal systematic review: no pre-registered protocol, single-pass
  search, no independent dual screening, no full deduplication log.
- The WESAD original paper (Schmidt et al. 2018) was not fully read in this
  pass (PDF structural extraction failed) — the claim that it does not discuss
  amusement/stress physiological overlap is **unverified**, not confirmed absent.
  Recommend a direct manual read before finalizing paper text that relies on
  this point.
- No source in this review runs the WESAD dataset itself through an RMSSD
  pipeline and reports per-condition direction (increase/decrease) explicitly
  cross-referenced against ECG ground truth on the *same* subjects — the
  synthesis above combines evidence from different studies/devices (same
  device family, different populations) rather than a single controlled study
  that directly reproduces our exact finding.
- Xu et al. (2026) meta-analysis is rest-only in scope; it is cited to support
  the *general* unreliability of PPG-derived RMSSD, not the stress-specific
  mechanism, which rests primarily on the single Sinichi et al. (2025) study.

## References (full citations)

1. Xu, S., Liu, H., Liu, Z., Su, P., & Gu, Z. (2026). Accuracy of Photoplethysmography-Derived Pulse Rate Variability Compared with Electrocardiography-Derived Heart Rate Variability: A Systematic Review and Meta-Analysis. *Sensors*, 26(16), 5192. https://doi.org/10.3390/s26165192
2. Sinichi, M., Gevonden, M. J., & Krabbendam, L. (2025). Quality in Question: Assessing the Accuracy of Four Heart Rate Wearables and the Implications for Psychophysiological Research. *Psychophysiology*, 62(2), e70004.
3. Kreibig, S. D. (2010). Autonomic nervous system activity in emotion: A review. *Biological Psychology*, 84(3), 394–421.
4. Wu, Y., Gu, R., Yang, Q., & Luo, Y. (2019). How Do Amusement, Anger and Fear Influence Heart Rate and Heart Rate Variability? *Frontiers in Neuroscience*, 13, 1131. https://doi.org/10.3389/fnins.2019.01131
5. Schmidt, P., Reiss, A., Duerichen, R., Marberger, C., & Van Laerhoven, K. (2018). Introducing WESAD, a Multimodal Dataset for Wearable Stress and Affect Detection. *Proceedings of ICMI 2018*. https://doi.org/10.1145/3242969.3242985 (already in main reference list — cited here for the amusement/stress classification discussion)

## Search Log

| Database/Engine | Date | Query | Results used |
|---|---|---|---|
| Web search | 2026-09-25 | wrist PPG signal quality vasoconstriction stress HRV | context on posture/motion mechanisms |
| Web search | 2026-09-25 | RMSSD increase paradox wrist PPG stress artifact | led to Xu et al. 2026 meta-analysis |
| Web search + WebFetch | 2026-09-25 | RMSSD HF power systematic overestimation PPG | confirmed Xu et al. 2026 exact figures |
| Web search + WebFetch | 2026-09-25 | TSST wrist PPG HRV accuracy ECG | led to Sinichi et al. 2025 |
| WebFetch | 2026-09-25 | (direct fetch of Sinichi et al. 2025 PMC page) | per-condition RMSSD accuracy figures (arithmetic, go/no-go) |
| Web search | 2026-09-25 | Kreibig 2010 ANS emotion review | canonical citation + HR/RMSSD pattern summary |
| Web search + WebFetch | 2026-09-25 | Frontiers 2019 amusement anger fear HR HRV | Wu et al. 2019 exact figures |
| Web search | 2026-09-25 | Kreibig EDA amusement fear magnitude | valence-blindness of EDA confirmed |
| Web search | 2026-09-25 | WESAD amusement stress misclassification | Schmidt 2018 benchmark numbers, "subtle changes" framing |
