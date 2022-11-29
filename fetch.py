import datetime
import time
import json

import requests


today = datetime.date.today().isoformat()
outfile_name = 'sd-roadkill.geojson'

results_per_page = 1000

url = 'https://services1.arcgis.com/PwrabBhZHUggYYSp/ArcGIS/rest/services/survey123_2fa2f046e8e0422fb99f2836d19beb52_stakeholder/FeatureServer/1/query'  # noqa

outfields = [
    'PCN',
    'Highway',
    'Species',
    'Sex',
    'Found',
    'Comments',
    'CreationDate'
]

params = {
    'f': 'geojson',
    'spatialRel': 'esriSpatialRelIntersects',
    'outFields': ','.join(outfields),
    'returnGeometry': True,
    'where': '1=1',
    'outSR': '4326',
    'resultOffset': 0,
    'resultRecordCount': results_per_page
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'  # noqa
}

data_features = []


def fetch_data(offset=0):

    params['resultOffset'] = offset

    r = requests.get(
        url,
        headers=headers,
        params=params
    )

    r.raise_for_status()
    print(f'Fetched records starting at {offset}...')

    data = r.json()['features']

    if data:

        # filter out records with no coordinates
        data = [x for x in data if tuple(x['geometry']['coordinates']) != (0, 0)]  # noqa

        for feature in data:

            # fix epoch time
            timestamp = feature['properties']['CreationDate']
            converted = datetime.datetime.fromtimestamp(timestamp / 1000.0).date().isoformat()  # noqa
            feature['properties']['CreationDate'] = converted

            # don't need super decimal precision
            feature['geometry']['coordinates'] = [round(x, 5) for x in feature['geometry']['coordinates']]  # noqa

        data_features.extend(data)

        offset = offset + results_per_page
        time.sleep(0.2)
        fetch_data(offset)

    else:
        return None


fetch_data()

geoj = {
    'type': 'FeatureCollection',
    'updated': today,
    'features': data_features
}

with open(outfile_name, 'w') as outfile:
    outfile.write(json.dumps(geoj))
