import os
import jsonpickle
import pika
import requests
import pickle
import firebase_admin
import makeDfLikedSongs
import makeDfReccommendations
import randomForest
import pandas as pd
from firebase_admin import credentials
from firebase_admin import db

'''
some
'''

#################### Set up rabbit mq ####################
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
print(f"Connecting to rabbitmq({rabbitMQHost})")

rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()
rabbitMQChannel.queue_declare(queue='toGenerator')

# cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
cred = credentials.Certificate('/mnt/c/Users/nkars/Documents/2021 - 2022 Courses/CSCI 5253 - Data Center Scale Computing/SpotifyRec/generator/spotifyplaylistgenerator-48abb-firebase-adminsdk-7lvlp-35a28672c7.json')
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://spotifyplaylistgenerator-48abb-default-rtdb.firebaseio.com/'
})

print(' [*] Waiting for sentiment analysis requests. To exit press CTRL+C')

#################### Define callback funcion to generate playlist ####################
def callback(ch, method, properties, body):
    jsonRest = pickle.loads(body)
    username = jsonRest['username']
    sp = jsonpickle.loads(jsonRest['spPickled'])
    ref = db.reference('/')

    # Train random forest classifier (or retrain existing user's model to account for new songs in 'Liked Songs')
    try:
        print("Getting liked songs for {}...".format(username))
        playlist_tracks_df = makeDfLikedSongs.createDfLikedSongs(sp)
        print("Getting reccommendations for {}...".format(username))
        recommendation_tracks_df = makeDfReccommendations.createDfReccommendations(sp, playlist_tracks_df)
        print("Training and fitting random forest for {}...".format(username))
        model, X_recommend = randomForest.trainAndFitRandomForest(playlist_tracks_df, recommendation_tracks_df)

        # Make prediction
        recommendation_tracks_df['ratings'] = model.predict(X_recommend)
        recommendation_tracks_df['prob_ratings'] = model.predict_proba(X_recommend)[:,1]  # slice for probability of 1
        playlist = list(recommendation_tracks_df[recommendation_tracks_df['prob_ratings'] >= 0.5]['name'])
        
        # Check if user is already in db
        pickledModel = jsonpickle.dumps(model)
        if ((ref.get() == None) or (username not in dict(ref.get()).keys())):
            ref.set({
                username : {
                    'playlist0' : playlist,
                    'pickledModel' : pickledModel
                }
            })
        else:
            # retrain random forest classifier to account for new songs added to 'Liked Songs'
            user_ref = ref.child(username)
            numPlaylists = len(list(user_ref.get().keys()))
            playlistName = "playlist" + str(numPlaylists + 1)
            user_ref.update({
                playlistName : playlist,
                'pickledModel' : pickledModel
            })
    except Exception as e:
        print("SOMETHING BAD HAPPENED:")
        print(e)


    # Return callback to rest server
    print(" [x] {}:{}".format(method.routing_key, jsonRest['callback']))
    if "callback" in jsonRest:
        url = jsonRest["callback"]["url"]
        data = jsonRest["callback"]["data"]
        try:
            r = requests.post(url, data=data)
        except requests.exceptions.ConnectionError:
            print("Connection refused")


rabbitMQChannel.basic_consume(queue='toGenerator', on_message_callback=callback, auto_ack=True)
rabbitMQChannel.start_consuming()