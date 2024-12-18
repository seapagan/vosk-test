import os
import wave
import json
from vosk import Model, KaldiRecognizer

# Path to the Vosk model (unpacked directory)
model_path = "vosk-model-en-us-0.22"

# Path to the audio file (16-bit PCM WAV format, mono)
audio_file = "rec1.wav"

# Load Vosk model
if not os.path.exists(model_path):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack it.")
    exit(1)

model = Model(model_path)

# Open audio file
wf = wave.open(audio_file, "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print("Audio file must be WAV format Mono PCM.")
    exit(1)

# Recognize speech using Vosk
rec = KaldiRecognizer(model, wf.getframerate())

# Process audio and output text incrementally
print("Transcription (word by word):")
while True:
    data = wf.readframes(4000)  # Process audio in chunks
    if len(data) == 0:
        break

    if rec.AcceptWaveform(data):  # Finalized chunks
        result = json.loads(rec.Result())
        print(result["text"])  # Print finalized text chunk
    else:  # Partial results for incremental text
        partial_result = json.loads(rec.PartialResult())
        print(partial_result["partial"], end="\r", flush=True)  # Print partial result in-place

# Final result
final_result = json.loads(rec.FinalResult())
print("\nFinal Transcription:")
print(final_result["text"])
