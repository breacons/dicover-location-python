import os
import json


def live():
    directory = 'live-data'
    contents = []
    for filename in os.listdir(directory):
        if filename.endswith(".json") and not filename.startswith('merged'):
            with open('{0}/{1}'.format(directory, filename)) as f:
                data = json.load(f)
                contents += data
    with open('live-data/merged.json', 'w', encoding='utf-8') as f:
        json.dump(contents, f, ensure_ascii=False, indent=4)


def notify():
    directory = 'notify'
    contents = []
    for filename in os.listdir(directory):
        if filename.endswith(".json") and not filename.startswith('merged'):
            with open('{0}/{1}'.format(directory, filename)) as f:
                data = json.load(f)
                contents += data

    with open('notify/merged.json', 'w', encoding='utf-8') as f:
        json.dump(contents, f, ensure_ascii=False, indent=4)

notify()