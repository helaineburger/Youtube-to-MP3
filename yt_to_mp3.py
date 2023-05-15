import os
import sys
import subprocess
from pytube import YouTube
import ffmpeg
import tempfile
from mutagen.easyid3 import EasyID3

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Get the path to the ffmpeg executable
ffmpeg_path = os.path.join(os.getcwd(), resource_path('bin'), resource_path('ffmpeg.exe'))

# Check if the ffmpeg executable exists
if not os.path.exists(ffmpeg_path):
    print('Error: ffmpeg not found')
    sys.exit(1)

# Get the directories
temp_dir = tempfile.gettempdir()
download_dir = download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

while True:
    print('''##################
# Youtube to MP3 #
##################\n''')
    
    # Prompt user for YouTube video URL
    url = input("Youtube URL: ")

    # Create a YouTube object
    youtube = YouTube(url)
    dirty_title = youtube.title
    title = dirty_title.replace('\\','').replace('/','').replace('*','').replace('?','').replace('"','').replace('<','').replace('>','').replace('|','').replace(':','')
    artist = youtube.author.replace('\\','').replace('/','').replace('*','').replace('?','').replace('"','').replace('<','').replace('>','').replace('|','').replace(':','')

    print('\nSong: ', title)
    print('Artist: ', artist)

    # Get the audio streams
    audio_streams = youtube.streams.filter(only_audio=True).order_by('abr').desc()

    # Print the available audio streams
    print("\nAvailable audio streams:")
    for i, stream in enumerate(audio_streams):
        print(f"{i+1}. {stream.abr} - {stream.mime_type}")

    audio_index = int(input("\nEnter the number of the audio stream you want to download: "))
    audio_stream = audio_streams[audio_index - 1]

    print(f"\nDownloading audio {audio_stream.abr}...")
    audio_file = audio_stream.download(output_path=temp_dir, filename=f"{title}_temp.mp4")

    # Convert to mp3
    input_audio = ffmpeg.input(audio_file)
    output_path = os.path.join(download_dir, f"{title}.mp3")
    output_audio = ffmpeg.output(input_audio, output_path, ac=2, ab='320k', ar='44100', format='mp3')
    #ffmpeg.run(output_audio)
    cmd = [ffmpeg_path, '-i', audio_file, '-ac', '2', '-ab', '320k', '-ar', '44100', '-f', 'mp3', output_path]
    subprocess.run(cmd, check=True)

    # Add metadata
    audio = EasyID3(output_path)
    audio['title'] = title
    audio['artist'] = artist
    audio.save()
 
    # Cleanup
    os.remove(audio_file)

    print(f"\nDownload finished! See Downloads folder. \n -------------------------------------\n")
