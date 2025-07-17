import requests
import pandas as pd

API_KEY = "ba9013143bfda3a448297144c0527f7e"
BASE_URL = "https://api.jotform.com"

def get_forms():
    url = f"{BASE_URL}/user/forms?apiKey={API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    forms = resp.json().get("content", [])
    return [(f["id"], f["title"]) for f in forms]

def get_submissions(form_id):
    url = f"{BASE_URL}/form/{form_id}/submissions?apiKey={API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    submissions = resp.json().get("content", [])

    data = []
    for sub in submissions:
        fields = sub.get("answers", {})
        record = {f["name"]: f.get("answer", "") for f in fields.values()}
        record["Submission ID"] = sub["id"]
        record["Created At"] = pd.to_datetime(sub["created_at"])
        data.append(record)

    df = pd.DataFrame(data)
    if 'Technician' not in df.columns:
        df['Technician'] = 'Unknown'
    if 'Work Type' not in df.columns:
        df['Work Type'] = 'Unknown'
    if 'Duration' not in df.columns:
        df['Duration'] = 0

    df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce').fillna(0)
    return df