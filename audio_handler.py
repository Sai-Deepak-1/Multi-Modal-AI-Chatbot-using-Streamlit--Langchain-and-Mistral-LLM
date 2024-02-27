import torch
from transformers import pipeline
import librosa
import io


def convert_bytes_to_array(audio_bytes):
    audio_bytes = io.BytesIO(audio_bytes)
    audio, sample_rate = librosa.load(audio_bytes)
    print(sample_rate)
    return audio


def transcribe_audio(audio_bytes):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    pipe = pipeline(
        task="automatic-speech-recognition",
        model="openai/whisper-small.en",
        chunk_length_s=30,
        device=device,
    )
    audio_array = convert_bytes_to_array(audio_bytes)
    prediction = pipe(audio_array, batch_size=1)["text"]
    return prediction
    # we can also return timestamps for the predictions
    # prediction = pipe(sample.copy(), batch_size=8, return_timestamps=True)["chunks"]
