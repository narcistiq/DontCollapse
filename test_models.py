import os
import google.genai
import datetime
client = google.genai.Client()
models_to_test = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
for m in models_to_test:
    try:
        resp = client.models.generate_content(model=m, contents="hi")
        print(f"{m}: OK")
    except Exception as e:
        print(f"{m}: ERR {str(e)[:100]}")
