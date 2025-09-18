import requests

city = input("Enter city name: ")
url = f"http://127.0.0.1:5000/weather?city={city}"

response = requests.get(url)  # Send GET request to API

if response.status_code == 200:
    data = response.json()
    print(f"Weather in {city}: {data['data']['temperature']}, {data['data']['condition']}")
else:
    print(response.json()["message"])
