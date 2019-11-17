import urllib.request
import json
import time
import datetime

parsed = []
while True:
    try:
        urlData = 'http://13.48.149.61:8000/notifycache.json'
        webURL = urllib.request.urlopen(urlData)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        content = data.decode(encoding)

        content = '[' + content[:-2] + ']'
        for line in json.loads(content):
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
                print('Saved {0}'.format(datetime.datetime.now()))

            parsed = []

        print('Fetched at {0}'.format(datetime.datetime.now()))
        time.sleep(1)
    except Exception as e:
        print(e)

