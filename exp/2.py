import pandas as pd
import requests
j = requests.get('https://iss.moex.com/iss/securities/YNDX/aggregates.json?date=2022-09-21').json()
data = [{k : r[i] for i, k in enumerate(j['aggregates']['columns'])} for r in j['aggregates']['data']]
print(pd.DataFrame(data))