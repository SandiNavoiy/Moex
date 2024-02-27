import datetime

import pandas as pd
import requests
from matplotlib import pyplot as plt

def plot_stock(name):
    """Вывод графика функции"""
    date1 = datetime.date(2023, 11, 27)
    date2 = datetime.date(2023, 12, 30)

    # Запрос
    respose = requests.get(f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{name}/candles.json?from={date1}&till={date2}&interval=24')
    #interval – Размер свечки - целое число 1 (1 минута), 10 (10 минут),
    # 60 (1 час), 24 (1 день), 7 (1 неделя), 31 (1 месяц) или 4 (1 квартал). По умолчанию дневные данные
    if respose.status_code == 200:
        # Преобразование JSON в словарь
        j = respose.json()

    # Загоняем в пандас
    data = [{k : r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
    frame = pd.DataFrame(data)
    # Построение графика
    plt.plot(list(frame['close']))
    #Сохранение акции
    plt.savefig("shares.png")
    plt.title(f"Стоимость акции {name}, рублей")
    plt.xlabel(f"C {date1} до {date2}")
    plt.ylabel("Стоимость")
    plt.grid(color='pink')
    plt.show()

def coast_stock(name):
    """Вывод цены конкретной акции на сегодня"""
    # Текущая дата
    dt_now = datetime.date.today()
    respose = requests.get(
        f'https://iss.moex.com/iss/securities/{name}/aggregates.json?date=2022-09-21')
    if respose.status_code == 200:
        # Преобразование JSON в словарь
        j = respose.json()
    print(j)