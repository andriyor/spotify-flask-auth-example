# https://github.com/plamere/spotipy/blob/master/spotipy/util.py
import os

from flask import Flask, request, redirect, render_template, jsonify
from spotipy import Spotify, oauth2

app = Flask(__name__)

PORT_NUMBER = 8888
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, 
                               SPOTIPY_REDIRECT_URI, scope=SCOPE, cache_path=CACHE)

@app.route("/")
def index():
    return render_template('login.html')
    

@app.route("/login")
def login():
    # Auth Step 1: Authorization
    return redirect(sp_oauth.get_authorize_url())


@app.route("/callback")
def callback():
    access_token = ""
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = Spotify(access_token)
        results = sp.current_user()
        return jsonify(results)

    else:
        return render_template(htmlForLoginButton())


def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

if __name__ == "__main__":
    app.run(debug=True, port=8888)
