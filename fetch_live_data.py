import urllib.request
import json
import time
import datetime

parsed = []
while True:
    url = 'http://13.48.149.61:8000/notify.json'
    response = urllib.request.urlopen(url.format('2019-11-16-00-27'))

    for line in json.load(response):
        if line["notifications"][0]['geoCoordinate']["longitude"] > 0:
            parsed.append({
                "deviceId": line["notifications"][0]['deviceId'],
                "latitude": line["notifications"][0]['geoCoordinate']["latitude"],
                "longitude": line["notifications"][0]['geoCoordinate']["longitude"],
                "timestamp": line["notifications"][0]["timestamp"],
            })

    if len(parsed) > 500:
        with open('notify/{0}.json'.format(datetime.datetime.now()), 'w', encoding='utf-8') as f:
            json.dump(parsed, f, ensure_ascii=False, indent=4)

        parsed = []

    print('Fetched at {0}'.format(datetime.datetime.now()))
    time.sleep(1)

