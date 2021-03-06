import urllib.request
import datetime
from dateutil import rrule
import json
import os.path


url = 'http://13.48.149.61:8000/data/notify.json.{0}'
start = datetime.datetime.strptime('2019-11-16-00-27', '%Y-%m-%d-%H-%M').date()
end = datetime.datetime.strptime('2019-11-18-10-00', '%Y-%m-%d-%H-%M').date()

for time in rrule.rrule(rrule.MINUTELY, dtstart=start, until=end):
    if os.path.isfile('live-data/{0}.json'.format(time.strftime('%Y-%m-%d-%H-%M'))):
        continue

    try:
        urlData = url.format(time.strftime('%Y-%m-%d-%H-%M'))
        print(urlData)
        webURL = urllib.request.urlopen(urlData)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        content = data.decode(encoding)

        content = content.replace('[[', '[')
        content = content.replace('"tagVendorData": null}]}]', '"tagVendorData": null}]},')

        print(content)
        print(json.loads(content))

        continue

        print(url.format(time.strftime('%Y-%m-%d-%H-%M')))
        response = urllib.request.urlopen(url.format(time.strftime('%Y-%m-%d-%H-%M')))

        if response.status == 'HTTP Error 404: Not Found':
            continue

        # data = response.read()  # a `bytes` object
        # text = data.decode('utf-8')

        parsed = []

        print(response)

        for line in json.load(response):
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
