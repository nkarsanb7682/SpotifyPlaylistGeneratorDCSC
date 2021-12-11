import pickle
import spotipy
import yaml
import os
from spotipy.oauth2 import SpotifyOAuth
from data_functions import offset_api_limit, get_artists_df, get_tracks_df, get_track_audio_df,\
    get_all_playlist_tracks_df, get_recommendations

with open("./spotify/spotify_details.yml", 'r') as stream:
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

while ["top_artists.pkl", "followed_artists.pkl", "top_tracks.pkl", "saved_tracks.pkl", "playlist_tracks.pkl", "recommendation_tracks.pkl"] not in os.listdir("./spotify"):
    # Spotify API calls and data manipulation
    # Save for later to be quickly read by multiple workflows
    if "top_artists.pkl" not in os.listdir("./spotify"):
        print("Getting, transforming, and saving top artist data...")
        top_artists = offset_api_limit(sp, sp.current_user_top_artists())
        top_artists_df = get_artists_df(top_artists)
        top_artists_df.to_pickle("./spotify/top_artists.pkl")

    if "followed_artists.pkl" not in os.listdir("./spotify"):
        print("Getting, transforming, and saving followed artist data...")
        followed_artists = offset_api_limit(sp, sp.current_user_followed_artists())
        followed_artists_df = get_artists_df(followed_artists)
        followed_artists_df.to_pickle("./spotify/followed_artists.pkl")

    if "top_tracks.pkl" not in os.listdir("./spotify"):
        print("Getting, transforming, and saving top track data...")
        top_tracks = offset_api_limit(sp, sp.current_user_top_tracks())
        top_tracks_df = get_tracks_df(top_tracks)
        top_tracks_df = get_track_audio_df(sp, top_tracks_df)
        top_tracks_df.to_pickle("./spotify/top_tracks.pkl")

    if "saved_tracks.pkl" not in os.listdir("./spotify"):
        print("Getting, transforming, and saving saved track data...")
        saved_tracks = offset_api_limit(sp, sp.current_user_saved_tracks())
        saved_tracks_df = get_tracks_df(saved_tracks)
        saved_tracks_df = get_track_audio_df(sp, saved_tracks_df)
        saved_tracks_df.to_pickle("./spotify/saved_tracks.pkl")

    playlist_tracks_df = dict()
    if "playlist_tracks.pkl" not in os.listdir("./spotify"):
        print("Getting, transforming, and saving playlist track data...")
        try:
            playlist_tracks_df = get_all_playlist_tracks_df(sp, sp.current_user_playlists())  # limit of 50 playlists by default
            playlist_tracks_df = get_track_audio_df(sp, playlist_tracks_df)
        except:
            print("Something went wrong")
        playlist_tracks_df.to_pickle("./spotify/playlist_tracks.pkl")
        # Create yaml dump
        playlist_dict = dict(zip(playlist_tracks_df['playlist_name'], playlist_tracks_df['playlist_id']))
        with open('./spotify/playlists.yml', 'w') as outfile:
            yaml.dump(playlist_dict, outfile, default_flow_style=False)
    else:
        with open("./spotify/playlist_tracks.pkl", 'rb') as pickle_file:
            playlist_tracks_df = pickle.load(pickle_file)

    if "recommendation_tracks.pkl" not in os.listdir("./spotify"):
        print("Getting, transforming, and saving tracks recommendations...")
        # Define a sample playlists to yield tracks to get recommendations for, 20 recommendations per track
        # recommendation_tracks = get_recommendations(sp, playlist_tracks_df)
        # recommendation_tracks = get_recommendations(sp, playlist_tracks_df[playlist_tracks_df['playlist_name']].drop_duplicates(subset='id', keep="first")['id'].tolist())
        # recommendation_tracks = get_recommendations(sp, playlist_tracks_df[playlist_tracks_df['playlist_name']])
        recommendation_tracks = get_recommendations(sp, playlist_tracks_df[playlist_tracks_df['popularity'].between(70,100)].drop_duplicates(subset='id', keep="first")['id'].tolist()[:4])
        recommendation_tracks_df = get_tracks_df(recommendation_tracks)
        recommendation_tracks_df = get_track_audio_df(sp, recommendation_tracks_df)
        recommendation_tracks_df.to_pickle("./spotify/recommendation_tracks.pkl")
