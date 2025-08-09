from config import ACCESS_ID, ACCESS_KEY, API_ENDPOINT, DEVICE_ID
from tuya_connector import TuyaOpenAPI

openai = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openai.connect()

response = openai.get(f"/v1.0/devices/{DEVICE_ID}")

result_obj = response.get("result", [])
if result_obj:
    status_pir = result_obj["status"][0]["value"]
    print("Motion Detected!" if status_pir == "pir" else "No Motion")
else:
    raise ValueError("No Datas Available!")