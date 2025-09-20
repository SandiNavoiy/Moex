from pprint import pprint
import pandas as pd
import requests


def get_bond_details(s):
    """вывод конкретной инфоррмации по конкретной бумаге"""
    url = f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQCB/securities/{s}.json"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Ошибка при получении данных для {s}")
        return None

    data = response.json()

    # columns = data['securities']['columns']
    # rows = data['securities']['data']
    #
    # if not rows:
    #     print(f"Нет данных для {s}")
    #     return None
    #
    # df = pd.DataFrame(rows, columns=columns)
    # pprint(data)

    return data['marketdata_yields']['data'][0][6], data['securities']['data'][0][12]


# Пример: получение данных по облигации с SECID = 'RU000A0JX0A4'
bond_secid = "RU000A10B313"
bond_data = get_bond_details(bond_secid)

if bond_data is not None:

    pprint(bond_data)