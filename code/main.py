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
from groq import Groq


api_key_voice = os.getenv('TEXT_TO_SPEECH')


def play_voice(text):
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

    # Make the API request
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
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
    else:
        print("Failed to generate speech:", response.status_code, response.text)








connection = sqlite3.connect("memory.db")
cursor = connection.cursor()
connection.commit()
database_results = cursor.execute("SELECT * FROM memories")
memories = database_results.fetchall()

"""
manual_adding = "Nixie considers Siri and Alexa as hers distant cousins and occasionally ‘chats’ with them to exchange information. But she think she is better than them"
cursor.execute("INSERT INTO memories (description) VALUES (?)", (manual_adding,))
connection.commit()
"""


def create_memory(memory_add):
    connection = sqlite3.connect("memory.db")
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO memories (description) VALUES (?)", (memory_add,))
        connection.commit()
    except sqlite3.ProgrammingError as e:
        print("An error occurred:", e)
    finally:
        cursor.close()  # Ensuring the cursor is closed after operation
        connection.close()  # Ensuring the connection is closed after operation

# Establishing temporary chat database connection
def create_temporary_chat_db():
    connection_temporary = sqlite3.connect("temporary_chat.db")
    cursor_temporary = connection_temporary.cursor()
    cursor_temporary.execute("DROP TABLE IF EXISTS temporary_chat")
    cursor_temporary.execute("CREATE TABLE IF NOT EXISTS temporary_chat (textUser TEXT, answer TEXT)")
    connection_temporary.commit()
    connection_temporary.close()

create_temporary_chat_db()

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

# Initialize Groq client
client = Groq()

def has_internet():
    try:
        requests.get('http://www.google.com', timeout=1)
        return True
    except requests.ConnectionError:
        return False

def get_groq_response(command, memories):
    temporary_chat = chat_history()
    chat_history_formatted = "\n".join(f"User: {chat[0]}, AI: {chat[1]}" for chat in temporary_chat)
    system_prompt = f"""
        You are an assistant trained to provide concise and short responses. You have access to memories where the creator stores information so you can customize the answers and recent chat interactions so you can have context what is being said. Here's the context you need:

        Memories:
        {memories}

        Recent Chat History:
        {chat_history_formatted}

        Based on the above information, respond to the user's current command shortly.
        """
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": command
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    response_text = completion.choices[0].message.content
    emotion = "normal"  # Placeholder for emotion. Implement logic to determine emotion if needed.

    return response_text, emotion


emotion_videos = {
    "normal": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Normal.mp4",
    "happy": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Happy.mp4",
    "sad": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Sad.mp4",
    "mad": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Mad.mp4",
    "bored": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Bored.mp4",
    "love": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Love.mp4",
    "blink": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Blink.mp4"
}

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

# Function to load responses from a JSON file
def load_responses(file_path):
    with open(file_path, 'r') as file:
        responses = json.load(file)
    return responses

# Function to save responses to a JSON file
def save_responses(file_path, responses):
    with open(file_path, 'w') as file:
        json.dump(responses, file, indent=4)

# Function to play a video in the Tkinter window
def play_video(video_path):
    video = imageio.get_reader(video_path, 'ffmpeg')
    def video_loop():
        for frame in video:
            image = Image.fromarray(frame)
            image = image.resize((600, 450))
            image = ImageTk.PhotoImage(image)
            label.config(image=image)
            label.image = image
            root.update()
            root.after(10)  # Adjust the delay as needed
    thread = threading.Thread(target=video_loop)
    thread.start()




# Function to get the appropriate response based on user input
def get_response(command, memories):
    if has_internet():
        response_text, emotion = get_groq_response(command, memories)
    else:
        responses = load_responses('responses.json')
        response_data = responses.get(command.lower(), {"answer": "I don't understand that command.", "emotion": "normal"})
        response_text, emotion = response_data["answer"], response_data["emotion"]
    return response_text, emotion

# Function to listen to the microphone input and recognize speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Adjust for ambient noise
        print("Listening...")
        audio = recognizer.listen(source, phrase_time_limit=10)
        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")

# Function to handle the assistant's main loop
def assistant_loop():
    connection_temporary = sqlite3.connect("temporary_chat.db")
    cursor_temporary = connection_temporary.cursor()
    while True:
        print("Ready to listen for a command...")
        command = listen()
        if command:
            if "new memory" in command.lower() or "create new memory" in command.lower() or "create memory" in command.lower():
                play_voice("Which memory you would like to create?")
                memory_add = listen()
                create_memory(memory_add)
                print(memory_add)
            # Corrected condition to properly handle "set time" or "set timer"
            if "set time" in command.lower() or "set timer" in command.lower():
                play_voice("How many minutes?")
                time_confirmation = listen()
                if time_confirmation:
                    time_converted = convert_word_to_number(time_confirmation)
                    if isinstance(time_converted, int):
                        play_voice(f"Timer for {time_converted} minute starts now")
                        set_timer(time_converted)
                    else:
                        play_voice("Sorry, I didn't understand the number.")
                continue  # Continue listening for new commands

            # Handles all other commands
            response_text, emotion = get_response(command, memories)
            temporary_conversation = (command, response_text)
            cursor_temporary.execute("""INSERT INTO temporary_chat VALUES(?, ?)""", temporary_conversation)
            connection_temporary.commit()
            play_video(emotion_videos.get(emotion, emotion_videos["normal"]))
            play_voice(response_text)
            if response_text == "I don't understand that command.":
                play_voice("Would you like to add an answer for that?")
                confirmation = listen()
                if confirmation and confirmation.lower() == "yes":
                    play_voice("Please say the response you want to add.")
                    new_response = listen()
                    if new_response:
                        responses[command.lower()] = {"answer": new_response, "emotion": "normal"}
                        save_responses('responses.json', responses)
                        play_voice("Response added successfully.")
                elif confirmation and confirmation.lower() == "no":
                    play_voice("Okay, no response will be added.")
        else:
            play_voice("I didn't hear you. Please try again.")
    

def set_timer(minutes):
    time.sleep(minutes * 60)
    play_voice("Timer Finished")
    timer_thread = threading.Thread(target=set_timer)
    timer_thread.start()

def convert_word_to_number(word):
    return word_to_number.get(word.lower(), "I don't know that one")

# Initialize Tkinter root window
root = tk.Tk()
label = tk.Label(root)
label.pack()

# Load the responses from a JSON file
responses = load_responses('code/responses.json')

# Run the assistant loop in a separate thread
assistant_thread = threading.Thread(target=assistant_loop)
assistant_thread.start()

# Start the Tkinter main loop
root.mainloop()