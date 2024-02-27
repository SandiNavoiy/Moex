from stock.parser import plot_stock, coast_stock

if __name__ == '__main__':
    name_stock = {1: "YNDX", 2: "ROSN"}
    plot_stock(name_stock[2])

    coast_stock(name_stock[2])