import subprocess
import json
import io
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from vosk import Model, KaldiRecognizer

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load the Vosk model once for efficiency
model = Model("vosk-model-en-us-0.42-gigaspeech")

# Serve the HTML Frontend
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint to receive audio chunks, buffer them,
    and process the complete stream when the client signals 'done'.
    """
    await websocket.accept()
    print("WebSocket Connection Established")

    audio_buffer = io.BytesIO()  # Buffer to store all incoming audio chunks

    try:
        while True:
            # Receive data from the WebSocket
            data = await websocket.receive_bytes()

            # Detect end-of-stream signal
            if data == b"__done__":
                print("End-of-stream signal received.")
                break

            print(f"Received Chunk: {len(data)} bytes")
            audio_buffer.write(data)  # Append the chunk to the buffer

        # Reset buffer to the beginning
        audio_buffer.seek(0)

        # Convert buffered audio to 16kHz PCM format
        pcm_audio = convert_audio_to_pcm(audio_buffer.read())
        print(f"PCM conversion returned: {'Success' if pcm_audio else 'Failed'}")

        if pcm_audio:
            print(f"PCM Audio length: {len(pcm_audio)} bytes")
            # Transcribe audio using Vosk
            recognizer = KaldiRecognizer(model, 16000)
            recognizer.SetWords(True)

            print("Starting recognition...")
            recognition_success = recognizer.AcceptWaveform(pcm_audio)
            print(f"Recognition success: {recognition_success}")

            # Get result even if recognition_success is False
            result = json.loads(recognizer.Result())
            print(f"Raw recognition result: {result}")

            # Also try getting partial results
            partial = json.loads(recognizer.PartialResult())
            print(f"Partial result: {partial}")

            final_text = result.get("text", "")
            print("Final Transcription:", final_text)
            await websocket.send_text(final_text)

        print("Processing complete.")
    except WebSocketDisconnect:
        print("WebSocket disconnected by client.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing WebSocket")
        await websocket.close()

# Helper function to convert WebM/Opus to PCM WAV
def convert_audio_to_pcm(input_bytes):
    """
    Converts WebM/Opus audio to 16kHz PCM format using FFmpeg.
    """
    try:
        process = subprocess.run(
            [
                "ffmpeg", "-f", "webm", "-i", "pipe:0",
                "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
            ],
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if process.returncode != 0:
            print("FFmpeg Error:", process.stderr.decode())
            return None
        return process.stdout
    except Exception as e:
        print(f"FFmpeg Conversion Error: {e}")
        return None
