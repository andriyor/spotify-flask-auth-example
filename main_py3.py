import os
import json
import base64
from urllib.parse import urlencode
import pprint

from flask import Flask, request, redirect, render_template, jsonify
import requests

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response. 

app = Flask(__name__)

#  Client Keys
CLIENT_ID =  os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET =  os.environ.get('SPOTIPY_CLIENT_SECRET')

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://localhost"
PORT = 8888
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private user-read-currently-playing"
STATE = ""
SHOW_DIALOG_BOOL = True
SHOW_DIALOG_STR = str(SHOW_DIALOG_BOOL).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/")
def index():
    return render_template('login.html')


@app.route("/login")
def login():
    # Auth Step 1: Authorization
    url_args = urlencode(auth_query_parameters)
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_code = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_code),
        "redirect_uri": REDIRECT_URI
    }

    base64encoded = base64.b64encode(bytes("{}:{}".format(CLIENT_ID, CLIENT_SECRET), 'utf-8'))
    headers = {"Authorization": "Basic {}".format(base64encoded.decode('utf-8'))} 
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)
    pprint.pprint(playlist_data)

    # Get the User's Currently Playing Track
    currently_playing_api_endpoint = "{}/me/player/currently-playing".format(SPOTIFY_API_URL)
    currently_playing_response = requests.get(currently_playing_api_endpoint, headers=authorization_header)
    currently_playing_data = json.loads(currently_playing_response.text)
    pprint.pprint(currently_playing_data)

    # Combine profile and playlist data to display
    return render_template("user_profile.html", profile_data=profile_data, response_data=response_data)


@app.route("/refresh_token", methods=['POST'])
def refresh_token():
    # 7. Requesting access token from refresh token
    refresh_token = request.form['refresh_token']
    code_payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    base64encoded = base64.b64encode(bytes("{}:{}".format(CLIENT_ID, CLIENT_SECRET), 'utf-8'))
    headers = {"Authorization": "Basic {}".format(base64encoded.decode('utf-8'))} 
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)
    response_data = json.loads(post_request.text)
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
