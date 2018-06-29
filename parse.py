import geopy
import json


class entry():
    def __init__(self, timestamp, latitude, longitude):
        self.timestamp = timestamp
        self.lat = latitude
        self.long = longitude


def format_lat_long(lat, long):
    pass


def find_country(lat, long):
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
    for line in input_json:
        ret.append(entry(
            timestamp = line["timestampMs"],
            latitude = line["latitudeE7"],
            longitude = line["longitudeE7"]
        ))
    return ret


def main():
    from geopy.geocoders import Nominatim
    geolocator = Nominatim()
    location = geolocator.reverse("52.509669, 13.376294")
    print(location.address)
    print((location.latitude, location.longitude))
    print(location.raw["address"]["country"])

    entries = read_json("test.json")
    print(entries)

    entries_parsed = strip_json(entries)
    print(entries_parsed)


main()