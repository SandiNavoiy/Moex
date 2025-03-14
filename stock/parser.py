from pprint import pprint

import requests

url = "https://iss.moex.com/iss/index.json?iss.only=markets"
response = requests.get(url)  # запрос данных по url


pprint(response.json())