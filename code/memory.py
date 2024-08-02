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


connection = sqlite3.connect("memory.db")
cursor = connection.cursor()
connection.commit()
database_results = cursor.execute("SELECT * FROM Nixie_Memories")
memories = database_results.fetchall()

"""
manual_adding = "Nixie can detect Andrei’s mood based on his voice and adjust her tone and responses to match."
cursor.execute("INSERT INTO memories (description) VALUES (?)", (manual_adding,))
connection.commit()
"""

def create_memory_Nixie(memory_add):
    connection = sqlite3.connect("memory.db")
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO Nixie_Memories (description) VALUES (?)", (memory_add,))
        connection.commit()
    except sqlite3.ProgrammingError as e:
        print("An error occurred:", e)
    finally:
        cursor.close()  # Ensuring the cursor is closed after operation
        connection.close()  # Ensuring the connection is closed after operation

def create_memory_Andrei(memory_add):
    connection = sqlite3.connect("memory.db")
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO Andrei_Vince_Memories (description) VALUES (?)", (memory_add,))
        connection.commit()
    except sqlite3.ProgrammingError as e:
        print("An error occurred:", e)
    finally:
        cursor.close()  # Ensuring the cursor is closed after operation
        connection.close()  # Ensuring the connection is closed after operation


# Temporary Chat
def create_temporary_chat_db():
    connection_temporary = sqlite3.connect("temporary_chat.db")
    cursor_temporary = connection_temporary.cursor()
    cursor_temporary.execute("DROP TABLE IF EXISTS temporary_chat")
    cursor_temporary.execute("CREATE TABLE IF NOT EXISTS temporary_chat (textUser TEXT, answer TEXT)")
    connection_temporary.commit()
    connection_temporary.close()

def insert_chat_history(user_input, ai_response):
    connection_temporary = sqlite3.connect("temporary_chat.db")
    cursor_temporary = connection_temporary.cursor()
    cursor_temporary.execute("INSERT INTO temporary_chat (textUser, answer) VALUES (?, ?)", (user_input, ai_response))
    connection_temporary.commit()
    connection_temporary.close()

def chat_history():
    connection_temporary = sqlite3.connect("temporary_chat.db")
    cursor_temporary = connection_temporary.cursor()
    results = cursor_temporary.execute("SELECT textUser, answer FROM temporary_chat").fetchall()
    connection_temporary.close()
    return results

create_temporary_chat_db()