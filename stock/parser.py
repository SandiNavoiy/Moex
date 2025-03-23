import time
import requests
import pandas as pd


# Настройки pandas для отображения всех столбцов
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

def get_moex_securities(market):
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

