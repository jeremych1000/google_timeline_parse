import geopy
import json
import reverse_geocoder as rg

from datetime import datetime
from geopy.geocoders import Nominatim

class entry():
    def __init__(self, timestamp, latitude, longitude):
        timestamp = int(timestamp) / 1000 # google counts in milliseconds
        latitude = str(latitude)
        longitude = str(longitude)
        self.timestamp = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.latitude = "{}.{}".format(latitude[0:2], latitude[2:])
        self.longitude = "{}.{}".format(longitude[0:2], longitude[2:])


def format_lat_long(latitude, longitude):
    pass


def find_country(latitude, longitude, offline=True):
    if offline:
        results = rg.search((latitude, longitude))
        print(results)
        return results
        
    else:
        geolocator = Nominatim()
        location = geolocator.reverse("{}, {}".format(latitude, longitude))
        print(location.address)
        print((location.latitude, location.longitude))
        
        country = location.raw["address"]["country"]
        
        print(country)
        return country


def find_day(timestamp):
    pass


def read_json(input="test.json"):
    with open(input) as input_json:
        return json.load(input_json)


def strip_json(input_json):
    # "timestampMs" : "1530209499870",
    # "latitudeE7" : 515014068,
    # "longitudeE7" : -1919385,
    # 
    ret = []
    for line in input_json["locations"]:
        ret.append(entry(
            timestamp = line["timestampMs"],
            latitude = line["latitudeE7"],
            longitude = line["longitudeE7"]
        ))
    return ret


def main():
    entries = read_json("test.json")
    print(entries)

    entries_parsed = strip_json(entries)
    print("{} entries parsed.".format(len(entries_parsed)))

    for entry in entries_parsed:
        country = find_country(entry.latitude, entry.longitude)



main()