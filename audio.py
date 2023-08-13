import os
import random
import openai
import time
from playsound import playsound

thinking_audio_path = 'audio/thinking' 

def play_thinking_audio():
    """
     // UNUSED // Play a random audio file from the thinking folder
    """
    file_names = os.listdir(thinking_audio_path)
    random_file_name = random.choice(file_names)
    print(random_file_name)
    playsound(thinking_audio_path + '/' + random_file_name)

def transcribe_whisper(audio):
    """
    Transcribe audio using Whisper API

    :param audio: audio file
    """
    print("I'm transcribing your audio...")
    start_transcribe = time.perf_counter()
    with open("audio.wav", "wb") as f:
        f.write(audio.get_wav_data())
    with open("audio.wav", "rb") as f:
        audio_response = openai.Audio.transcribe("whisper-1", f)['text']
    end_transcribe = time.perf_counter()
    print(f"It took: {end_transcribe - start_transcribe} seconds")

    return audio_response