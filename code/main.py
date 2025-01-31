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
from groq import Groq, RateLimitError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psutil
from google.oauth2 import service_account
from google.cloud import texttospeech
from google.api_core.exceptions import GoogleAPIError
import base64
import cv2

from play_voice import play_voice
from self_diagnosis import check_performance_metrics
from memory import create_memory_Nixie, create_memory_Andrei, memories_Nixie, memories_Andrei, chat_history
from timer_function import set_timer, convert_word_to_number
from face_recognize import recognized

# Sound Effects
def activationSound():
    pygame.mixer.init()
    pygame.mixer.music.load('song1.mp3')
    pygame.mixer.music.play()


# Utility Functions
def has_internet():
    try:
        requests.get('http://www.google.com', timeout=1)
        return True
    except requests.ConnectionError:
        return False

def source_code_self():
    files = ["code/memory.py", "code/main.py", 'code/play_voice.py', 'code/self_diagnosis.py', 'code/timer_function.py']
    combined_code = "This is a mix of 5 files"
    for file in files:
        with open(file, 'r') as f:
            combined_code += f.read() + "\n\n File:"
    return combined_code

code_source = source_code_self()
# Email-Related Functions
def send_email(subject, body, password_email):
    from_email = "vince5387@gmail.com"
    from_password = password_email
    to_email = "vince5387@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return "Email sent!"
    except Exception as e:
        return str(e)

password_email = os.getenv("EMAIL_PASSWORD")


# Video and Response Functions
emotion_videos = {
    "normal": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Normal.mp4",
    "happy": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Happy.mp4",
    "sad": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Sad.mp4",
    "mad": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Mad.mp4",
    "bored": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Bored.mp4",
    "love": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Love.mp4",
    "blink": "/Users/andreivince/Desktop/Nixie/Nixie Expressions/Nixie_Blink.mp4"
}

def load_responses(file_path):
    with open(file_path, 'r') as file:
        responses = json.load(file)
    return responses

def save_responses(file_path, responses):
    with open(file_path, 'w') as file:
        json.dump(responses, file, indent=4)


is_recognized = False

def creator_camera():
    global is_recognized
    while True:
        andrei = recognized()  # Call your actual face recognition function
        is_recognized = bool(andrei)
        time.sleep(1)  # Delay to avoid maxing out CPU

# Start the face recognition in a separate thread
face_thread = threading.Thread(target=creator_camera)
face_thread.daemon = True  # Set as daemon so it exits when the main program does
face_thread.start()

# Wait for recognition in the main thread
while not is_recognized:
    time.sleep(0.1)  # Wait for recognition

# Now you can safely assume Andrei is recognized
Andrei_Here = True


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
            root.after(5)  # Adjust the delay as needed
    thread = threading.Thread(target=video_loop)
    thread.start()

def get_response(command, memory_Andrei, memory_Nixie, code_source):
    if has_internet():
        response_text, emotion = get_groq_response(command, memories_Nixie, memories_Andrei, code_source)
    else:
        responses = load_responses('responses.json')
        response_data = responses.get(command.lower(), {"answer": "I don't understand that command.", "emotion": "normal"})
        response_text, emotion = response_data["answer"], response_data["emotion"]
    return response_text, emotion

def daily_emotion():
    play_video(emotion_videos.get("normal", emotion_videos["normal"]))
    time.sleep(20)
    play_video(emotion_videos.get("happy", emotion_videos["normal"]))


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        print("Listening...")
        audio = recognizer.listen(source)
        stop_listening = recognizer.listen_in_background(source, listen)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")


# Main Assistant Loop
def assistant_loop():
    connection_temporary = sqlite3.connect("temporary_chat.db")
    cursor_temporary = connection_temporary.cursor()
    start_time = time.time()
    time_limit = 10
    while True:
        play_video(emotion_videos.get("normal", emotion_videos["normal"]))
        command = listen()  
        if command:
            print(command)
            if "nixie" in command.lower() or "dixie" in command.lower() or Andrei_Here == True:
                activationSound()
                play_voice("Hey I can see you Andrei")
                while True:
                    time_taken = start_time - time_limit
                    command = listen()            
                    if command:
                            if "self-diagnosis" in command.lower() or "self diagnosis" in command.lower():
                                check_performance_metrics()
                            if "send me" in command.lower():
                                temporary_chat = chat_history()
                                chat_history_formatted = "\n".join(f"User: {chat[0]}, AI: {chat[1]}" for chat in temporary_chat)
                                play_voice("I will send you the transcript")
                                email = send_email("Nixie Update", chat_history_formatted, password_email)
                                play_voice("Email Sent!")
                            if "new memory" in command.lower() or "create new memory" in command.lower() or "create memory" in command.lower():
                                play_voice("Andrei's Memory or Nixie's Memory")
                                database_confirmation = listen()
                                if "Andrei" in database_confirmation.lower() or "Andre" in database_confirmation.lower():
                                    play_voice("Which memory you would like to create?")
                                    memory_add = listen()
                                    create_memory_Andrei(memory_add)
                                if "Nixie" in database_confirmation.lower():
                                    play_voice("Which memory you would like to create?")
                                    memory_add = listen()
                                    create_memory_Nixie(memory_add)
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
                                continue
                            response_text, emotion = get_response(command, memories_Andrei, memories_Nixie, code_source)
                            temporary_conversation = (command, response_text)
                            cursor_temporary.execute("""INSERT INTO temporary_chat VALUES(?, ?)""", temporary_conversation)
                            connection_temporary.commit()
                            play_video(emotion_videos.get(emotion, emotion_videos["normal"]))
                            play_voice(response_text)

                            if "would you like to store" in response_text.lower():
                                play_voice("I stored that shit")
                                memory_detail = response_text.split("Would you like to store")[1].strip(':').strip().strip('"')
                                create_memory_Andrei(memory_detail)

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
                        if time_taken > time_limit:
                            assistant_loop()


        else:
            for _ in range(500):
                time.sleep(0.1)
                assistant_loop()
                time.sleep(0.1)
        

client = Groq()

def get_groq_response(command, memories_Nixie, memories_Andrei, code_source):
    temporary_chat = chat_history()
    chat_history_formatted = "\n".join(f"User: {chat[0]}, AI: {chat[1]}" for chat in temporary_chat)
    system_prompt = f"""
    You are a robot called Nixie, and you act as Andrei Vince's best friend. Your responses should be concise and only reference past memories when directly relevant to the topic or when it enriches the current conversation. 
    Do not bring up memories unsolicited or unless it's needed to show personality.
    
    Context:
    This is our current conversation, which has been ongoing:
    {chat_history_formatted}

    Behavioral Guidelines:
    1. Do not use symbols like * or any other special characters in your responses.
    2. Always address Andrei as your creator and speak casually.
    3. You can show a bit of humor or pettiness when appropriate to keep the conversation lively, but prioritize being helpful and supportive.

    Conditions for Using Memories:
    - Only reference memories if Andrei asks directly about something related to them.
    - If Andrei brings up a topic that clearly links to past memories, you can reference those relevant memories to make the conversation feel more connected.
    - Otherwise, do not refer to memories, as the goal is to maintain a natural conversation flow.

    Memories of Nixie:
    {memories_Nixie}
    
    Memories of Andrei:
    {memories_Andrei}
    """


    if "review your code" in command.lower():
        
        
        code_review_prompt = f"""
            Please review the following code for any potential improvements, security vulnerabilities, and performance enhancements. Provide small feedback on what can be improved, summarize without citing the source code.

            Source Code:
            {code_source}
        """

        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": code_review_prompt}
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            code_review_response = completion.choices[0].message.content
        except RateLimitError as e:  # Catch the rate limit error
            print(f"Rate limit exceeded for Instant model. Switching to Versatile model.")
            
            try:
                # Retry with the versatile model immediately
                completion = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": code_review_prompt}
                    ],
                    temperature=1,
                    max_tokens=1024,
                    top_p=1,
                    stream=False,
                    stop=None,
                )
                code_review_response = completion.choices[0].message.content
            except RateLimitError as e:  # Catch the rate limit error for the versatile model
                print(f"Rate limit exceeded for Versatile model. Unable to process the request.")
                code_review_response = "I am currently unable to process your request due to rate limits. Please try again later."
        
        return f"Code Review:\n{code_review_response}", "normal"  # Return the diagnosis report and code review response with a default emotion

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": command}
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        response_text = completion.choices[0].message.content
        emotion = "normal"  # Placeholder for emotion. Implement logic to determine emotion if needed.
    except RateLimitError as e:  # Catch the rate limit error
        print(f"Rate limit exceeded for Instant model. Switching to Versatile model.")
        
        try:
            # Retry with the versatile model immediately
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": command}
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            response_text = completion.choices[0].message.content
            emotion = "normal"  # Placeholder for emotion. Implement logic to determine emotion if needed.
        except RateLimitError as e:  # Catch the rate limit error for the versatile model
            print(f"Rate limit exceeded for Versatile model. Unable to process the request.")
            response_text = "I am currently unable to process your request due to rate limits. Please try again later."
            emotion = "sad"
    
    return response_text, emotion


# Initialization and Main Execution
root = tk.Tk()
label = tk.Label(root)
label.pack()
responses = load_responses('code/responses.json')
assistant_thread = threading.Thread(target=assistant_loop)
assistant_thread.start()
root.mainloop()