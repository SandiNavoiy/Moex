
import time
import requests
import pandas as pd


# Настройки pandas для отображения всех столбцов
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

def get_moex_bonds(market):
    """Функия получения данных от API Мсбиржи"""
    # Получаем данные по указанному рынку (расширенный формат)
    # Максимальное число получаемых записей в одном запросе - 100
    # Получаем данные построчно, пока не закончатся данные по рынку
    # Если результат пустой, возвращаем None

    # Формат URL для получения данных от API Мосбиржи:
    # https://iss.moex.com/iss/securities.json?engine=stock&market={market}
    # engine - указывает вид торговых операций
    url = f"https://iss.moex.com/iss/securities.json?engine=stock&market={market}"
    all_data = []
    start = 0

    while True:
        try:
            response = requests.get(f"{url}&start={start}", timeout=30)
            # timeout=30 выбран опытным путем
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения:  - выключи vpn {e}")
            time.sleep(5)  # Пауза перед повтором
            continue

        columns = data.get('securities').get('columns')
        rows = data.get('securities').get('data')
        # выход из цикла
        if not rows:
            break
        # добавляем полученные данные в общий список
        all_data.extend(rows)
        start += 100

    if not all_data:
        return None

    df = pd.DataFrame(all_data, columns=columns)
    return df

def get_moex_bonds_urovni_stavok():
    """Функия уровня ставок от кредитного рейтинга"""
    for i in get_all_bond_tickers():
        print(get_bond_details(i))


def get_bond_details(s):
    """вывод конкретной инфоррмации по конкретной бумаге"""
    url = f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQCB/securities/{s}.json"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Ошибка при получении данных для {s}")
        return None

    data = response.json()

    columns = data['securities']['columns']
    rows = data['securities']['data']

    if not rows:
        print(f"Нет данных для {s}")
        return None

    df = pd.DataFrame(rows, columns=columns)

    return df




def get_all_bond_tickers():
    """Собирает все тикеры облигаций с MOEX (всех досок)"""
    base_url = "https://iss.moex.com/iss/securities.json"
    params = {
        "engine": "stock",
        "market": "bonds",
        "iss.meta": "on",  # включаем метаданные
    }

    all_tickers = []
    start = 0

    while True:
        try:
            response = requests.get(base_url, params={**params, "start": start}, timeout=30)
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения: {e}")
            time.sleep(5)
            continue

        securities = data.get("securities", {})
        columns = securities.get("columns", [])
        rows = securities.get("data", [])

        if not rows:
            break

        # определяем индекс secid динамически
        try:
            secid_index = columns.index("secid")
        except ValueError:
            print(f"secid не найден в колонках: {columns}")
            break

        tickers = [row[secid_index] for row in rows if row[secid_index]]
        all_tickers.extend(tickers)
        start += 100

    return sorted(set(all_tickers))


