import requests

OPENAI_API_KEY = "YOUR_API_KEYsk-proj-1baJafxnVXL-pmW2U9VEkoDMx2BO3Ski_IrrwpAYEt6qycEUeWZMguT4GlU6-suvqOEZYUO8KxT3BlbkFJdtlB7XFJ2yKYr-cZzoBpahX2grY0FumPsaH60_chCcrzLXwiyu2MnU-gTua4r59_KIqfOMuHcA"

def extract_corrections(transcript):
    url = "https://api.openai.com/v1/responses"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are an academic assistant.

    Extract corrections from this postgraduate presentation transcript.

    Categorize them into:
    - Critical
    - Major
    - Minor

    Transcript:
    {transcript}
    """

    data = {
        "model": "gpt-4.1-mini",
        "input": prompt
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()