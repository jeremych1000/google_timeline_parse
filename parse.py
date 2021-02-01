import geopy
import json
import csv
import click
import pandas as pd
import reverse_geocoder as rg

from datetime import datetime
from geopy.geocoders import Nominatim


def get_all_country_dates(df, home_country, min_entries_per_day):
    dates = {}

    total_rows = len(df)
    for index, row in df.iterrows():
        if index % 100000 == 0:
            print(f"\rProcessing {index} of {total_rows}...", end="")

        time = datetime.strptime(row["Time"], "%Y-%m-%d %H:%M:%S")
        curr_date = datetime.strftime(time, "%Y-%m-%d")
        curr_country = row["cc"]

        if curr_date not in dates:
            dates[curr_date] = {curr_country: 1}
        else:
            try:
                dates[curr_date][curr_country] = dates[curr_date][curr_country] + 1
            except KeyError:
                dates[curr_date][curr_country] = 1

    print(f"\rDONE - Processed {index+1} of {total_rows}.")

    # now get rid of false positives
    print(
        f"Removing false positives (threshold: minimum {min_entries_per_day} entries required)..."
    )
    for k, v in dates.items():
        if (
            len(v) == 1 or home_country not in v.keys()
        ):  # ignore min_entries_per_day as probably lack of data
            dates[k] = [next(iter(v))]
        else:
            dates[k] = [kk for kk, vv in v.items() if vv >= min_entries_per_day]

    return dates


def get_out_of_country_dates(dates, home_country, count_part_day):
    days_fully_in_country = []
    days_partial_out_of_country = []
    days_fully_out_of_country = []

    for k, v in dates.items():
        if v == [home_country]:
            days_fully_in_country.append(k)
        else:  # more than one country
            if home_country in v:
                days_partial_out_of_country.append(k)
            else:
                days_fully_out_of_country.append(k)

    if count_part_day:  # partial out of country days are counted as out of country
        return days_partial_out_of_country + days_fully_out_of_country
    else:
        return days_fully_out_of_country


def get_no_days_in_year(list_dates):
    list_datetime = [datetime.strptime(date, "%Y-%m-%d") for date in list_dates]
    list_sorted = sorted(list_datetime, reverse=True)

    first_year = int(datetime.strftime(list_sorted[-1], "%Y"))
    last_year = int(datetime.strftime(list_sorted[0], "%Y"))

    year_dict = {}
    for i in range(first_year, last_year + 1):
        year_dict[str(i)] = 0

    for i in list_sorted:
        year = datetime.strftime(i, "%Y")
        year_dict[year] += 1

    return year_dict


@click.command()
@click.option(
    "--skip-country-lookup",
    default=False,
    is_flag=True,
    help="Whether to skip the reverse geocoding lookup",
)
@click.option(
    "--raw-csv",
    default="timeline_raw.csv",
    help="CSV Google Timeline Raw Output (from location-history-json-converter",
)
@click.option(
    "--country-csv",
    default="country.generated.csv",
    help="Reverse Geocoded CSV with countries",
)
@click.option("--home-country", default="GB", help="Home Country Code")
@click.option(
    "--count-part-day",
    default=False,
    is_flag=True,
    help="Whether to partial days as full day out of country",
)
@click.option(
    "--min-entries-per-day",
    default=50,
    help="Minimum entries per day of that country to filter out false positives",
)
def main(
    skip_country_lookup,
    raw_csv,
    country_csv,
    home_country,
    count_part_day,
    min_entries_per_day,
):
    dates_full_csv_name = "dates_full.generated.csv"
    dates_not_in_country_txt_name = "dates_not_in_country.generated.txt"

    if not skip_country_lookup:
        print(
            "Starting reverse lookup of all timeline entries to the respective country."
        )
        df = pd.read_csv(raw_csv, delimiter=",")
        # print(df)

        entries_list = []
        count = 0
        timeline_entries = len(df)
        for _, row in df.iterrows():
            if count % 10000 == 0:
                print(f"\rProcessed {count} entries of {timeline_entries}...", end="")
            count += 1
            entries_list.append(
                ("{:.7f}".format(row["Latitude"]), "{:.7f}".format(row["Longitude"]))
            )
        print(f"\rDONE - Processed {count} entries of {timeline_entries}.")
        entries_tuple = tuple(entries_list)

        # print(entries_tuple)
        results = rg.search(entries_tuple, mode=1)
        # print(results)

        in_len = len(df)
        out_len = len(results)
        assert in_len == out_len

        results_df = pd.DataFrame(results)
        combined_df = pd.concat([df, results_df], axis=1)
        # print(combined_df)

        combined_df.to_csv(country_csv, index=False)
        print(f"Finished country lookup, saved to {country_csv}.")
    else:
        print("Skipping country lookup...")
        combined_df = pd.read_csv(country_csv, delimiter=",")
        print("Total rows: {}".format(len(combined_df)))

    print("Getting all country dates...")
    all_dates = get_all_country_dates(combined_df, home_country, min_entries_per_day)
    with open(dates_full_csv_name, "w") as f:
        writer = csv.writer(f)
        header = ["date", "countries_visited"]
        writer.writerow(header)
        writer.writerows(all_dates.items())
    print("DONE - Getting all country dates...")

    print("Getting all out of country dates...")
    if count_part_day:
        print("WARNING - partial days are counted as full days")
    out_of_country_dates = get_out_of_country_dates(
        all_dates, home_country, count_part_day
    )
    print("DONE - Getting all out of country dates.")

    if out_of_country_dates:
        print(
            "{} days not detected in home country (earliest {}, latest {})".format(
                len(out_of_country_dates),
                out_of_country_dates[0],
                out_of_country_dates[-1],
            )
        )

        year_dict = get_no_days_in_year(out_of_country_dates)
        print("Days away per year: {}".format(year_dict))

        with open(dates_not_in_country_txt_name, "w") as outfile:
            outfile.write("Days away per year: {}\n---\n".format(year_dict))
            for i in range(len(out_of_country_dates)):
                outfile.write("{}\n".format(out_of_country_dates[i]))
            outfile.close()
    else:
        print("No days detected out of country.")


if __name__ == "__main__":
    main()