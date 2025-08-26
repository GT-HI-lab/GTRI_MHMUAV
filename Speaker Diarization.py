import assemblyai as aai
import csv

#Step 1: replace your API key for Assembly AI
aai.settings.api_key = "957e21fc093d4d7f97d01d49e292500b"

# You can also transcribe a local file by passing in a file path
# FILE_URL = './path/to/file.mp3'
#Step 2: select your file (use the file directory if you store it somewhere on your laptop)
FILE_URL = 'file_name'

config = aai.TranscriptionConfig(speaker_labels=True)

transcriber = aai.Transcriber()
transcript = transcriber.transcribe(
  FILE_URL,
  config=config
)

transcription_count = 0

#Step 3: fill in the start time hour and minute
start_hour = 00
start_minute = 00

#Step 4: fill in output file name (how you want to name your excel file)
with open('output_name', 'w', newline='') as csvfile:
  fieldnames = ['Timestamp', 'Speaker', 'Transcription']
  thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
  thewriter.writeheader()

  for utterance in transcript.utterances:
    transcription_count += 1
    if start_minute + int(utterance.start/1000/60) < 60:
      time = f"{start_hour}:{start_minute + int(utterance.start/1000/60)}:{int((utterance.start/1000)%60)}"
    else:
      time = f"{start_hour + 1}:{start_minute + int(utterance.start / 1000 / 60) - 60}:{int((utterance.start / 1000) % 60)}"
    thewriter.writerow({'Timestamp': time, 'Speaker': utterance.speaker, 'Transcription': utterance.text})
    print(f"Timestamp {time}  Speaker {utterance.speaker}: {utterance.text}")
