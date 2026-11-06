# GTRI_MHMUAV
## Machine-learning analyses of operator eye-tracking and physiological data

Analyses for the GTRI IRAD project on trust in multi-human multi-agent teams (two human operators, two simulated
UAVs). Each analysis is a numbered notebook; shared data products live in `data/`.

> Status: work in progress, shared for collaboration. 

## Study

- **Team:** Commander and Intelligence Support operator, both human; North and South UAVs, both simulated.
- **Task:** reconnaissance, surveillance, and target acquisition. The UAVs scan adjacent areas and identify targets;
  operators monitor and veto incorrect identifications.
- **Design:** 3 (UAV reliability, within-subjects) × 2 (trust priming of the Intelligence Support operator, between-subjects).
- **Participants:** 53 teams (N = 106)
- **Measures:** eye tracking (Pupil Labs Neon; **Commander only**), PPG and EDA (EmotiBit), trust ratings (single-item
  and multi-dimensional trust after each block), synchronised via Lab Streaming Layer.
- **UAV reliability by condition** (Order counterbalanced)

| Condition | North UAV | South UAV |
|---|---|---|
| High-High (HH) | 96% | 94% |
| Mixed (M) | 95–96% | 58% |
| Low-Low (LL) | 58% | 63% |

## Analyses

| # | Notebook | Question | Input | Status |
|---|---|---|---|---|
| 01 | `01_eye_feature_extraction.ipynb` | Summarise Commander eye tracking per block | raw merged file (not in repo) | done |
| 02 | `02_reliability_classification.ipynb` | Can Commander eye tracking identify the reliability condition of a block? | `data/eye_features_by_block.csv` | early results |

A short summary of each analysis follows below; full methods, outputs and limitations are in the notebooks, which are
saved with their outputs.

### 02 — Reliability classification from eye tracking

- **Unit:** Commander × block; 45 Commanders with all three blocks (135 blocks).
- **Targets:** reliability condition (High-High / Mixed / Low-Low) and, secondarily, High-High vs Mixed.
- **Features:** 20 eye-tracking features, centered within each Commander.
- **Models compared:** baseline, logistic regression, random forest, XGBoost.
- **Model selection:** simplest model within 0.02 balanced accuracy of the best.
- **Interpretation:** permutation importance and SHAP values; feature-level linear mixed-effects models for statistical
  claims about individual features.
- **Result:** logistic regression selected for both targets. 3-way balanced accuracy 0.816 (AUC 0.920; chance 0.333).
  High-High vs Mixed balanced accuracy 0.791 (AUC 0.805; chance 0.5). Low-Low blocks are recognised almost perfectly;
  errors are mostly High-High ↔ Mixed confusions.

## References

Full citations to be completed.

- Cui et al. (2024). Gaze transition entropy. *Scientific Reports*, 14, 23405.
- Dybvik et al. (2023); Enders et al. (2021); Jia & Du (2026); Long et al. (2024); Ries et al. (2026) — eye-movement event filters.
- Krejtz et al. (2015). Gaze transition entropy.
- Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods*.
