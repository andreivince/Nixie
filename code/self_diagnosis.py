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

THRESHOLDS = {
    "cpu": {"high": 80, "moderate": 50},
    "memory": {"high": 80, "moderate": 50},
    "disk": {"high": 80, "moderate": 50},
    "network": {"slow": 1}  # Network speed in Mbps
}

def interpret_metric(value, thresholds):
    if value > thresholds["high"]:
        return "high"
    elif value > thresholds["moderate"]:
        return "moderate"
    else:
        return "normal"


def check_performance_metrics():
    play_voice("Running Self-Diagnosis")
    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_status = interpret_metric(cpu_usage, THRESHOLDS["cpu"])
    
    # Memory usage
    memory_info = psutil.virtual_memory()
    memory_status = interpret_metric(memory_info.percent, THRESHOLDS["memory"])
    
    # Disk usage
    disk_info = psutil.disk_usage('/')
    disk_status = interpret_metric(disk_info.percent, THRESHOLDS["disk"])
    
    # Network speed (placeholder for actual network speed check)
    # For the sake of example, let's assume a dummy network speed
    network_speed = 5  # This should be replaced with actual network speed checking logic
    network_status = "slow" if network_speed < THRESHOLDS["network"]["slow"] else "normal"
    
    diagnosis = (f"CPU Usage is {cpu_status} at {cpu_usage}%. "
                 f"Memory usage is {memory_status} at {memory_info.percent}%. "
                 f"Disk usage is {disk_status} at {disk_info.percent}%. "
                 f"Network speed is {network_status}.")
    
    play_voice(diagnosis)
    return True

