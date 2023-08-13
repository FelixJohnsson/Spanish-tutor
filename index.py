import time
import speech_recognition
import requests
import openai
import re
import pygame.mixer
from rich.console import Console
from audio import transcribe_whisper
from chatGPT import call_chatGPT
from dotenv import load_dotenv
import os

"""
    Spanish tutor voice assistant

This is the main file that runs the voice assistant. It listens to your voice, converts it to text, sends it to chatGPT to get a response, and then converts the response to speech.
The voice assistant is in Spanish, but you can change the language by changing the voice ID. Currently this is up to you and your Eleven labs account.
"""

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

ELEVEN_LABS_API_KEY = os.getenv('ELEVEN_LABS_API_KEY')
ELEVEN_LABS_URL = 'https://api.elevenlabs.io/v1/text-to-speech/'

#standard_voice_id = os.getenv('STANDARD_VOICE_ID')
SPANISH_VOICE_ID = os.getenv('SPANISH_VOICE_ID')

# Do you want to use Whisper API to transcribe audio? It's very accurate, but not free. Otherwise it will use Google Speech Recognition only.
IS_WHISPER_ENABLED = True

# If you'd want to use a keyword to finish the conversation, you can set it here. Probably not needed.
KEYWORD = ""

console = Console()

def main():
    console.rule('[bold yellow] Voice Assistant')
    
    recognizer = speech_recognition.Recognizer()

    while True:
        with console.status(status='Listening to you...', spinner='point'):
            try:
                with speech_recognition.Microphone() as mic:
                    recognizer.adjust_for_ambient_noise(mic, duration=0.1)
                    audio = recognizer.listen(mic, timeout=10, phrase_time_limit=8)
                
                initial_guess = recognizer.recognize_google(audio_data=audio).lower()
                console.print(f'[bold]Initial guess[/bold]: {initial_guess}')
                if(len(initial_guess) > 0 and IS_WHISPER_ENABLED):
                    audio_response = transcribe_whisper(audio)
                    console.print(f'[bold]Recognized text[/bold]: {audio_response}')
                else:
                    audio_response = initial_guess

                if KEYWORD in audio_response.lower():
                    total_timer_start = time.perf_counter()

                    print("I'm now thinking of an answer...")
                    text_content = call_chatGPT(audio_response)
                    console.print(text_content)
                    audio_content = convert_text_to_speech(text_content)

                    total_time = time.perf_counter() - total_timer_start
                    print(f"-------------------------------------- Total time: {total_time} seconds")

                    file_name = save_response_to_file(text_content, audio_content)

                    try:
                        print("playing audio")
                        pygame.mixer.init()
                        pygame.mixer.music.load(file_name)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy() == True:
                            continue
                        pygame.mixer.quit()
                        
                    except Exception as e:
                        print(e)
                        print('Could not play audio file')
                        continue
                            
            except speech_recognition.UnknownValueError:
                continue

def clean_string_for_file_name(string):
    string = re.sub(r'\W+', '', string)
    string = string.replace(' ', '_')
    special_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in special_chars:
        string = string.replace(char, '')

    return string

counter = 0
def save_response_to_file(text, audio):
    global counter
    FILE_NAME_LENGTH = 50
    counter += 1

    file_name_placeholder = 'Spanish_teacher'


    if(file_name_placeholder == ''):
        description = text[:FILE_NAME_LENGTH].replace(' ', '_')
        description = clean_string_for_file_name(description)
        file_name = f"{description}_{counter}.mp3"
    else:
        file_name = f"audio/{file_name_placeholder}_{counter}.mp3"

    with open(file_name, 'wb') as f:
        f.write(audio)

    return file_name

def convert_text_to_speech(text_content):
    """
    Convert text to speech using ElevenLabs API

    :param text_content: text to convert
    :return: audio stream or None if there's an error
    """
    print("I'm now converting my answer to speech...")
    url = f"{ELEVEN_LABS_URL}{SPANISH_VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_LABS_API_KEY}
    data = {"text": text_content}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)  # added a timeout for the request
        
        # Check if the response status code indicates success
        response.raise_for_status()

        # You can also add specific checks on the content, for instance:
        if not response.content:
            print("Error: Received empty content from ElevenLabs API.")
            return None

        return response.content
    
    except requests.Timeout:
        print("Error: The request to ElevenLabs API timed out.")
    except requests.ConnectionError:
        print("Error: Failed to connect to ElevenLabs API.")
    except requests.RequestException as e:
        # For other types of exceptions that requests might raise
        print(f"Error: An error occurred while communicating with ElevenLabs API - {e}")
    except Exception as e:
        # A generic exception catch for unforeseen exceptions
        print(f"An unexpected error occurred: {e}")

    return None
                
if __name__ == '__main__':
    main()