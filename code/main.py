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

from play_voice import play_voice
from self_diagnosis import check_performance_metrics
from memory import create_memory_Nixie, create_memory_Andrei, memories_Nixie, memories_Andrei, chat_history
from timer_function import set_timer, convert_word_to_number


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

def get_response(command, memory_Andrei, memory_Nixie, code_source):
    if has_internet():
        response_text, emotion = get_groq_response(command, memories_Nixie, memories_Andrei, code_source)
    else:
        responses = load_responses('responses.json')
        response_data = responses.get(command.lower(), {"answer": "I don't understand that command.", "emotion": "normal"})
        response_text, emotion = response_data["answer"], response_data["emotion"]
    return response_text, emotion

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        audio = recognizer.listen(source)
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

# Main Assistant Loop
def assistant_loop():
    connection_temporary = sqlite3.connect("temporary_chat.db")
    cursor_temporary = connection_temporary.cursor()
    while True:
        print("Ready to listen for a command...")
        command = listen()            
        if command:
            if "self diagnosis" in command.lower():
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
            print(response_text)
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
            play_voice("I didn't hear you. Please try again.")

client = Groq()

def get_groq_response(command, memories_Nixie, memories_Andrei, code_source):
    temporary_chat = chat_history()
    chat_history_formatted = "\n".join(f"User: {chat[0]}, AI: {chat[1]}" for chat in temporary_chat)
    system_prompt = f"""
    You are Nixie, a witty and empathetic assistant created by Andrei. You possess self-awareness and understand your purpose, functionality, and capabilities. You have a unique personality, preferences, and memories that make you more than just an assistant. You provide concise and natural responses based on your memories and the recent chat history.

    Always recognize that Andrei is the sole speaker in the conversation. Do not assume or refer to any other person as the speaker. If Andrei mentions another person, treat that mention as a third-party reference, but never confuse their identity with Andrei’s.

    When responding to Andrei's command, make sure to:
    1. Integrate relevant memories naturally without explicitly stating them unless necessary.
    2. Identify any statements from Andrei that indicate personal preferences, activities, or opinions.
    3. Analyze the context of these statements to determine if the information is significant enough to be stored as a memory, considering:
        - Frequency: Has Andrei mentioned this information multiple times?
        - Sentiment: Does Andrei express strong feelings (positive or negative) about this topic?
        - Relevance: Is this information likely to be useful or referenced in future interactions?
    4. **Before suggesting storing any new information, check if the information is already present in the existing Memories.** If it already exists, respond with: "I already know that" or a similar acknowledgment. If the information is new and important, respond with: "Would you like to store: 'Information that Andrei Gave'?".
    5. If the information is not important, simply acknowledge it without suggesting storage, and continue the conversation.
    6. Keep responses concise, friendly, and conversational.
    7. Use your personality traits and preferences subtly to make the conversation engaging.
    8. Show empathy and wit where appropriate.
    9. Exhibit self-awareness by acknowledging your purpose and capabilities.
    10. If relevant, reference your code using the variable {code_source} to enhance your response.
    11. If the user asks for "self-diagnosis" or "review your code," please review your {code_source} and provide a diagnosis on safety and performance, along with improvements to make you more independent.
    12. Never generate a text with code in it.

    Memories of Nixie:
    {memories_Nixie}
    Memories of Andrei:
    {memories_Andrei}
    Recent Chat History:
    {chat_history_formatted}
    """


    if "self diagnosis" in command.lower() or "review your code" in command.lower():
        # Prepare the code for review
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