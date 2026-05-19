import requests

API_KEY = "d605e6ea-f930-4c4e-916b-9aaedb9b9d41"

ASSISTANT_ID = "d3bb2a68-ebbf-4429-bd7f-e518d3bfaed3"

PHONE_NUMBER = "+919845084018"

url = "https://api.vapi.ai/call"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "assistantId": ASSISTANT_ID,
    "phoneNumberId": "2c7c5dc2-a4c7-46ce-bcc4-b04b1ad1ec9f",
    "customer": {
        "number": PHONE_NUMBER
    }
}
response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.text)