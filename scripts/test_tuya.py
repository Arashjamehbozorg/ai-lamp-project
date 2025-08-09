from tuya_connector import TuyaOpenAPI
from dotenv import load_dotenv # loads variables from .env file
import os # let us communicate with operating system for editing files, .. and raeding variables from .env file

load_dotenv() # looks for a file named .env in the current directory, which is scripts folders

# Function for checking if the variables in .env exist or not
def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value

API_ENDPOINT = get_env_var("API_ENDPOINT")
ACCESS_ID = get_env_var("ACCESS_ID")
ACCESS_KEY = get_env_var("ACCESS_KEY")
DEVICE_ID = get_env_var("DEVICE_ID")

openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

# Getting device status
response = openapi.get("/v1.0/devices/{}".format(DEVICE_ID))
print(response)
