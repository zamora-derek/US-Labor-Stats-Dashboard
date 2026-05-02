import pandas as pd
import requests
import os
from datetime import date

# list(series_map.keys())

url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
key = '7dfab3a0b7434080b003818155c0e896'

current_year = date.today().year

series_dict = {
    'JTS000000000000000JOR': 'Jobs',
    'LNS11300000': 'Labor Force',
    'CES0500000003': 'Hourly Earnings',
    'CUUR0000SA0': 'CPI',
    'LNS14000000': 'Unemployement Rate',
    'CES0000000001': 'Non Farm Emp'
}


def fetch_data(series, start, end, api):
    temp_start = start

    df_final = []
    all_parts = []

    while temp_start <= end:

        temp_end = min(temp_start + 19, end)

        

        response = requests.post(url, json={
            "seriesid": series,
            "startyear": str(temp_start),
            "endyear": str(temp_end),
            "registrationkey": api
        })

        results = response.json()['Results']['series']

        records = []
        for s in results:
            s_id = s['seriesID']
            for i in s['data']:

                if i['period'] != 'M13':  # ignores the last row

                    raw_val = i['value']

                    try:  # try to convert to float
                        float_val = float(raw_val)
                    except ValueError:
                        # includes empty/-/non numbers
                        float_val = float('nan')

                    records.append({
                        "Date": pd.to_datetime(f"{i['year']}-{i['period'][1:]}-01"), # date converted to real date
                        "Metric": series_dict[s_id],
                        "Value": float_val  # uses clean float value
                    })

        # aligns data as not all have the same dates
        if records:
            df_part = pd.DataFrame(records).pivot(index='Date', columns='Metric', values='Value')
            all_parts.append(df_part)

        temp_start = temp_end + 1  # start will be less than end if need to rerun
                                    # must happen after

    # combines into one final df
    if all_parts:
        df_final = pd.concat(all_parts).sort_index()
        return df_final
    return None


if __name__ == "__main__":
    df = fetch_data(list(series_dict.keys()), 2000, current_year, key) # fetches data from 2000 to current year
    if df is not None:
    
        df.to_csv('data/bls_data.csv')
