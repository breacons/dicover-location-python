import urllib.request
import datetime
from dateutil import rrule
import json
import os.path

url = 'http://13.48.149.61:8000/data/notify.json.{0}'
response = urllib.request.urlopen(url.format('2019-11-16-00-27'))
data = response.read()  # a `bytes` object
text = data.decode('utf-8')  # a `str`; this step can't be used if data is binary
print(text)

start = datetime.datetime.strptime('2019-11-16-00-27', '%Y-%m-%d-%H-%M').date()
end = datetime.datetime.strptime('2019-11-18-10-00', '%Y-%m-%d-%H-%M').date()

for time in rrule.rrule(rrule.MINUTELY, dtstart=start, until=end):
    if os.path.isfile('live-data/{0}.json'.format(time.strftime('%Y-%m-%d-%H-%M'))):
        continue

    try:
        print(url.format(time.strftime('%Y-%m-%d-%H-%M')))
        response = urllib.request.urlopen(url.format(time.strftime('%Y-%m-%d-%H-%M')))
        print(response.status)

        if response.status == 'HTTP Error 404: Not Found':
            continue

        # data = response.read()  # a `bytes` object
        # text = data.decode('utf-8')

        parsed = []

        for line in json.load(response) :
            if line["notifications"][0]['geoCoordinate']["longitude"] > 0:
                parsed.append({
                    "deviceId": line["notifications"][0]['deviceId'],
                    "latitude": line["notifications"][0]['geoCoordinate']["latitude"],
                    "longitude": line["notifications"][0]['geoCoordinate']["longitude"],
                    "timestamp": line["notifications"][0]["timestamp"],
                })

        with open('live-data/{0}.json'.format(time.strftime('%Y-%m-%d-%H-%M')), 'w', encoding='utf-8') as f:
            json.dump(parsed, f, ensure_ascii=False, indent=4)

        print('Saved ', time.strftime('%Y-%m-%d-%H-%M'))
    except Exception as e:
        print(e)
