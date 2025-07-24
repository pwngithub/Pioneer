import requests
import pandas as pd

def fetch_jotform_data(form_id):
    API_KEY = "ba9013143bfda3a448297144c0527f7e"  # Replace if needed
    url = f"https://api.jotform.com/form/{form_id}/submissions?apiKey={API_KEY}"

    response = requests.get(url)
    submissions = response.json().get("content", [])

    records = []
    for s in submissions:
        answers = s.get("answers", {})
        record = {}
        for answer in answers.values():
            q_name = answer.get("name")
            q_answer = answer.get("answer")
            if isinstance(q_answer, dict) and 'prettyFormat' in q_answer:
                record[q_name] = q_answer['prettyFormat']
            else:
                record[q_name] = q_answer
        records.append(record)

    return pd.DataFrame(records)