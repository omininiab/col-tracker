import json
import requests
import os

DATA_FILE = "data/prices.json"

# ==========================================
# Statistics Canada & Bank of Canada Vector IDs
# ==========================================
GASOLINE_VECTOR_ID = 735097                 # Ottawa - Table 18-10-0001-01
MILK_VECTOR_ID = 1353834285                 # Canada 4L - Table 18-10-0245-01
BREAD_VECTOR_ID = 1353834326                # Canada 675g - Table 18-10-0245-01
ELECTRICITY_VECTOR_ID = 41691063            # Canada Electricity Index - Table 18-10-0004-01
CLOTHING_VECTOR_ID = 41691108               # Canada Clothing Index - Table 18-10-0004-01
RENT_VECTOR_ID = 41691052                   # Canada Rent Index - Table 18-10-0004-01
OWNED_ACCOMMODATION_VECTOR_ID = 41691055   # Canada Owned Accommodation Index - Table 18-10-0004-01
AVERAGE_WAGE_VECTOR_ID = 2132579           # Canada Average Hourly Wage - Table 14-10-0063-01
MEDIAN_WAGE_VECTOR_ID = 2132581            # Canada Median Hourly Wage - Table 14-10-0063-01

def fetch_historical_boc(start_date):
    url = f"https://www.bankofcanada.ca/valet/observations/V80691311/json?start_date={start_date}"
    response = requests.get(url)
    response.raise_for_status()
    observations = response.json().get('observations', [])
    return {obs['d']: float(obs['V80691311']['v']) for obs in observations}

def fetch_historical_statcan(vector_id, periods=24):
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
    payload = [{"vectorId": vector_id, "latestN": periods}]
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()[0]
    if data.get('status') != 'SUCCESS':
        print(f"⚠️ Error: StatCan API failed for Vector ID {vector_id}.")
        return {}
        
    data_points = data.get('object', {}).get('vectorDataPoint', [])
    return {pt['refPer']: float(pt['value']) for pt in data_points}

def main():
    print("Fetching historical data...")
    
    # 1. Fetch 24 months of StatCan Data
    gas_history = fetch_historical_statcan(GASOLINE_VECTOR_ID, periods=24)
    milk_history = fetch_historical_statcan(MILK_VECTOR_ID, periods=24)
    elec_history = fetch_historical_statcan(ELECTRICITY_VECTOR_ID, periods=24)
    cloth_history = fetch_historical_statcan(CLOTHING_VECTOR_ID, periods=24)
    bread_history = fetch_historical_statcan(BREAD_VECTOR_ID, periods=24)
    rent_history = fetch_historical_statcan(RENT_VECTOR_ID, periods=24)
    owned_history = fetch_historical_statcan(OWNED_ACCOMMODATION_VECTOR_ID, periods=24)
    avg_wage_history = fetch_historical_statcan(AVERAGE_WAGE_VECTOR_ID, periods=24)
    med_wage_history = fetch_historical_statcan(MEDIAN_WAGE_VECTOR_ID, periods=24)
    
    all_histories = [
        gas_history, milk_history, elec_history, cloth_history,
        bread_history, rent_history, owned_history, avg_wage_history, med_wage_history
    ]
    if not all(all_histories):
        print("❌ Backfill aborted. One or more Vector IDs failed.")
        return
    
    # 2. Fetch BoC data
    boc_history = fetch_historical_boc("2024-10-01") 
    
    # 3. Create a unique list of dates based on the primary index
    dates = sorted(list(set(list(gas_history.keys()) + list(milk_history.keys()))))
    
    history = {
        "dates": [], 
        "prime_rate": [], 
        "gasoline": [], 
        "milk": [],
        "bread_per_kg": [],
        "rent_index": [],
        "owned_accommodation_index": [],
        "average_hourly_wage": [],
        "median_hourly_wage": [],
        "electricity_index": [], 
        "clothing_index": []
    }
    
    for month_date in dates:
        matching_boc_rate = None
        year_month = month_date[:7]
        
        # Find closest BoC rate
        for day in range(1, 10): 
            test_date = f"{year_month}-{day:02d}"
            if test_date in boc_history:
                matching_boc_rate = boc_history[test_date]
                break
                
        if matching_boc_rate is None and boc_history:
            matching_boc_rate = list(boc_history.values())[0]
             
        history["dates"].append(year_month)
        
        # Apply the bread conversion
        raw_bread = bread_history.get(month_date, None)
        converted_bread = round(raw_bread / 0.675, 2) if raw_bread is not None else None

        history["prime_rate"].append(matching_boc_rate)
        history["gasoline"].append(gas_history.get(month_date, None))
        history["milk"].append(milk_history.get(month_date, None))
        history["bread_per_kg"].append(converted_bread)
        history["rent_index"].append(rent_history.get(month_date, None))
        history["owned_accommodation_index"].append(owned_history.get(month_date, None))
        history["average_hourly_wage"].append(avg_wage_history.get(month_date, None))
        history["median_hourly_wage"].append(med_wage_history.get(month_date, None))
        history["electricity_index"].append(elec_history.get(month_date, None))
        history["clothing_index"].append(cloth_history.get(month_date, None))

    # 4. Overwrite JSON
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=2)
        
    print(f"✅ Successfully backfilled {len(dates)} historical data points into {DATA_FILE}")

if __name__ == "__main__":
    main()
