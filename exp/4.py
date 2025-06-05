import requests
import time
from collections import defaultdict

def get_bonds_from_tqcb():
    """Получает список облигаций с доски TQCB на Мосбирже"""
    url = "https://iss.moex.com/iss/securities.json"
    params = {
        "engine": "stock",
        "market": "bonds",
        "iss.meta": "on",
        "filter": "boardid=TQCB"
    }

    all_bonds = []
    start = 0

    while True:
        try:
            response = requests.get(url, params={**params, "start": start}, timeout=30)
            data = response.json()
        except Exception as e:
            print("Ошибка подключения:", e)
            time.sleep(5)
            continue

        securities = data.get("securities", {})
        rows = securities.get("data", [])
        columns = securities.get("columns", [])
        if not rows:
            break

        try:
            secid_idx = columns.index("secid")
            shortname_idx = columns.index("shortname")
        except ValueError as e:
            print("Не найдены нужные поля:", columns)
            break

        all_bonds.extend([
            {"secid": row[secid_idx], "shortname": row[shortname_idx]}
            for row in rows if row[secid_idx]
        ])

        start += 100

    return all_bonds


def get_yield_and_rating(secid, max_retries=3):
    ytm = None
    rating = None

    for attempt in range(max_retries):
        try:
            url_yield = f"https://iss.moex.com/iss/engines/stock/markets/bonds/securities/{secid}/marketdata.json"
            r_yield = requests.get(url_yield, timeout=10)
            r_yield.raise_for_status()
            md = r_yield.json().get("marketdata", {})
            if md.get("data"):
                ytm_idx = md["columns"].index("YIELD")
                ytm_val = md["data"][0][ytm_idx]
                if isinstance(ytm_val, (float, int)):
                    ytm = ytm_val

            url_desc = f"https://iss.moex.com/iss/securities/{secid}/description.json"
            r_desc = requests.get(url_desc, timeout=10)
            r_desc.raise_for_status()
            for row in r_desc.json().get("description", {}).get("data", []):
                if row[0].lower() in {"creditrating", "credit_rating"}:
                    rating = row[1]
                    break

            break  # если всё прошло успешно - выходим из цикла
        except Exception as e:
            print(f"{secid}: попытка {attempt+1} ошибка — {e}")
            time.sleep(3)
    else:
        print(f"{secid}: не удалось получить данные после {max_retries} попыток")

    return ytm, rating or "Без рейтинга"



def analyze_bonds():
    bonds = get_bonds_from_tqcb()
    print(f"Найдено облигаций на TQCB: {len(bonds)}")

    rating_map = defaultdict(list)

    for i, bond in enumerate(bonds):
        secid = bond["secid"]
        print(f"{i+1}/{len(bonds)}: {secid}")
        ytm, rating = get_yield_and_rating(secid)
        if ytm is not None:
            rating_map[rating].append(ytm)

    print("\n📊 Средние доходности по кредитному рейтингу:\n")
    for rating in sorted(rating_map):
        yields = rating_map[rating]
        avg_yield = sum(yields) / len(yields)
        print(f"{rating:<20}: {avg_yield:.2f}%  (на {len(yields)} облигациях)")


# Запуск анализа
if __name__ == "__main__":
    analyze_bonds()
