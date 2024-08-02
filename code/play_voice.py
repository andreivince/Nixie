import tkinter as tk
from PIL import Image, ImageTk
import imageio
from gtts import gTTS
import pygame
import os
import speech_recognition as sr
import requests
import sqlite3
from groq import Groq, RateLimitError  # Ensure RateLimitError is imported
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psutil
from google.oauth2 import service_account
from google.cloud import texttospeech
from google.api_core.exceptions import GoogleAPIError
from google.oauth2 import service_account
from google.cloud import texttospeech
import base64

service_account_path = '/Users/andreivince/Desktop/Nixie/dulcet-opus-431018-s2-e959df4a8f4b.json'  # Replace with your Google service account path
credentials = service_account.Credentials.from_service_account_file(service_account_path)
gtts_client = texttospeech.TextToSpeechClient(credentials=credentials)

api_key_voice = os.getenv('TEXT_TO_SPEECH')

def play_voice(text):
    # Attempt to use Google Text-to-Speech API first
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Journey-O"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            effects_profile_id=["small-bluetooth-speaker-class-device"],
            pitch=0,
            speaking_rate=1
        )
        response = gtts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open("temp_voice.wav", "wb") as out:
            out.write(response.audio_content)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load("temp_voice.wav")
        pygame.mixer.music.play()

        # Wait until the audio finishes playing
        while pygame.mixer.music.get_busy():
            pass

        # Remove the temporary audio file
        os.remove("temp_voice.wav")
    except Exception as e:
        print(f"Failed to generate speech with Google Text-to-Speech: {e}")

        # Attempt to use Eleven Labs API as fallback
        try:
            url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key_voice
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }

            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            # Save the response content to a file
            with open('temp_voice.mp3', 'wb') as f:
                f.write(response.content)
            
            # Initialize pygame mixer
            pygame.mixer.init()
            pygame.mixer.music.load("temp_voice.mp3")
            pygame.mixer.music.play()

            # Wait until the audio finishes playing
            while pygame.mixer.music.get_busy():
                pass

            # Remove the temporary audio file
            os.remove("temp_voice.mp3")
        except Exception as e:
            print(f"Failed to generate speech with Eleven Labs: {e}")

            # Use GTTS as last fallback
            try:
                tts = gTTS(text=text, lang='en')
                tts.save("temp_voice.mp3")
                
                # Initialize pygame mixer
                pygame.mixer.init()
                pygame.mixer.music.load("temp_voice.mp3")
                pygame.mixer.music.play()

                # Wait until the audio finishes playing
                while pygame.mixer.music.get_busy():
                    pass

                # Remove the temporary audio file
                os.remove("temp_voice.mp3")
            except Exception as e:
                print(f"Failed to generate speech with GTTS: {e}")