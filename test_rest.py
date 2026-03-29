import requests
import json
import os

account = os.getenv("SNOWFLAKE_ACCOUNT", "").replace(".snowflakecomputing.com", "")
token = os.getenv("SNOWFLAKE_TOKEN", "")
url = f"https://{account}.snowflakecomputing.com/api/v2/statements"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
payload = {
    "statement": "SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', 'Hello, how are you?')"
}

print(f"Calling {url} ...")
res = requests.post(url, headers=headers, json=payload)
print(res.status_code)
print(res.text)
