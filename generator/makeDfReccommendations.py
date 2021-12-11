import pandas as pd

def createDfReccommendations(sp, playlist_tracks_df):
    ############################## Get reccommendations ##############################
    def get_recommendations(sp, tracks):
        data = []
        for x in tracks:
            results = sp.recommendations(seed_tracks=[x])  # default api limit of 20 is enough
            data.extend(results['tracks'])
        return data

    def get_tracks_df(tracks):
        """
        Transform and tidy Spotify track data
        :param tracks: list of Spotify track data
        :return: formatted pandas dataframe
        """
        tracks_df = pd.DataFrame(tracks)
        # Spread track values if not yet spread to columns
        if 'track' in tracks_df.columns.tolist():
            tracks_df = tracks_df.drop('track', 1).assign(**tracks_df['track'].apply(pd.Series))
        # Album
        tracks_df['album_id'] = tracks_df['album'].apply(lambda x: x['id'])
        tracks_df['album_name'] = tracks_df['album'].apply(lambda x: x['name'])
        tracks_df['album_release_date'] = tracks_df['album'].apply(lambda x: x['release_date'])
        tracks_df['album_tracks'] = tracks_df['album'].apply(lambda x: x['total_tracks'])
        tracks_df['album_type'] = tracks_df['album'].apply(lambda x: x['type'])
        # Album Artist
        tracks_df['album_artist_id'] = tracks_df['album'].apply(lambda x: x['artists'][0]['id'])
        tracks_df['album_artist_name'] = tracks_df['album'].apply(lambda x: x['artists'][0]['name'])
        # Artist
        tracks_df['artist_id'] = tracks_df['artists'].apply(lambda x: x[0]['id'])
        tracks_df['artist_name'] = tracks_df['artists'].apply(lambda x: x[0]['name'])
        select_columns = ['id', 'name', 'popularity', 'type', 'is_local', 'explicit', 'duration_ms', 'disc_number',
                        'track_number',
                        'artist_id', 'artist_name', 'album_artist_id', 'album_artist_name',
                        'album_id', 'album_name', 'album_release_date', 'album_tracks', 'album_type']
        # saved_tracks has ['added_at', 'tracks']
        if 'added_at' in tracks_df.columns.tolist():
            select_columns.append('added_at')
        return tracks_df[select_columns]

    def get_track_audio_df(sp, df):
        """
        Include Spotify audio features and analysis in track data.
        :param sp: Spotify OAuth
        :param df: pandas dataframe of Spotify track data
        :return: formatted pandas dataframe
        """
        df['genres'] = df['artist_id'].apply(lambda x: sp.artist(x)['genres'])
        df['album_genres'] = df['album_artist_id'].apply(lambda x: sp.artist(x)['genres'])
        # Audio features
        df['audio_features'] = df['id'].apply(lambda x: sp.audio_features(x))
        df['audio_features'] = df['audio_features'].apply(pd.Series)
        df = df.drop('audio_features', 1).assign(**df['audio_features'].apply(pd.Series))
        # Don't need sp.audio_analysis(track_id) audio analysis for this project
        return df

    recommendation_tracks = get_recommendations(sp, playlist_tracks_df[playlist_tracks_df['popularity'].between(70,100)].drop_duplicates(subset='id', keep="first")['id'].tolist()[:4])
    recommendation_tracks_df = get_tracks_df(recommendation_tracks)
    recommendation_tracks_df = get_track_audio_df(sp, recommendation_tracks_df)
    return recommendation_tracks_df