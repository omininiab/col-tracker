import json
import requests
from datetime import datetime
import os

DATA_FILE = "data/prices.json"

# ==========================================
# 🛑 ACTION REQUIRED: UPDATE THESE VECTOR IDs
# ==========================================
GASOLINE_VECTOR_ID = 735097      # Ottawa - Use the absolute price ID from Table 18-10-0001-01
MILK_VECTOR_ID = 1353834285          # Use the absolute price ID from Table 18-10-0245-01
BREAD_VECTOR_ID = 1353834326         # Use the ID for "White bread, 675g" from Table 18-10-0245-01
ELECTRICITY_VECTOR_ID = 41691063   # Use the Electricity Index ID from Table 18-10-0004-01

# The Clothing and Footwear Index ID has been pre-filled for you
CLOTHING_VECTOR_ID = 41691108      #

def fetch_boc_prime_rate():
    url = "https://www.bankofcanada.ca/valet/observations/V80691311/json?recent=1"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return float(data['observations'][0]['V80691311']['v'])

def fetch_statcan_vector(vector_id):
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
    payload = [{"vectorId": vector_id, "latestN": 1}]
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()[0]
    if data.get('status') != 'SUCCESS':
        raise ValueError(f"StatCan API failed for Vector ID {vector_id}")
        
    return float(data['object']['vectorDataPoint'][0]['value'])

def main():
    os.makedirs("data", exist_ok=True)
    
    # Load existing history or initialize with the expanded metrics
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {
            "dates": [], 
            "prime_rate": [], 
            "gasoline": [], 
            "milk": [],
            "electricity_index": [],
            "clothing_index": [],
            "bread_per_kg": []
        }
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if len(history["dates"]) == 0 or history["dates"][-1] != today:
        try:
            # Fetch all data
            prime = fetch_boc_prime_rate()
            gas = fetch_statcan_vector(GASOLINE_VECTOR_ID)
            milk = fetch_statcan_vector(MILK_VECTOR_ID)
            electricity = fetch_statcan_vector(ELECTRICITY_VECTOR_ID)
            clothing = fetch_statcan_vector(CLOTHING_VECTOR_ID)
            
            # Fetch bread (675g) and convert to 1kg equivalent
            bread_675g = fetch_statcan_vector(BREAD_VECTOR_ID)
            bread_per_kg = round(bread_675g / 0.675, 2)

            # Append to time series
            history["dates"].append(today)
            history["prime_rate"].append(prime)
            history["gasoline"].append(gas)
            history["milk"].append(milk)
            history["electricity_index"].append(electricity)
            history["clothing_index"].append(clothing)
            history["bread_per_kg"].append(bread_per_kg)
            
            with open(DATA_FILE, "w") as f:
                json.dump(history, f, indent=2)
                
            print(f"Successfully logged data for {today}")
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            exit(1)
    else:
        print(f"Data for {today} already exists. Skipping.")

if __name__ == "__main__":
    main()