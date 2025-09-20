from bonds.parser import get_moex_bonds, get_moex_bonds_urovni_stavok, get_all_bond_tickers
from stock.parser import get_moex_securities

print("Выберете тип ценных бумаг")
print("пока досупны акции - 1  или облигации - 2")
r = input()
if r == "1":
    stocks = get_moex_securities("shares")
    if stocks is not None:
        print("Акции:")
        print(stocks)
elif r == "2":
    bonds = get_moex_bonds_urovni_stavok()
    if bonds is not None:
        print("Облигации:")
        print(bonds)


elif r == "3":

