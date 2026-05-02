import pandas as pd
import requests
import os
from datetime import date

# list(series_map.keys())

url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
key = '7dfab3a0b7434080b003818155c0e896'
current_year = date.today().year


#

# prompted by LLM
# series for all 50 states + DC for total non farmer jobs
state_series_dict = {
    'SMU01000000000000001': 'AL', 'SMU02000000000000001': 'AK',
    'SMU04000000000000001': 'AZ', 'SMU05000000000000001': 'AR',
    'SMU06000000000000001': 'CA', 'SMU08000000000000001': 'CO',
    'SMU09000000000000001': 'CT', 'SMU10000000000000001': 'DE',
    'SMU11000000000000001': 'DC', 'SMU12000000000000001': 'FL',
    'SMU13000000000000001': 'GA', 'SMU15000000000000001': 'HI',
    'SMU16000000000000001': 'ID', 'SMU17000000000000001': 'IL',
    'SMU18000000000000001': 'IN', 'SMU19000000000000001': 'IA',
    'SMU20000000000000001': 'KS', 'SMU21000000000000001': 'KY',
    'SMU22000000000000001': 'LA', 'SMU23000000000000001': 'ME',
    'SMU24000000000000001': 'MD', 'SMU25000000000000001': 'MA',
    'SMU26000000000000001': 'MI', 'SMU27000000000000001': 'MN',
    'SMU28000000000000001': 'MS', 'SMU29000000000000001': 'MO',
    'SMU30000000000000001': 'MT', 'SMU31000000000000001': 'NE',
    'SMU32000000000000001': 'NV', 'SMU33000000000000001': 'NH',
    'SMU34000000000000001': 'NJ', 'SMU35000000000000001': 'NM',
    'SMU36000000000000001': 'NY', 'SMU37000000000000001': 'NC',
    'SMU38000000000000001': 'ND', 'SMU39000000000000001': 'OH',
    'SMU40000000000000001': 'OK', 'SMU41000000000000001': 'OR',
    'SMU42000000000000001': 'PA', 'SMU44000000000000001': 'RI',
    'SMU45000000000000001': 'SC', 'SMU46000000000000001': 'SD',
    'SMU47000000000000001': 'TN', 'SMU48000000000000001': 'TX',
    'SMU49000000000000001': 'UT', 'SMU50000000000000001': 'VT',
    'SMU51000000000000001': 'VA', 'SMU53000000000000001': 'WA',
    'SMU54000000000000001': 'WV', 'SMU55000000000000001': 'WI',
    'SMU56000000000000001': 'WY'
}



def fetch_state_data(series, api):
    
    # needs to be split up as API can only handle 50 requests at once
    half1 = list(series.keys())[:25]
    half2 = list(series.keys())[25:]

    halves = [half1, half2]
    
    combined_results = []

    for part in halves:
        
        response = requests.post(url, json={
            "seriesid": part,
            "startyear": str(current_year - 1), # only checking state data from present day and one year ago
            "endyear": str(current_year),
            "registrationkey": api
        })
        
        results = response.json().get('Results', {}).get('series', [])

        for s in results:
            s_id = s['seriesID']
            state_abbr = series[s_id]
            
            for i in s['data']:
                if i['period'] != 'M13':
                    combined_results.append({
                        "Date": pd.to_datetime(f"{i['year']}-{i['period'][1:]}-01"),
                        "State": state_abbr,
                        "Jobs": float(i['value']) * 1000 
                    })
        
    return pd.DataFrame(combined_results)

if __name__ == "__main__":
    df_states = fetch_state_data(state_series_dict, key)
    if not df_states.empty:
        df_states.to_csv('data/state_data.csv', index=False)
