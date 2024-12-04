import requests
import schedule
import time
from datetime import datetime, timedelta
import json
import signal
import sys

# API settings
url = "https://stage.uchet24.kz/api/v1/greenkassa/get-checks-bin/"
bin_value = "821023402309"

# Starting time dates
start_time = datetime.strptime("2024-08-06T07:00:00", "%Y-%m-%dT%H:%M:%S")
end_time_limit = datetime.strptime("2024-08-06T23:59:59", "%Y-%m-%dT%H:%M:%S")

# Result list
results = []

def send_request():
    global start_time

    # End of current interval
    end_time = start_time + timedelta(hours=6) - timedelta(seconds=1)
    if end_time > end_time_limit:
        end_time = end_time_limit

    # Creating data for POST-request
    data = {
        "start_date": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_date": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "bin": bin_value
    }

    try:
        # Sending request
        response = requests.post(url, json=data)
        print(f"Request sent: {data}")
        print(f"Server's response: {response.status_code} - {response.text}")

        # Saving request and answer
        results.append({
            "request": data,
            "response": {
                "status_code": response.status_code,
                "body": response.text
            }
        })

    except Exception as e:
        print(f"Error in sending request: {e}")

    start_time = end_time + timedelta(seconds=1)

    if start_time > end_time_limit:
        print("End has been reached. Saving data and ending processes.")
        save_results_to_file()
        schedule.clear()

def save_results_to_file():
    with open("results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)
    print("Data was saved in 'results.json'")

# In case someone would want to stop it manually
def stop_script(signal_received, frame):
    print("\nScript was stopped by user. Saving data...")
    save_results_to_file()
    sys.exit(0)

signal.signal(signal.SIGINT, stop_script)

schedule.every(10).minutes.do(send_request)
send_request()

while True:
    schedule.run_pending()
    time.sleep(1)
