from tuya_connector import TuyaOpenAPI

ACCESS_ID = "p73wjpk7xv4k938qeyht"
ACCESS_KEY = "36a41b4ca24f40909557884006953ccc"
API_ENDPOINT = "https://openapi.tuyaeu.com"  
DEVICE_ID = "bfaf0fd8be6effd2d3uhgx"

openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

# Getting device status
response = openapi.get("/v1.0/devices/{}".format(DEVICE_ID))
print(response)
