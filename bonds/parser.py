from datetime import datetime


def get_bonds():
    """Парсим бонды"""
    start_time = datetime.datetime.now()
    for p in range(1, 1000):
        bonds = moex.get_bonds(p, 100)