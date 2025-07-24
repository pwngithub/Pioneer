import requests
import pandas as pd

def fetch_jotform_data(form_id: str, api_key: str) -> pd.DataFrame:
    url = f"https://api.jotform.com/form/{form_id}/submissions?apiKey={api_key}&limit=1000"
    response = requests.get(url)
    data = response.json()

    records = []
    for submission in data["content"]:
        answers = submission.get("answers", {})
        record = {}
        for qid, answer in answers.items():
            name = answer.get("name")
            value = answer.get("answer")
            if isinstance(value, dict):
                value = " ".join(str(v) for v in value.values() if v)
            record[name] = value
        records.append(record)

    return pd.DataFrame(records)

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    # Basic standardization, fill missing values
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].fillna("").astype(str).str.strip()
    return df
