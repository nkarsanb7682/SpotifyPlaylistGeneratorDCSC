from flask import Flask, request, Response
import os
import pika
import datetime
import jsonpickle
import pickle

rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
print("Connecting to rabbitmq({})".format(rabbitMQHost))


# Info for client token
if os.environ['CLIENT_ID'] == None or os.environ.get('CLIENT_SECRET') == None:
    print("CLIENT_ID, and/or CLIENT_SECRET is None. Terminating server")
    quit()
else:
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ.get('CLIENT_SECRET')
spotifyClientTokenExpirationDate = datetime.datetime.now()
scope = "user-library-read user-follow-read user-top-read"
redirect_uri = 'http://localhost:5000/'

#################### Define flask app and routes ####################
app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return '<h1> Playlist Generation Server</h1><p> User is logged in</p><p>Click <a href={}>here</a> to logout</p>'.format(redirect_uri + 'apiv1/logout')

@app.route(('/apiv1/loginorregister'), methods=['POST'])
def login():
    data = request.get_json()
    access_token = data["access_token"]
    
    
@app.route(('/apiv1/logout'), methods=['GET'])
def logout():
    

    response = {
        "message" : "User logged out of spotify",
        }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route(('/apiv1/generateplaylist/'), methods=['POST'])
def generateplaylist():
    # Set up exchange to place requests on. Worker will grab requests off exchange, and process them
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=rabbitMQHost))
    channel = connection.channel()

    # Exchange to send requests to worker
    channel.exchange_declare(exchange='toGenerator',
                            exchange_type='direct')
    channel.queue_declare(queue='toGenerator')

    # Get data in request
    data = request.get_json()
    spPickled = data["spPickled"]
    username = data["username"]

    
    
    # Add request to queue, so playlist can be generated
    rbmqMessage = {
        "username" : username,
        "spPickled" : spPickled,
        "callback" : {
            "url": "http://localhost:5000",
            "data": {"some": "arbitrary", "data": "to be returned"}
        }
    }
    channel.basic_publish(exchange='', routing_key='toGenerator', body=pickle.dumps(rbmqMessage))
    
    response = {
        "action" : "queued",
        }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")



app.debug = True
# start flask app
app.run(host="0.0.0.0", port=5000)
    
