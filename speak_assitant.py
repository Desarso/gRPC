import os
import grpc
import chat_pb2, chat_pb2_grpc
import pyaudio
from openai import OpenAI
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from time import time
import queue
import sounddevice as sd
import numpy as np

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

channel = grpc.insecure_channel("localhost:9000")
stub = chat_pb2_grpc.ChatStub(channel)

messages = []
messages = [
    chat_pb2.Message(role="system", content="You are a helpful friendly assistant. Please answer clearly and concisely. You are part of a home assitant system, respond to user commands with function calls."),
]



def message(input_message):
    messages.append(chat_pb2.Message(role="user", content=input_message))
    request = chat_pb2.ChatRequest(
        messages=messages,
        apiKey=GROQ_API_KEY,
        model="llama-3.3-70b-versatile"
    )
    try:
        # Calling the ChatStream RPC and reading the responses
        responses = stub.ChatStream(request)
        assitantMessage = chat_pb2.Message(role="assistant", content="")
        print("Assistant: ", end="")

        for response in responses:
            print(response)
            ##print in same line
            # print(response.choices[0].delta.content, end="")
            assitantMessage.content += response.choices[0].delta.content
        
        print("")

        messages.append(assitantMessage)
        speak(assitantMessage.content)

    except grpc.RpcError as e:
        print(f"RPC failed: {e}")


# Initialize Whisper Model
model_size = "base"
model = WhisperModel(model_size)

# Audio settings
SAMPLE_RATE = 16000  # Whisper expects a sample rate of 16 kHz
CHANNELS = 1
CHUNK_DURATION = 1  # Duration of each audio chunk in seconds
BLOCKSIZE = int(SAMPLE_RATE * CHUNK_DURATION)

# Parameters to detect pauses
PAUSE_THRESHOLD = 1.5  # Time in seconds to consider as a pause
last_audio_time = time()  # Tracks the last time audio was processed

# A thread-safe queue to store audio chunks
audio_queue = queue.Queue()


SILENCE_THRESHOLD = 0.03  # Adjust based on testing; lower means more sensitive to noise

def is_silent(audio_chunk):
    """Check if the audio chunk is silent based on RMS."""
    rms = np.sqrt(np.mean(np.square(audio_chunk)))  # Root Mean Square (RMS)
    return rms < SILENCE_THRESHOLD

def audio_callback(indata, frames, time, status):
    """Callback function to receive audio data from the microphone."""
    if status:
        print(f"Audio Input Error: {status}")
    audio_queue.put(indata.copy())  # Add audio data to the queue

# def llm_response(text):
#     # Connect to the gRPC server

#     # Get the API key from the environment



#     # Create a request
 

def process_audio():
    """Function to process audio from the queue in real-time."""
    print("Live transcription started. Speak into your microphone!")
    buffering = np.zeros((0,), dtype=np.float32)
    transcript = ""  # Full transcript for LLM response

    global last_audio_time
    try:
        while True:
            # Check for a pause in speech
            if time() - last_audio_time > PAUSE_THRESHOLD and transcript.strip():
                print("")
                message(transcript.strip())
                transcript = ""  # Reset transcript after LLM call

            # Get audio data from the queue
            try:
                audio_chunk = audio_queue.get(timeout=0.1)  # Non-blocking
            except queue.Empty:
                continue  # Skip if no audio available

            # Check for silence
            if is_silent(audio_chunk):
                continue  # Skip silent chunks

            # Append audio data to a buffer
            buffering = np.concatenate((buffering, audio_chunk.flatten()))

            # Process the audio if buffering size meets the block size
            if len(buffering) >= BLOCKSIZE:
                process_chunk = buffering[:BLOCKSIZE]
                buffering = buffering[BLOCKSIZE:]  # Keep the remaining part

                # Perform transcription
                segments, info = model.transcribe(process_chunk, beam_size=5)
                for segment in segments:
                    # print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                    print(f"{segment.text}", end="")
                    transcript += f" {segment.text}"  # Append to transcript
                # print("")

                # Update the last processed time
                last_audio_time = time()

    except KeyboardInterrupt:
        print("Live transcription stopped.")
    except Exception as e:
        print(f"Error during transcription: {e}")

def main():
    """Main function to start live transcription."""

    try:
        # Start the audio stream
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=np.float32,
                            callback=audio_callback, blocksize=BLOCKSIZE):
            # Process the audio data in real-time
            process_audio()
    except Exception as e:
        print(f"Could not start audio stream: {e}")


def speak(input_message):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    p = pyaudio.PyAudio()
    stream = p.open(format=8,
                    channels=1,
                    rate=24_000,
                    output=True)

    with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=input_message,
            response_format="pcm"
    ) as response:
        for chunk in response.iter_bytes(1024):
            stream.write(chunk)

if __name__ == "__main__":
    main()
