import json
import requests
import os

DATA_FILE = "data/prices.json"

# ==========================================
# 🛑 ACTION REQUIRED: UPDATE THESE VECTOR IDs
# ==========================================
GASOLINE_VECTOR_ID = 735097      
MILK_VECTOR_ID = 1353834285          
BREAD_VECTOR_ID = 1353834326         
ELECTRICITY_VECTOR_ID = 41691063   
CLOTHING_VECTOR_ID = 41691108      #

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
    
    if not (gas_history and milk_history and elec_history and cloth_history and bread_history):
        print("❌ Backfill aborted. Please fix the Vector IDs.")
        return
    
    # 2. Fetch BoC data
    boc_history = fetch_historical_boc("2024-10-01") 
    
    # 3. Create a unique list of dates based on the primary index
    dates = sorted(list(set(list(gas_history.keys()) + list(milk_history.keys()))))
    
    history = {
        "dates": [], "prime_rate": [], "gasoline": [], "milk": [],
        "electricity_index": [], "clothing_index": [], "bread_per_kg": []
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

        history["gasoline"].append(gas_history.get(month_date, None))
        history["milk"].append(milk_history.get(month_date, None))
        history["electricity_index"].append(elec_history.get(month_date, None))
        history["clothing_index"].append(cloth_history.get(month_date, None))
        history["bread_per_kg"].append(converted_bread)
        history["prime_rate"].append(matching_boc_rate)

    # 4. Overwrite JSON
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=2)
        
    print(f"✅ Successfully backfilled {len(dates)} historical data points into {DATA_FILE}")

if __name__ == "__main__":
    main()