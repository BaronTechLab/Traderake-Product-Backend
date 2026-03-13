import requests

url = "http://127.0.0.1:8000/api/accounts/request-otp/"
data = {
    "country_code": "+91",
    "phone_number": "8861718806"
}

print(f"Sending POST request to {url} with data {data}")
response = requests.post(url, json=data)

print(f"Status Code: {response.status_code}")
try:
    print(f"Response: {response.json()}")
except ValueError:
    print(f"Response text: {response.text}")
