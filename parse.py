import geopy
import json
import csv
import pandas as pd
import reverse_geocoder as rg

from datetime import datetime
from geopy.geocoders import Nominatim


def get_country_count(df, manual=False):
    if manual:
        country_df = pd.DataFrame(columns=["Time","Latitude","Longitude","lat","lon","name","admin1","admin2","cc"])

        count = 0
        for index, row in df.iterrows():
            if count % 1000 == 0:
                print("\rNow on {}...".format(count), end="")
            count += 1
            if row["cc"] != "GB":
                country_df = country_df.append(row)
        return country_df
    else:
        return df[df.cc != "GB"]

def main():
    skip = True

    if not skip:
        df = pd.read_csv("output.csv", delimiter=",")
        #print(df)

        entries_list = []
        for index, row in df.iterrows():
            entries_list.append(("{:.7f}".format(row["Latitude"]), "{:.7f}".format(row["Longitude"])))
        entries_tuple = tuple(entries_list)
        
        #print(entries_tuple)
        results = rg.search(entries_tuple, mode=1)
        #print(results)

        in_len = len(df)
        out_len = len(results)
        assert in_len == out_len

        results_df = pd.DataFrame(results)
        combined_df = pd.concat([df, results_df], axis=1)
        #print(combined_df)

        combined_df.to_csv("to_csv.csv", index=False)
    else:
        print("Skipping country lookup.")
        combined_df = pd.read_csv("to_csv.csv", delimiter=",")
        print("Total rows: {}".format(len(combined_df)))
    country_df = get_country_count(combined_df)
    country_df.to_csv("to_csv_country.csv", index=False)

main()