# google_timeline_parse

Find how many days you are out of your own home country.

## Requirements
- [A copy of your Google Timeline in JSON](https://takeout.google.com/settings/takeout)
- [location-history-json-converter](https://github.com/Scarygami/location-history-json-converter/)
- Python
    - Pandas
    - reverse-geocoder
    - json
    - csv
   
## Instructions
- Clone
- Convert Google Timeline JSON to less heavy file using location-history-json-converter
    - e.g. `python location_history_json_converter.py location.json timeline_raw.csv -f csv` 
- If running for the firs time, ensure `skip = False` in main()
- `python parse.py` (this assumes taking in CSV)
- Look for newly generated files.
