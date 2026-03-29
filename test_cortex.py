import os
import logging
from snowflake.snowpark.session import Session
logging.basicConfig(level=logging.DEBUG)

account = os.getenv("SNOWFLAKE_ACCOUNT", "").replace(".snowflakecomputing.com", "")
token = os.getenv("SNOWFLAKE_TOKEN", "")

try:
    print(f"Trying to connect with oauth... account={account}")
    session_oauth = Session.builder.configs({
        "account": account,
        "authenticator": "oauth",
        "token": token
    }).create()
    print("OAUTH CONNECTED")
except Exception as e:
    print(f"OAUTH Failed: {e}")
