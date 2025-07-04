import wave
import os
import math
import contextlib
import speech_recognition as sr
from moviepy.editor import AudioFileClip
import multiprocessing
import subprocess
from moviepy.editor import VideoFileClip

"""
Beta Version 1.5

Patch Note:
    12/4/2024 -- get it working with the first runner
    12/4/2024 -- add multiprocessing to speed up the process
    13/4/2024 -- multiprocessing can be used to speed up the process
    15/4/2024 -- add a function to convert mp4 to mp3
    15/4/2024 -- add a function to summarize the text
    22/4/2024 -- add a function to read the text (stupid)
    30/4/2024 -- delete the function to read the text (stupid)
    21/6/2024 -- remove tranformer : METAL bug
    23/2/2025 -- input file path with input function
Future Update:
    add a function to translate the text
    slow process summary
    use jupyter notebook for better visualization

Problem:
    text have no full stop
    sometimes wrong word by google speech recognition
    translator is fucking stupid (try and already delete)
    read the text is also fucking stupid (try and already delete)
"""

### Settings
target = "x.mp3"

# set language
language = "th-TH" # en-EN, ja-JP, th-TH

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



