import wave
import os
import math
import contextlib
import speech_recognition as sr
from moviepy.editor import AudioFileClip
import multiprocessing
import subprocess
from transformers import BartForConditionalGeneration, BartTokenizer
from moviepy.editor import VideoFileClip
from langdetect import detect

"""
Beta Version 1.5

Patch Note:
    12/4/2024 -- get it working with the first runner
    12/4/2024 -- add multiprocessing to speed up the process
    13/4/2024 -- multiprocessing can be used to speed up the process
    15/4/2024 -- add a function to convert mp4 to mp3
    15/4/2024 -- add a function to summarize the text
    22/4/2024 -- add a function to read the text (stupid)

Future Update:
    add a function to translate the text

Problem:
    text have no full stop
    sometimes wrong word by google speech recognition
    slow process summary
    translator is fucking stupid (try and already delete)
    read the text is also fucking stupid

"""

### Settings
target = "xxx.mp4" # input file mp4 or mp3

# set language
language = "en-EN" # en-EN, jp-JP, th-TH

# separate for use multiple processes
aaa = 60  # 60++ is stable

## Part of MP4 to MP3
file_path_mp4 = target  

def convert_mp4_to_mp3(mp4_file, mp3_file):
    video = VideoFileClip(mp4_file)
    audio = video.audio
    audio.write_audiofile(mp3_file)
    audio.close()
    video.close()

## Part of MP3 to Text
zoom_video_file_name = target
transcribed_audio_file_name = "transcribed_speech.wav"
file_path_txt = "transcription_MP3.txt"

# Recognize speech
r = sr.Recognizer()


def transcribe_audio(i):
    with sr.AudioFile(transcribed_audio_file_name) as source:
        audio = r.record(source, offset=i * aaa, duration=aaa)
    try:
        text = r.recognize_google(audio, language=language)  # Set language
        # print("P(" + str(i + 1) + ")_script: " + str(text) + "\n") # for debugging
        return text
    except Exception as e:
        # print(f"Error in transcribing segment {i}: {e}") # for debugging
        return ""


# Load tokenizer and model
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

## Part of Text to Summary
def generate_summary(text):
    inputs = tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)
    summary_ids = model.generate(inputs['input_ids'], num_beams=4, min_length=300, max_length=3000, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

## part of read the text

def detect_language(text):
    try:
        language = detect(text)
        return language
    except:
        return "Unknown"
    
def text_to_speech(text,rate=150,lang='x'): # caller function
    if lang == 'x':
        lang = detect_language(text)
    if lang == 'en':
        text_to_speech_en(text,rate)
    elif lang == 'ja':
        text_to_speech_jp(text,rate)
    elif lang == 'th':
        text_to_speech_th(text,rate)
    elif lang == 'Unknown':
        text_to_speech_en(text,rate)
    else:
        print("Language not supported")
        return
        
def text_to_speech_en(text,rate=150):
    subprocess.call(['say', '-v', 'Reed','-r',str(rate), text])

def text_to_speech_jp(text,rate=150):
    subprocess.call(['say', '-v', 'Kyoko','-r',str(rate), text])

def text_to_speech_th(text,rate=150):
    subprocess.call(['say', '-v', 'Kanya','-r',str(rate), text])

if __name__ == "__main__":
    # Clear text
    with open("transcription_MP3.txt", "w", encoding="utf-8") as f:
        f.write("")

    # condition mp4 to mp3
    
    if file_path_mp4.lower().endswith(".mp4"):
        mp3_file = os.path.splitext(file_path_mp4)[0] + ".mp3"
        convert_mp4_to_mp3(file_path_mp4, mp3_file)
        print(f"Conversion complete. MP3 file saved as: {mp3_file}")
    else:
        print("File is not an MP4 file. Conversion skipped.")
        mp3_file = None

    if mp3_file:
        zoom_video_file_name = mp3_file

    # Convert video to audio
    audioclip = AudioFileClip(zoom_video_file_name)
    audioclip.write_audiofile(transcribed_audio_file_name)

    # Get audio duration
    with contextlib.closing(wave.open(transcribed_audio_file_name, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    total_duration = math.ceil(duration)
    total_duration = int((duration / aaa) + 1)
    print("MP3 Duration:", total_duration, " minutes")

    # Multiprocessing
    pool = multiprocessing.Pool()
    result = pool.map(transcribe_audio, range(total_duration))
    pool.close()
    pool.join()

    print("Transcription complete.\n")
    script = ""
    for i, text in enumerate(result):
        script += str(text + " ")

    print("Script: " + script)

    # Save transcription results to file
    try:
        with open("transcription_MP3.txt", "a", encoding="utf-8") as f:
            f.write(script)
    except Exception as e:  # Handle exceptions
        print(f"\nError: {e}")

    # Open the file
    try:
        subprocess.run(["open", file_path_txt], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError: {e}")

    print("\ncomplete.")

    Summary_Script = generate_summary(script)
    print("Summary Script:",Summary_Script)

    # read with speech to text subprocess
    text_to_speech(Summary_Script,150)


