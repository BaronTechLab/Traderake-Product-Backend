import requests

url = "http://127.0.0.1:8000/api/accounts/users/reset_password/"
data = {"email": "sanalsabu@gmail.com"}

print(f"Sending POST request to {url} with data {data}")
response = requests.post(url, json=data)

print(f"Status Code: {response.status_code}")
if response.status_code == 204:
    print("Password reset request successful! Check the celery worker logs and the destination email.")
else:
    print(f"Error: {response.text}")
