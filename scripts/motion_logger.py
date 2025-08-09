""" import csv
from datetime import datetime
from config import ACCESS_ID, ACCESS_KEY, API_ENDPOINT, DEVICE_ID
from tuya_connector import TuyaOpenAPI

openai = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openai.connect()
# ["status"][0]["value"] Motion Detected!" if status_pir == "pir" else "No Motion"
response = openai.get(f"/v1.0/devices/{DEVICE_ID}")

result_obj = response.get("result", [])
time_stamp_converted = datetime.fromtimestamp(result_obj["update_time"])
if result_obj:
    status_pir = result_obj["status"][0]["value"]
    
    print(status_pir)
    print(time_stamp_converted)
else:
    raise ValueError("No Datas Available!")



with open("../logs/lamp_data.csv", "w") as data:
    csv_writer = csv.writer(data)
    csv_writer.writerow(["timestamp","motion_status"]) """

import csv
import time
from datetime import datetime
from pathlib import Path
from config import ACCESS_ID, ACCESS_KEY, API_ENDPOINT, DEVICE_ID
from tuya_connector import TuyaOpenAPI

# --- Setup ---
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

# CSV path (change if you prefer)
csv_path = Path("../logs/lamp_data.csv")
csv_path.parent.mkdir(parents=True, exist_ok=True)  # ensure ../logs exists

# Create header once (only if file is new)
if not csv_path.exists():
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["local_timestamp", "tuya_update_time", "motion_status"])

print("Change-only motion logger running. Press Ctrl+C to stop.")

# Keep track of last seen values to avoid duplicate rows
last_status = None
last_update_ts = None  # Tuya's update_time (unix seconds)

try:
    while True:
        # 1) Query Tuya
        resp = openapi.get(f"/v1.0/devices/{DEVICE_ID}")
        result = resp.get("result", {})
        status_list = result.get("status", [])
        update_ts = result.get("update_time")  # unix seconds (int)

        # 2) Extract PIR status safely
        status_pir = None
        for item in status_list:
            if item.get("code") == "pir":
                status_pir = item.get("value")  # "pir" or "none"
                break

        if status_pir is None or update_ts is None:
            # Nothing meaningful returned; wait and retry
            time.sleep(2)
            continue

        # 3) Only log if something changed (status or Tuya's update_time)
        changed = (status_pir != last_status) or (update_ts != last_update_ts)
        if changed:
            local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tuya_time = datetime.fromtimestamp(update_ts).strftime("%Y-%m-%d %H:%M:%S")

            # Console feedback
            pretty = "Motion Detected" if status_pir == "pir" else "No Motion"
            print(f"[{local_time}] {pretty} | Tuya: {tuya_time}")

            # Write one new row
            with csv_path.open("a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([local_time, tuya_time, status_pir])

            # Update last seen
            last_status = status_pir
            last_update_ts = update_ts

        # 4) Poll interval
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped.")
