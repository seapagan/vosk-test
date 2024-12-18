# File is from the vosk package

import argparse
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json

q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# Parse arguments
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-l", "--list-devices", action="store_true", help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)

parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[parser]
)
parser.add_argument("-f", "--filename", type=str, metavar="FILENAME", help="audio file to store recording to")
parser.add_argument("-d", "--device", type=int_or_str, help="input device (numeric ID or substring)")
parser.add_argument("-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument("-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

# Main logic
try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        args.samplerate = int(device_info["default_samplerate"])

    model = Model(lang=args.model if args.model else "en-us")

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    full_transcript = []  # Store all finalized results

    with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device,
                           dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)

        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                print(text, end=" ", flush=True)
                full_transcript.append(text)  # Store finalized text

            if dump_fn is not None:
                dump_fn.write(data)

except KeyboardInterrupt:
    print("\n\nFinal Complete Transcript:")
    print(" ".join(full_transcript))
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))
