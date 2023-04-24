from base64 import b64encode
import os
import environs
import requests
import youtube_d#import environment varibales
from environs import Env
env = Env()
env.read_env()
# Get the Spotify API credentials from the environment variables
SPOTIFY_CLIENT_ID = env('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = env('SPOTIFY_CLIENT_SECRET')
# Replace SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET with your own Spotify API credentials

# Replace PLAYLIST_ID with the ID of the Spotify playlist you want to download
PLAYLIST_ID = "37i9dQZF1EJMeGJot5XqO9"

# Set the path where you want to download the songs
DOWNLOAD_PATH = "./download/spotify"

# Get an access token from the Spotify API
auth_header = {
    "Authorization": "Basic {}".format(
        b64encode(
            "{}:{}".format(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET).encode("utf-8")
        ).decode("utf-8")
    )
}
auth_data = {"grant_type": "client_credentials"}
auth_response = requests.post("https://accounts.spotify.com/api/token",
                              headers=auth_header, data=auth_data)
auth_response.raise_for_status()
access_token = auth_response.json()["access_token"]

# Use the access token to get the tracks in the playlist
headers = {"Authorization": "Bearer {}".format(access_token)}
response = requests.get("https://api.spotify.com/playlists/{}".format(PLAYLIST_ID),
                        headers=headers)
response.raise_for_status()
tracks = response.json()["items"]
# https://open.spotify.com/playlist/37i9dQZF1EJMeGJot5XqO9?si=973d1078637d409c
# Iterate through the tracks and download them from YouTube
for track in tracks:
    # Get the track name and artist
    track_name = track["track"]["name"]
    artist = track["track"]["artists"][0]["name"]

    # Search for the track on YouTube
    youtube_query = "{} {}".format(track_name, artist)
    youtube_url = "https://www.youtube.com/results?search_query={}".format(
        youtube_query.replace(" ", "+")
    )
    youtube_response = requests.get(youtube_url)
    youtube_response.raise_for_status()
    youtube_html = youtube_response.text

    # Extract the first YouTube video from the search results
    youtube_id_start = youtube_html.index("watch?v=") + len("watch?v=")
    youtube_id_end = youtube_html.index("\"", youtube_id_start)
    youtube_id = youtube_html[youtube_id_start:youtube_id_end]

    # Download the YouTube video with youtube-dl
    youtube_url = "https://www.youtube.com/watch?v={}".format(youtube_id)
    ydl_opts = {
        "outtmpl": "{}/%(title)s.%(ext)s".format(DOWNLOAD_PATH),
        "format": "bestaudio/best",
        "postprocessors": 
        [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
