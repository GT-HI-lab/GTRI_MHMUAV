# MHMUAV — Machine-learning analyses of operator eye-tracking, conversation and physiological data

Analyses for the project on trust in multi-human multi-agent teams (two human operators, two simulated
UAVs). Feature-extraction steps turn raw recordings into block-level tables in `data/`; model notebooks start from
those tables.

## Study

- **Team:** Commander (CO) and Intelligence Support (IS) operator, both human; North and South UAVs, both simulated.
- **Task:** reconnaissance, surveillance and target acquisition. The UAVs scan adjacent areas and identify targets;
  operators monitor and veto incorrect identifications.
- **Design:** 3 (UAV reliability, within-subjects) × 2 (trust priming of the IS operator, between-subjects).
  Reliability order counterbalanced (Latin square). Final sample: 53 teams.
- **Measures:** eye tracking (Pupil Labs Neon; **Commander only**), conversation (audio, transcribed and time-aligned),
  PPG and EDA (EmotiBit), trust ratings (single-item and multi-dimensional trust after each block), synchronised via
  Lab Streaming Layer.
- **Seating:** The Commander sits closer to the North UAV display (left). The Intelligence Support sits closer to the South UAV display (right).

**UAV reliability by condition**

| Condition | North UAV | South UAV |
|---|---|---|
| High-High (HH) | 96% | 94% |
| Mixed (M) | 95% | 58% |
| Low-Low (LL) | 58% | 63% |

Feature-extraction files are numbered in the order they run. Model notebooks are numbered in the order they build on
each other (model 02 uses the stage-1 design from model 01). All notebooks are saved with their outputs.

## Feature extraction

| Step | File | Input | Output |
|---|---|---|---|
| 01 | `feature_extraction/01_eye_features.ipynb` | merged 25 Hz file `physio_eye_survey.csv` | `data/eye_features_by_block.csv` (eye features + Commander trust ratings) |
| 02a | `feature_extraction/02a_conversation_sentiment.R` | aligned utterance files `Audio_<ID>_aligned.csv` | `sentence_sentiment.csv` (sentence text + score; kept outside the repository) |
| 02b | `feature_extraction/02b_conversation_features.ipynb` | utterance files, `sentence_sentiment.csv`, block times from the 25 Hz file | `data/speech_features_by_block.csv` |

- **Eye tracking (Commander only):** 20 features per block — attention to each UAV display (dwell share, fixation rate
  and duration), gaze transitions between the displays (Cui et al., 2024; Krejtz et al., 2015), pupil, blinks, overall
  fixations, saccades. Fixed event filters adopted from the literature: fixations 80–4000 ms, saccades ≤ 120 ms.
- **Conversation (Commander and IS operator):** per speaker, amount of speech, overall sentiment, and sentiment and
  mentions of each UAV (keyword rule: north/left, south/right); team turn-taking. Text features use all utterances;
  timing features use only utterances whose aligned timing passed the checks (`usable`). Sentiment is scored per
  sentence with sentimentr, with "false positive/negative" scored as negative phrases.

## Models

| # | File | Question | Status |
|---|---|---|---|
| 01 | `models/01_reliability_eye_tracking.ipynb` | Can Commander eye tracking identify the reliability condition of a block? | early results |
| 02 | `models/02_trust_two_stage.ipynb` | Does conversation about each UAV add to eye tracking when predicting the Commander's trust in it? | early results |

### Model 01 — Reliability condition from eye tracking

- **Unit:** Commander × block; 45 Commanders with all three blocks (135 blocks).
- **Targets:** reliability condition (High-High / Mixed / Low-Low) and, secondarily, High-High vs Mixed.
- **Features:** 20 eye-tracking features, centered within each Commander.
- **Models compared:** baseline, logistic regression, random forest, XGBoost; nested cross-validation grouped by
  Commander; the simplest model within 0.02 balanced accuracy of the best is selected.
- **Interpretation:** permutation importance and SHAP values; feature-level linear mixed-effects models for claims about
  individual features.
- **Result:** logistic regression selected for both targets. 3-way balanced accuracy 0.816 (AUC 0.920; chance 0.333).
  High-High vs Mixed balanced accuracy 0.791 (AUC 0.805; chance 0.5). Low-Low blocks are recognised almost perfectly;
  errors are High-High ↔ Mixed confusions.

### Model 02 — Two-stage prediction of Commander trust

- **Unit and target:** Commander × block; 39 Commanders with eye tracking and conversation data (117 blocks);
  post-block trust in the North and South UAV (MDMT, 0–7).
- **Stage 1:** eye tracking → P(Low-Low) (logistic regression, as in model 01).
- **Stage 2:** linear regression on P(Low-Low) plus, for the UAV being rated, the sentiment of sentences mentioning it
  and how often it is mentioned, for the Commander and the IS operator (4 features).
- **Validation:** stage 1 is cross-fitted; all steps run inside outer folds grouped by Commander (10 repeats);
  permutation test (500 shuffles) for the gain from conversation.
- **Result (held-out R²):**

  | Target | Condition (oracle) | Stage 1 only | Stage 1 + conversation | Gain from conversation |
  |---|---|---|---|---|
  | Trust in North UAV | 0.53 | 0.46 | 0.42 | −0.05 (p = .87) |
  | Trust in South UAV | 0.50 | 0.24 | 0.35 | +0.11 (p = .002) |

  For South trust, conversation also predicts differences between Commanders within the same condition
  (beyond-condition r = 0.23), mostly through the IS operator's sentiment about the South UAV. Adding other
  conversation features (amount, overall sentiment, timing, AFINN, NRC-VAD) did not improve the model (exploratory).

## References

Full citations to be completed.

- Cui et al. (2024). Gaze transition entropy. *Scientific Reports*, 14, 23405.
- Dybvik et al. (2023); Enders et al. (2021); Jia & Du (2026); Long et al. (2024); Ries et al. (2026) — eye-movement event filters.
- Krejtz et al. (2015). Gaze transition entropy.
- Kret, M. E., & Sjak-Shie, E. E. (2019). Preprocessing pupil size data: Guidelines and code. *Behavior Research Methods*.
- Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words (NRC-VAD). *ACL*.
- Nielsen, F. Å. (2011). A new ANEW: Evaluation of a word list for sentiment analysis in microblogs (AFINN).
- Rinker, T. W. sentimentr: Calculate text polarity sentiment (R package).
