import os
import jsonpickle
import pika
import requests
import pickle
import firebase_admin
import makeDfLikedSongs
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
    print(type(sp))

    # Check if user already has a classifier stored
    ref = db.reference('/')
    print("USERS IN DB: ", dict(ref.get()).keys())
    if ((ref.get() == None) or (username not in dict(ref.get()).keys())):
        # Train random forest classifier
        model = 
        # Make prediction
        playlist = 
        ref.set({
            username : {
                'playlistName' : playlist,
                'model' : model
            }
        })
    else:
        # retrain random forest classifier to account for new songs added to 'Liked Songs'
        pass
    print(ref.get())


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