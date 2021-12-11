import pandas as pd

def createDfLikedSongs(sp):
    ############################## Load playlist data ##############################
    # Get users liked songs
    numSongsToGet = 45
    columns = ['id', 'name', 'popularity', 'explicit', 'duration_ms', 'danceability', 'energy',
                            'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
                            'liveness', 'valence', 'tempo', 'time_signature', 'genres']
    likedSongsDictionary = {name:[] for name in columns}

    results = sp.current_user_saved_tracks(limit = numSongsToGet)
    for idx, item in enumerate(results['items']):
        track = item['track']
        likedSongsDictionary['id'].append(track['id'])
        likedSongsDictionary['name'].append(track['name'])

    # Add audio features for each song  'popularity', 'explicit'
    audioFeaturesColumns = ['duration_ms', 'danceability', 'energy',
                            'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
                            'liveness', 'valence', 'tempo', 'time_signature']
    results = sp.audio_features(likedSongsDictionary['id'])
    for idx, audioFeatures in enumerate(results):
        for feature in audioFeaturesColumns:
            likedSongsDictionary[feature].append(audioFeatures[feature])

    # Add general features of track
    audioAnalysisColumns = ['popularity', 'explicit']
    results = sp.tracks(list(likedSongsDictionary['id']))
    for idx, track in enumerate(results['tracks']):
        for feature in audioAnalysisColumns:
            likedSongsDictionary[feature].append(track[feature])
        
    # Get genre of artist, and assume its the same for the track
    results = sp.tracks(list(likedSongsDictionary['id']))
    for idx, trackGenre in enumerate(results['tracks']):
        artistname = trackGenre['artists'][0]['name']
        results = sp.search(q='artist:' + artistname, type='artist')
        likedSongsDictionary['genres'].append(results['artists']['items'][0]['genres'])

    # Convert dictionary into dataframe, and pickle
    likedSongsDf = pd.DataFrame.from_dict(likedSongsDictionary)    
    
    return likedSongsDf