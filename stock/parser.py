import pandas as pd
import requests
from matplotlib import pyplot as plt

def plot_stock():
    """Вывод графика функции"""
    # Запрос
    j = requests.get('http://iss.moex.com/iss/engines/stock/markets/shares/securities/YNDX/candles.json?from=2023-05-25&till=2023-09-01&interval=24').json()
    # Загоняем в пандас
    data = [{k : r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
    frame = pd.DataFrame(data)
    # Построение графика
    plt.plot(list(frame['close']))
    #Сохранение акции
    plt.savefig("shares.png")
    plt.title("Стоимость акции")
    plt.xlabel("Дни")
    plt.ylabel("Стоимость")
    plt.show()