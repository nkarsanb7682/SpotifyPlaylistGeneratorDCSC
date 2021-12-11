import pandas as pd
import numpy as np
import yaml
import random

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier

'''
Source: https://github.com/anthonyli358/spotify-recommender-systems
'''

def trainAndFitRandomForest(playlist_tracks_df, recommendation_tracks_df):
    ############################## Load playlist data ##############################
    # Load list of playlist ids for my favourite playlists

    playlist_tracks_df['ratings'] = [round(random.uniform(0,1)) for _ in range(len(playlist_tracks_df['id']))] # playlist_tracks_df['id'].apply(lambda x: 1 if x in playlists.values() else 0)

    recommendation_tracks_df = recommendation_tracks_df.drop_duplicates(subset='id', keep="first").reset_index()
    # Avoid data leakage
    recommendation_tracks_df = recommendation_tracks_df[~recommendation_tracks_df['id'].isin(playlist_tracks_df['id'].tolist())]

    ############################## Get training and testing data ##############################
    # Training data
    X = playlist_tracks_df[['popularity', 'explicit', 'duration_ms', 'danceability', 'energy',
                            'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
                            'liveness', 'valence', 'tempo', 'time_signature', 'genres']]  # order here is important for xgboost later
    y = playlist_tracks_df['ratings']

    # Drop NA
    X = X.dropna()
    recommendation_tracks_df = recommendation_tracks_df.dropna()

    # Create genre columns (one-hot encoding)
    X = X.drop('genres', 1).join(X['genres'].str.join('|').str.get_dummies())
    X_recommend = recommendation_tracks_df.copy()
    X_recommend = X_recommend.drop('genres', 1).join(X_recommend['genres'].str.join('|').str.get_dummies())

    # Ensure features are consistent across training, test, and evaluation
    X = X[X.columns.intersection(X_recommend.columns)]
    X_recommend = X_recommend[X_recommend.columns.intersection(X.columns)]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train.head()

    ############################## Create random forest classifiers ##############################
    # Random Forest Classifier
    rfc = RandomForestClassifier(n_estimators = 1000, random_state=42)
    rfc_gcv_parameters = {'min_samples_leaf': [1, 3, 5, 8], 
                        'max_depth': [3, 4, 5, 8, 12, 16, 20], 
                        }
    rfe_gcv = GridSearchCV(rfc, rfc_gcv_parameters, n_jobs=-1, cv=StratifiedKFold(2), verbose=1, scoring='roc_auc')
    rfe_gcv.fit(X_train, y_train)

    return rfe_gcv, X_recommend