
import requests
import pandas as pd

def fetch_jotform_data(form_id: str, api_key: str) -> pd.DataFrame:
    url = f"https://api.jotform.com/form/{form_id}/submissions?apiKey={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from JotForm API. Status Code: {response.status_code}")

    submissions = response.json().get("content", [])
    records = []

    for sub in submissions:
        answer_data = sub.get("answers", {})
        row = {}

        for ans in answer_data.values():
            name = ans.get("name")
            value = ans.get("answer")

            if isinstance(value, dict) and "prettyFormat" in value:
                row[name] = value["prettyFormat"]
            elif isinstance(value, dict) and "datetime" in value:
                row[name] = value["datetime"]
            else:
                row[name] = value

        row["submission_id"] = sub.get("id")
        row["submission_date"] = sub.get("created_at")
        records.append(row)

    df = pd.DataFrame(records)
    return df
