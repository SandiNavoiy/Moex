from pprint import pprint

import requests
import pandas as pd


def get_bond_details(secid):
    url = f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQCB/securities/{secid}.json"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Ошибка при получении данных для {secid}")
        return None

    data = response.json()
    pprint(data)
    columns = data['securities']['columns']
    rows = data['securities']['data']

    if not rows:
        print(f"Нет данных для {secid}")
        return None

    df = pd.DataFrame(rows, columns=columns)
    return df


# Пример: получение данных по облигации с SECID = 'RU000A0JX0A4'
bond_secid = "SU26248RMFS3"
bond_data = get_bond_details(bond_secid)

if bond_data is not None:
    print(bond_data)
