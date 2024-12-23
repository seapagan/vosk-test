# Speech To Text Experiments

Just some experiments with speech to text using the `vosk` package and models.
Vosk is not as accurate as `Whisper`, but transcription is a lot faster. I'll be
looking at the `fast-whisper` package later too.

## Installation

```bash
uv sync
source .venv/bin/activate
```

You also need to download a suitable`vosk` model. The model should be extracted
in it's own named folder in the root of the repository. You can get the models
from the [vosk website](https://alphacephei.com/vosk/models).

> [!NOTE]
>
> It should be possible to pass the resulting transcribed result through another
> model like [recasepunc](https://github.com/benob/recasepunc) to end up with a
> properly punctuated and cased string. This is something to look into adding
> later.

## Files

- `backend.py`: A FastAPI backend and Jinja template that uses the `vosk`
package to transcribe audio files. This version will only return once the
recording is done.
- `test_microphone.py`: A script that uses the `sounddevice` package to record
  from the microphone and transcribe the audio in real-time using the `vosk`
  package (modified from the original code from the `vosk` package).
- `transcribe_file.py`: A script that uses the `vosk` package to transcribe an
  audio file.
