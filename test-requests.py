import requests
import json
import os
import yaml
import spotipy
import jsonpickle
from spotipy import SpotifyOAuth

REST = os.getenv("REST") or "localhost:5000"

def mkReq(reqmethod, endpoint, data):
    print(f"Response to http://{REST}/{endpoint} request is")
    jsonData = json.dumps(data)
    response = reqmethod(f"http://{REST}/{endpoint}", data=jsonData,
                         headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print(jsonResponse)
        return jsonResponse
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
        return response.text

# Log user in
isLoggedIn = False
username = None
with open("spotify_details.yml", 'r') as stream:
    spotify_details = yaml.safe_load(stream)

# https://developer.spotify.com/web-api/using-scopes/
scope = "user-library-read user-follow-read user-top-read playlist-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=spotify_details['client_id'],
    client_secret=spotify_details['client_secret'],
    redirect_uri=spotify_details['redirect_uri'],
    scope=scope,
    requests_timeout=60
))
username = sp.current_user()['display_name']
if not username == None:
    isLoggedIn = True

spPickled = jsonpickle.dumps(sp)
mkReq(requests.post, "apiv1/generateplaylist/", data= {
    'username' : username,
    'spPickled' : spPickled
})