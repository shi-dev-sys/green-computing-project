import requests

url = "http://127.0.0.1:5000/energy"

data = {
    "cpu_usage": 40,
    "hours": 2
}

response = requests.post(url, json=data)

print("Server Response:")
print(response.json())