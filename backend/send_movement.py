from flask import Flask, jsonify, make_response, send_from_directory, send_file
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
import random

from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*', path='/socket.io')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

meeting_threshold = 5
running = False

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
    global running
    if running == False:
        running = True
        round = 0
        buffer = 0
        current_timeslot = {}

        with open("../notify/merged.json") as datafile:
            counter = json.load(datafile)

        df = pd.DataFrame(counter)
        print(df)

        df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
        df = df.sort_values('timestamp')

        print('All devices')
        print(pd.Series(df["deviceId"].value_counts()))
        device_ids = df.groupby(by='deviceId').count().sort_values('timestamp', ascending=False)


        # ezt írtam bele, nézd meg hogy jobb lett e, hanem akkor töröld
        print('Moving devices')
        moving_devices = device_ids[device_ids.timestamp > 400].index
        print(moving_devices)

        # df = df[(df.deviceId in moving_devices)]
        df = df[df['deviceId'].isin(moving_devices)]
        print('filtered')
        print(df)

        # eddig

        players = {}


        def random_color():
            return "%06x" % random.randint(0, 0xFFFFFF)

        def get_top_teams():
            current_teams = [player["team"] for player in current_timeslot.values()]
            return dict(itertools.islice(collections.OrderedDict(Counter(current_teams)).items(), 0, 5))

        def get_leaderboard():
            current_players = {key: player["score"] for key, player in current_timeslot.items()}
            sorted_players = sorted(current_players.items() ,  key=lambda item: item[1], reverse=True) 
            # print(sorted_players)
            return dict(itertools.islice(collections.OrderedDict(sorted_players).items(), 0, 5))

        def emit_update(): 
            if buffer > 10:
                data = {
                    "time": time_key.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "positions": current_timeslot,
                }

                data["teams"] = get_top_teams()
                data["leaderboard"] = get_leaderboard()

                #print('{0} - sending: {1}'.format(datetime.now(), json.dumps(data)))

                if data != {}:
                    socketio.emit('FromAPI', {'data': data})
                # buffer = 0
        
        current_time_key = None
        for index, row in df.iterrows():
            deviceId = row['deviceId']
            latitude = row['latitude']
            longitude = row['longitude']
            timestamp = row['timestamp']

            if deviceId not in players:
                players[deviceId] = {
                    "team": random_color(),
                    "score": 1, 
                    "met": {}
                }

            player = players[deviceId]
            score = player["score"]
            team = player["team"]
            met = player["met"]


            time_key = roundTime(timestamp, roundTo=1)
            time_key = timestamp
            emit_update()
            if not current_time_key or time_key > current_time_key:
                # emit_update()
                round += 1
                current_time_key = time_key

            if deviceId not in current_timeslot:
                current_timeslot[deviceId] = {
                    "score": score,
                    "team": team
                }

            for key, player in current_timeslot.items():
                if key != deviceId:
                    # met[key] = True
                    distance = geopy.distance.distance((latitude, longitude), (player["latitude"], player["longitude"])).m

                    if distance < meeting_threshold and player["team"] != team:
                        current_timeslot[deviceId]["score"] += 1
                        current_timeslot[key]["score"] += 1

                        if current_timeslot[deviceId]["score"] > current_timeslot[key]["score"]:
                            current_timeslot[key]["team"] = current_timeslot[deviceId]["team"]
                        elif current_timeslot[deviceId]["score"] < current_timeslot[key]["score"]:
                            current_timeslot[deviceId]["team"] = current_timeslot[key]["team"]
                buffer += (buffer % 10) + 1


            current_timeslot[deviceId]["latitude"] = latitude
            current_timeslot[deviceId]["longitude"] = longitude


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
    print('after')
    main()
