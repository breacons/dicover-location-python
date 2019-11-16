import copy
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
import json
import geopy.distance
import numpy as np
import matplotlib
import pickle

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import matplotlib.image as mpimg

sns.set_palette("bright")
sns.set(rc={'figure.figsize': (11.7, 8.27)})

file_name = 'notify.json.2019-11-10-18-05'
live_data = 'merged.json'
row_count = 500
meeting_threshold = 5
load_timeslots = False

maxLongitude = 24.826288783593107
minLongitude = 24.82266643082625
maxLatitude = 60.18623494565414
minLatitude = 60.18458550228668

# Rounding time to roundTo seconds
def roundTime(dt=None, roundTo=60):
    if dt == None: dt = datetime.now()
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + roundTo / 2) // roundTo * roundTo
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)


timeslots = {}

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

    df = df.head(row_count)

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
    for index, row in df.iterrows():
        print('Processing row: {0}'.format(index))
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
        if time_key not in timeslots:
            values = list(timeslots.values())

            if len(values) > 0:
                timeslots[time_key] = copy.deepcopy(values[-1])
            else:
                timeslots[time_key] = {}

        if deviceId not in timeslots[time_key]:
            timeslots[time_key][deviceId] = {}

        for key, player in timeslots[time_key].items():
            if key != deviceId:
                distance = geopy.distance.distance((latitude, longitude), (player["latitude"], player["longitude"])).m

                if distance < meeting_threshold and player["team"] != team:
                    # print('At {0}, {1} met with {2}'.format(time_key, deviceId, key))
                    if player["score"] > score:
                        player["score"] += (score + 10)
                        timeslots[time_key][deviceId]["team"] = player["team"]
                    else:
                        score += (player["score"] + 10)
                        player["team"] = team

        timeslots[time_key][deviceId]["latitude"] = latitude
        timeslots[time_key][deviceId]["longitude"] = longitude
        timeslots[time_key][deviceId]["team"] = team
        timeslots[time_key][deviceId]["score"] = score

    with open('processed/{0}-{1}-{2}.pickle'.format(file_name, row_count, datetime.timestamp(datetime.now())),
              'wb') as handle:
        pickle.dump(timeslots, handle, protocol=pickle.HIGHEST_PROTOCOL)

print(list(timeslots.values())[-1].values())
teams = Counter([player["team"] for player in list(timeslots.values())[-1].values()])
print('Teams with the most members')
print(teams)

qualitative_colors = sns.color_palette("Set3", len(teams))

fig, ax = plt.subplots(figsize=(5, 5))
ax.set_xlim(minLongitude, maxLongitude)
ax.set_xlabel('Longitude', fontsize=20)
ax.set_ylim(minLatitude, maxLatitude)
ax.set_ylabel('Latitude', fontsize=20)

map_img = mpimg.imread('vare.png')


def get_data(i):
    print("Animation step {0}".format(i))

    key = list(timeslots.keys())[i]
    slot = timeslots[key]
    values = slot.values()
    ax.set_title(key, fontsize=10)
    x = [value["longitude"] for value in values]
    y = [value["latitude"] for value in values]
    s = [value["score"] for value in values]
    c = np.array([value["team"] for value in values])

    return x, y, c, s


def init():
    x, y, col, s = get_data(0)
    scat = ax.scatter(x, y, c=col, s=s)
    return scat


def animate(i):
    plt.cla()
    ax.set_xlim(minLongitude, maxLongitude)
    ax.set_ylim(minLatitude, maxLatitude)
    ax.set_yticks([])
    ax.set_xticks([])
    x, y, col, s = get_data(i)
    scat = ax.scatter(x, y, c=col, s=s, alpha=0.5, zorder=2, )
    ax.imshow(map_img,
              aspect=ax.get_aspect(),
              extent=ax.get_xlim() + ax.get_ylim(),
              zorder=1)

    return scat


anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(timeslots), interval=50, )

plt.show()
