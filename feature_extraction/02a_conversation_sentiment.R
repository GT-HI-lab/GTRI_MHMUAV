# Feature extraction 02a — Sentence-level sentiment with sentimentr (run before 02b_conversation_features.ipynb)
#
# Input : aligned utterance files, Audio_<ID>_aligned.csv (one per team; not in the repository)
# Output: sentence_sentiment.csv next to the utterance files (contains transcript text; not in the repository)
#         one row per sentence: ID, row (utterance row in its team file, 0-based), sentence_id, speaker, sentence,
#         sentiment (sentimentr score; negative < 0 < positive)
#
# sentimentr (Rinker) scores sentences with the Jockers-Rinker lexicon and adjusts for valence shifters
# (negators such as "not", amplifiers, de-amplifiers, "but"). Default settings, with one task-specific change:
# "false positive(s)" / "false negative(s)" are scored as one negative phrase (-0.75). By default "false" (-0.6) and
# "positive" (+0.75) cancel, so "That is a false positive" came out slightly positive.

suppressPackageStartupMessages({
  library(sentimentr)
  library(dplyr)
})

BASE <- "/Users/debbiehsu/Documents/PythonProjects/GTRI_MHMUAV"
UTT_DIR <- file.path(BASE, "Audio", "Aligned")
OUT_PATH <- file.path(BASE, "Audio", "sentence_sentiment.csv")

EXCLUDE_TEAMS <- c(1, 2, 3, 7, 8, 9, 11, 13, 47, 50, 51, 53, 59)
SPEAKERS <- c("commander" = "C", "intelligence support" = "IS", "intelligent support" = "IS")

files <- list.files(UTT_DIR, pattern = "^Audio_\\d+_aligned\\.csv$", full.names = TRUE)
utt <- bind_rows(lapply(files, function(f) {
  d <- read.csv(f, check.names = FALSE, stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM")
  data.frame(ID = d$ID, row = seq_len(nrow(d)) - 1,            # same row index as 02b_conversation_features.ipynb (0-based)
             speaker = unname(SPEAKERS[tolower(trimws(d$Speaker))]),
             text = as.character(d$Transcription), stringsAsFactors = FALSE)
}))
utt <- utt %>% filter(!ID %in% EXCLUDE_TEAMS, !is.na(speaker), !is.na(text), nchar(trimws(text)) > 0)
cat(length(files), "team files |", nrow(utt), "Commander/IS utterances after exclusions\n")

TASK_PHRASES <- data.frame(x = c("false positive", "false positives", "false negative", "false negatives"),
                           y = -0.75)
key <- update_key(lexicon::hash_sentiment_jockers_rinker, x = TASK_PHRASES)

sentences <- get_sentences(utt$text)
scores <- sentiment(sentences, polarity_dt = key)               # one row per sentence
out <- utt[scores$element_id, c("ID", "row", "speaker")]
out$sentence_id <- scores$sentence_id
out$sentence <- unlist(sentences)
out$sentiment <- scores$sentiment
out <- out[grepl("[A-Za-z]", out$sentence), ]
write.csv(out, OUT_PATH, row.names = FALSE)
cat("saved", OUT_PATH, "|", nrow(out), "sentences\n")
