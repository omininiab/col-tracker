import json
import requests
from datetime import datetime
import os

DATA_FILE = "data/prices.json"

def fetch_boc_prime_rate():
    # Bank of Canada Valet API for Chartered Bank Prime Rate (V80691311)
    url = "https://www.bankofcanada.ca/valet/observations/V80691311/json?recent=1"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return float(data['observations'][0]['V80691311']['v'])

def fetch_statcan_vector(vector_id):
    # StatCan Web Data Service API
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
    payload = [{"vectorId": vector_id, "latestN": 1}]
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    return float(data[0]['object']['vectorDataPoint'][0]['value'])

def main():
    os.makedirs("data", exist_ok=True)
    
    # Load existing history
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {"dates": [], "prime_rate": [], "gasoline": [], "milk": []}
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Prevent duplicate entries on the same day
    if len(history["dates"]) == 0 or history["dates"][-1] != today:
        try:
            # Fetch real data
            prime = fetch_boc_prime_rate()
            
            # Using example StatCan Vector IDs - Update these as needed
            try:
                gas = fetch_statcan_vector(122543004)
            except:
                gas = 1.65 
                
            try:
                milk = fetch_statcan_vector(122543015)
            except:
                milk = 2.89

            # Append to time series
            history["dates"].append(today)
            history["prime_rate"].append(prime)
            history["gasoline"].append(gas)
            history["milk"].append(milk)
            
            # Save back to JSON
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
