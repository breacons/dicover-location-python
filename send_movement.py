from flask import Flask, jsonify, make_response
from flask_socketio import SocketIO, emit
import copy
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
import json
import geopy.distance
import numpy as np
import pickle
import operator
import itertools
import collections

from flask_cors import CORS, cross_origin


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*', path='/socket.io')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


file_name = 'notify.json.2019-11-10-18-05'
# live_data = 'merged.json'
live_data = False
row_count = 50000
meeting_threshold = 5
load_timeslots = False


# Rounding time to roundTo seconds
def roundTime(dt=None, roundTo=60):
    if dt == None: dt = datetime.now()
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + roundTo / 2) // roundTo * roundTo
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('connect')
def test_connect():
    print('Client connected')


@app.route('/load')
@cross_origin()
def main():
    round = 0
    timeslots = {}
    current_timeslot = {}


    if live_data:
        with open("live-data/{0}".format(live_data)) as datafile:
            counter = json.load(datafile)
    else:
        counter = []
    with open("data/{0}".format(file_name)) as datafile:
        data = json.load(datafile)

        for line in data:
            if line["notifications"][0]['geoCoordinate']["longitude"] > 0:
                counter.append({
                    "deviceId": line["notifications"][0]['deviceId'],
                    "latitude": line["notifications"][0]['geoCoordinate']["latitude"],
                    "longitude": line["notifications"][0]['geoCoordinate']["longitude"],
                    "timestamp": line["notifications"][0]["timestamp"],
                })

    df = pd.DataFrame(counter)
    print(df)

    df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
    df = df.sort_values('timestamp')

    players = {}

    def random_color():
        return len(players)

    def get_top_teams():
        current_teams = [player["team"] for player in current_timeslot.values()]
        return dict(itertools.islice(collections.OrderedDict(Counter(current_teams)).items(), 0, 5))

    def get_leaderboard():
        current_players = {key: player["score"] for key, player in current_timeslot.items()}
        return dict(itertools.islice(collections.OrderedDict(Counter(current_players)).items(), 0, 5))


    current_time_key = None
    for index, row in df.iterrows():
        deviceId = row['deviceId']
        latitude = row['latitude']
        longitude = row['longitude']
        timestamp = row['timestamp']

        if deviceId not in players:
            players[deviceId] = {
                "team": random_color(),
                "score": 1
            }

        player = players[deviceId]
        score = player["score"]
        team = player["team"]

        time_key = roundTime(timestamp, roundTo=10)
        if not current_time_key or time_key > current_time_key:
            data = {
                "time": time_key.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "positions": current_timeslot,
            }

            if round % 10 == 1:
                data["teams"] = get_top_teams()
                data["leaderboard"] = get_leaderboard()

                print('{0} - sending: {1}'.format(datetime.now(), json.dumps(data)))

            if data != {}:
                socketio.emit('FromAPI', {'data': data})

            round += 1

            current_time_key = time_key

        if deviceId not in current_timeslot:
            current_timeslot[deviceId] = {}

        for key, player in current_timeslot.items():
            if key != deviceId:
                distance = geopy.distance.distance((latitude, longitude), (player["latitude"], player["longitude"])).m

                if distance < meeting_threshold and player["team"] != team:
                    if player["score"] > score:
                        player["score"] += (score + 10)
                        current_timeslot[deviceId]["team"] = player["team"]
                    else:
                        score += (player["score"] + 10)
                        player["team"] = team

        current_timeslot[deviceId]["latitude"] = latitude
        current_timeslot[deviceId]["longitude"] = longitude
        current_timeslot[deviceId]["team"] = team
        current_timeslot[deviceId]["score"] = score


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
    print('after')
    main()
