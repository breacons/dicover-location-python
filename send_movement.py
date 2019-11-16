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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

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


@app.route('/load')
def main():
    round = 0
    timeslots = {}
    current_timeslot = {}

    if load_timeslots:
        with open('processed/{0}'.format(load_timeslots), 'rb') as handle:
            timeslots = pickle.load(handle)
    else:
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
        # maxLongitude = df['longitude'].max()
        # minLongitude = df['longitude'].min()
        # maxLatitude = df['latitude'].max()
        # minLatitude = df['latitude'].min()

        df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
        df = df.sort_values('timestamp')

        # Filter data to top devices
        # df = df[(df['deviceId'] == '00:00:32:f7:4f:86') | (df['deviceId'] == '00:00:68:7d:04:fb ')  | (df['deviceId'] == '00:00:b1:52:80:90')  | (df['deviceId'] == '00:00:8a:15:94:3e')  | (df['deviceId'] == '00:00:65:eb:ad:3c')]

        # df = df.head(row_count)

        # Find devices with the most data
        # print(df['deviceId'].value_counts())

        # Plot all data points
        # df.plot.scatter(x='longitude', y='latitude', c='DarkBlue')
        # plt.show()

        players = {}

        def random_color():
            return len(players)

        # We iterate on all the rows to create movement dataset in the follow structure
        # {
        #     time: {
        #         deviceId: {
        #             longitude,
        #             latitude,
        #             score,
        #             team
        #         }
        #     }

        current_time_key = None
        for index, row in df.iterrows():
            # print('Processing row: {0}'.format(index))
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
                # Send last timeslot to socket
                # values = list(timeslots.values())

                data = {
                    "time": time_key.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "positions": current_timeslot,
                }

                if round % 10 == 1:
                    print("Sending extra data")
                    current_teams = [player["team"] for player in current_timeslot.values()]
                    current_players = {key: player["score"] for key, player in current_timeslot.items()}
                    data["teams"] = dict(
                        itertools.islice(collections.OrderedDict(Counter(current_teams)).items(), 0, 5))
                    data["leaderboard"] = dict(
                        itertools.islice(collections.OrderedDict(Counter(current_players)).items(), 0, 5))

                print('{0} - sending: {1}'.format(datetime.now(), json.dumps(data)))

                if data != {}:
                    socketio.emit('FromAPI', {"data": data})

                round += 1

                current_time_key = time_key

            if deviceId not in current_timeslot:
                current_timeslot[deviceId] = {}

            for key, player in current_timeslot.items():
                # deviceId belongs to the currently moved user
                # key belongs to another user who is on the network at the same time
                if key != deviceId:
                    # we calculate the distance between the two user
                    distance = geopy.distance.distance((latitude, longitude),
                                                       (player["latitude"], player["longitude"])).m

                    # if they are close and not in the same team then the interaction happens
                    if distance < meeting_threshold and player["team"] != team:
                        # print('At {0}, {1} met with {2}'.format(time_key, deviceId, key))
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
    socketio.run(app, host='0.0.0.0', debug=False)
    print('after')
    main()
