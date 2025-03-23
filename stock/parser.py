import time
import requests
import pandas as pd

def get_moex_securities(market):
    """Функия получения данных от API Мсбиржи"""
    # Получаем данные по указанному рынку (расширенный формат)
    # Максимальное число получаемых записей в одном запросе - 100
    # Получаем данные построчно, пока не закончатся данные по рынку
    # Если результат пустой, возвращаем None

    # ��ормат URL для получения данных от API Мосбиржи:
    # https://iss.moex.com/iss/securities.json?engine=stock&market={market}
    # engine - указывает вид торговых операций
    url = f"https://iss.moex.com/iss/securities.json?engine=stock&market={market}"
    all_data = []
    start = 0

    while True:
        try:
            response = requests.get(f"{url}&start={start}", timeout=10)
            response.raise_for_status()  # Вызывает исключение при ошибке HTTP
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения: {e}")
            time.sleep(5)  # Пауза перед повтором
            continue

        columns = data.get('securities', {}).get('columns', [])
        rows = data.get('securities', {}).get('data', [])

        if not rows:
            break

        all_data.extend(rows)
        start += 100

    if not all_data:
        return None

    df = pd.DataFrame(all_data, columns=columns)
    return df

