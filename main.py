import tkinter as tk
from PIL import Image, ImageTk
import imageio
from gtts import gTTS
import pygame
import os
import json
import speech_recognition as sr
import threading

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
            root.after(0)  # Adjust the delay as needed
    thread = threading.Thread(target=video_loop)
    thread.start()

# Function to generate and play a voice response
def play_voice(text):
    tts = gTTS(text=text, lang='en')
    tts.save("temp_voice.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("temp_voice.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass  # Wait until the audio finishes playing
    os.remove("temp_voice.mp3")  # Remove the temporary audio file

# Function to get the appropriate response based on user input
def get_response(input_text, responses):
    return responses.get(input_text.lower(), "I don't understand that command.")

# Function to listen to the microphone input and recognize speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Adjust for ambient noise
        print("Listening...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
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
            return None

# Function to handle the assistant's main loop
def assistant_loop():
    while True:
        # Listen for a command
        print("Ready to listen for a command...")
        command = listen()
        if command:
            response_text = get_response(command, responses)
            play_voice(response_text)

            if response_text == "I don't understand that command.":
                play_voice("Would you like to add an answer for that?")
                confirmation = listen()
                if confirmation and confirmation.lower() == "yes":
                    play_voice("Please say the response you want to add.")
                    new_response = listen()
                    if new_response:
                        responses[command.lower()] = new_response
                        save_responses('responses.json', responses)
                        play_voice("Response added successfully.")
                elif confirmation and confirmation.lower() == "no":
                    play_voice("Okay, no response will be added.")
        else:
            play_voice("I didn't hear you. Please try again.")
    

# Initialize Tkinter root window
root = tk.Tk()
label = tk.Label(root)
label.pack()

# Load the responses from a JSON file
responses = load_responses('responses.json')

# Play the video in a separate thread
play_video('/Users/andreivince/Desktop/Nixie/videoplayback.mp4')

# Run the assistant loop in a separate thread
assistant_thread = threading.Thread(target=assistant_loop)
assistant_thread.start()

# Start the Tkinter main loop
root.mainloop()