import geopy
import json
import csv
import pandas as pd
import reverse_geocoder as rg

from datetime import datetime
from geopy.geocoders import Nominatim


def get_not_home(df, home='GB', manual=False):
    print("Removing all rows that are not {}...".format(home))
    if manual:
        country_df = pd.DataFrame(columns=["Time","Latitude","Longitude","lat","lon","name","admin1","admin2","cc"])

        count = 0
        for index, row in df.iterrows():
            if count % 1000 == 0:
                print("\rNow on {}...".format(count), end="")
            count += 1
            if row["cc"] != home:
                country_df = country_df.append(row)
        return country_df
    else:
        return df[df.cc != home]


def get_distinct_dates(df):
    dates = []
    for index, row in df.iterrows():
        time = datetime.strptime(row["Time"], "%Y-%m-%d %H:%M:%S")
        dates.append(datetime.strftime(time, "%Y-%m-%d"))
    
    #now get rid of duplicates
    ret = pd.Series(dates).drop_duplicates().tolist()    
    #or from https://stackoverflow.com/questions/45746312/one-liner-to-remove-duplicates-keep-ordering-of-list
    #ret = sorted(set(dates), key=dates.index)
    return ret


def get_no_days_in_year(list_dates):
    list_datetime = [datetime.strptime(date, "%Y-%m-%d") for date in list_dates]
    list_sorted = sorted(list_datetime)
    
    first_year = int(datetime.strftime(list_sorted[0], "%Y"))
    last_year = int(datetime.strftime(list_sorted[-1], "%Y"))

    year_dict = {}
    for i in range(first_year, last_year+1):
        year_dict[str(i)] = 0
    
    for i in list_sorted:
        year = datetime.strftime(i, "%Y")
        year_dict[year] += 1
    
    return year_dict

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
    
    country_df = get_not_home(combined_df, home='GB')
    country_df.to_csv("to_csv_country.csv", index=False)

    distinct_dates = get_distinct_dates(country_df)
    print("{} days not detected in home country (first {}, last {})".format(len(distinct_dates), distinct_dates[-1], distinct_dates[0]))

    year_dict = get_no_days_in_year(distinct_dates)
    print("Days away per year: {}".format(year_dict))

    with open('dates_not_in_uk.txt', 'w') as outfile:
        outfile.write("Days away per year: {}\n---\n".format(year_dict))
        for i in range(len(distinct_dates)):
            outfile.write("{}\n".format(distinct_dates[i]))
        outfile.close()

main()