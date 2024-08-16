import tkinter as tk
from PIL import Image, ImageTk
import imageio
from gtts import gTTS
import pygame
import os
import json
import speech_recognition as sr
import threading
import time
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

from play_voice import play_voice
from self_diagnosis import check_performance_metrics

word_to_number = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10
}

def set_timer(minutes):
    time.sleep(minutes * 60)
    play_voice("Timer Finished")
    timer_thread = threading.Thread(target=set_timer)
    timer_thread.start()

def convert_word_to_number(word):
    return word_to_number.get(word.lower(), "I don't know that one")