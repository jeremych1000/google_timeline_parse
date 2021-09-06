import csv
import ast
import datetime
import click
from dataclasses import dataclass
from typing import Dict, List, Set

import pycountry

FILENAME = "dates_full.generated.csv"
CSV_NAME = "dates_edmans_format.csv"


@dataclass
class Entry:
    date: datetime.datetime
    country: any


@dataclass
class EntryRange:
    date_entered: datetime.datetime
    date_left: datetime.datetime
    countries: Set
    reason: str = "Leisure"


@click.command()
@click.option(
    "-i",
    "--inclusive",
    help="Include start and end dates",
    is_flag=True,
    type=bool,
    default=False,
)
@click.option(
    "-p",
    "--pretty-print",
    help="Use complete country names",
    is_flag=True,
    default=False,
)
def main(inclusive, pretty_print):
    days_list = []
    tmp_date = None

    with open(FILENAME) as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            countries = ast.literal_eval(row["countries_visited"])
            date = datetime.datetime.strptime(row["date"], "%Y-%m-%d")

            if countries != ["GB"]:
                if not tmp_date:
                    tmp_date = EntryRange(
                        date_entered=date,
                        date_left=date,
                        countries=set(countries),
                    )
                else:
                    tdelta = date - tmp_date.date_left
                    if tdelta.total_seconds() > 0:
                        # still same holiday
                        tmp_date.date_left = date
                        tmp_date.countries.update(countries)
                    else:
                        raise Exception
            else:
                # back home
                if tmp_date:
                    # bug where GB makes it in
                    tmp_date.countries.discard(
                        "GB"
                    )  # discard doesn't throw error if not exist
                    days_list.append(tmp_date)
                    tmp_date = None

    for d_range in days_list:
        print(d_range)
    print(f"{len(days_list)} trips in total")

    with open(CSV_NAME, "w") as f:
        f.write(
            "Date left the UK|Date returned to the UK|Reason for absence|Country travelled to\n"
        )
        for d_range in days_list:
            if pretty_print:
                countries = [
                    pycountry.countries.get(alpha_2=c).name for c in d_range.countries
                ]
            else:
                countries = d_range.countries
            f.write(
                f"{d_range.date_entered.strftime('%Y-%m-%d')}|{d_range.date_left.strftime('%Y-%m-%d')}|{d_range.reason}|{'; '.join(countries)}"
            )
            f.write("\n")


if __name__ == "__main__":
    main()