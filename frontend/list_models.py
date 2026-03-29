import os
import requests
api_key = os.environ.get("GOOGLE_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
print([m['name'] for m in response.json().get('models', []) if 'flash' in m['name'] or 'pro' in m['name']])
