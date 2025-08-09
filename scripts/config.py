from dotenv import load_dotenv #for loading the env file
import os # for communicating with operation system

load_dotenv() # finds and loads the .env file in the current directory which is scripts

# getting and checking if the variable in .env exists or not (string or None)
def get_env_var(name:str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"there is no variable named:{name} in the .env file!")
    return value

API_ENDPOINT = get_env_var("API_ENDPOINT")
ACCESS_ID = get_env_var("ACCESS_ID")
ACCESS_KEY = get_env_var("ACCESS_KEY")
DEVICE_ID = get_env_var("DEVICE_ID")
