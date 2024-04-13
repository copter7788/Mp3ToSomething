import wave
import math
import contextlib
import speech_recognition as sr
from moviepy.editor import AudioFileClip
import multiprocessing
import subprocess

"""
Beta Version 1.2
Patch Note:
    12/4/2024 -- Get it working with the first runner
    12/4/2024 -- Add multiprocessing to speed up the process
    13/4/2024 -- Multiprocessing can be used to speed up the process

Future Update:
    Add a function to covert mp4 to mp3
"""

transcribed_audio_file_name = "transcribed_speech.wav"
zoom_video_file_name = "xxx.mp3" # Set the path to the video file
file_path_txt = "transcription_MP3.txt"

# set language
language = "en-EN"

# separate for use multiple processes
aaa = 60  # 60++ is stable

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
    print("MP3 Duration:", total_duration, "s")

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
        print(f"Error: {e}")

    # Open the file
    try:
        subprocess.run(["open", file_path_txt], check=True)
        print(file_path_txt)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

    print("\ncomplete.")
