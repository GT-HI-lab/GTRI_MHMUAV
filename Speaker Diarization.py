import assemblyai as aai
import csv
import os

# Parameters - Change these for each run
PARTICIPANT_ID = "participant_ID"
CONDITION = "High/Low"

# Step 1: replace your API key for Assembly AI
aai.settings.api_key = "957e21fc093d4d7f97d01d49e292500b"

# Step 2: select your file
FILE_URL = "file_path"

config = aai.TranscriptionConfig(speaker_labels=True)

transcriber = aai.Transcriber()
transcript = transcriber.transcribe(FILE_URL, config=config)

transcription_count = 0

# Step 3: fill in the start time hour and minute
start_hour = 00
start_minute = 00

# Step 4: Create output file path
output_file = os.path.join(os.path.expanduser("~"), "Downloads", f"Audio_{PARTICIPANT_ID}.csv")

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    # Updated fieldnames to include ID and Condition
    fieldnames = ['ID', 'Condition', 'Timestamp', 'Speaker', 'Transcription']
    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    thewriter.writeheader()

    for utterance in transcript.utterances:
        transcription_count += 1
        if start_minute + int(utterance.start / 1000 / 60) < 60:
            time = f"{start_hour}:{start_minute + int(utterance.start / 1000 / 60)}:{int((utterance.start / 1000) % 60)}"
        else:
            time = f"{start_hour + 1}:{start_minute + int(utterance.start / 1000 / 60) - 60}:{int((utterance.start / 1000) % 60)}"

        thewriter.writerow({
            'ID': PARTICIPANT_ID,
            'Condition': CONDITION,
            'Timestamp': time,
            'Speaker': utterance.speaker,
            'Transcription': utterance.text
        })

        print(
            f"ID: {PARTICIPANT_ID}, Condition: {CONDITION}, Timestamp {time}, Speaker {utterance.speaker}: {utterance.text}")

print(f"\nTranscription complete! CSV file saved as: {output_file}")
print(f"Total utterances processed: {transcription_count}")