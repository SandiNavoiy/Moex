# Модель оценки компании по фундаментальному анализу

from dataclasses import dataclass
import matplotlib.pyplot as plt

@dataclass
class CompanyData:
    name: str
    projected_net_profit: float  # прогноз чистой прибыли, млрд руб
    historical_pe: float         # среднеисторический P/E
    shares_outstanding: float    # количество акций, млрд шт

    revenue: float               # прогноз выручки
    operating_expenses: float    # прогноз операционных расходов
    net_debt: float              # чистый долг
    interest_rate: float         # ставка обслуживания долга
    total_assets: float = None   # активы для расчета Debt/Assets
    total_equity: float = None   # собственный капитал
    ebitda: float = None         # EBITDA для расчета Net Debt/EBITDA
    free_cash_flow: float = None # свободный денежный поток (FCF)
    market_cap: float = None     # рыночная капитализация, млрд руб
    tax_rate: float = 0.25       # налоговая ставка (по умолчанию 25%)

    def forecast_profit(self):
        financial_expenses = self.net_debt * self.interest_rate
        ebt = self.revenue - self.operating_expenses - financial_expenses
        net_profit = ebt * (1 - self.tax_rate)
        return net_profit

    def fair_price(self):
        net_profit = self.forecast_profit()
        return round((net_profit * self.historical_pe) / self.shares_outstanding, 2)

    def calc_multiples(self):
        multiples = {}
        if self.market_cap and self.projected_net_profit:
            multiples['P/E'] = round(self.market_cap / self.projected_net_profit, 2)
        if self.market_cap and self.total_equity:
            multiples['P/BV'] = round(self.market_cap / self.total_equity, 2)
        if self.market_cap and self.free_cash_flow:
            multiples['P/FCF'] = round(self.market_cap / self.free_cash_flow, 2)
        if self.net_debt and self.ebitda:
            multiples['Net Debt/EBITDA'] = round(self.net_debt / self.ebitda, 2)
        if self.total_equity:
            multiples['Debt/Equity'] = round(self.net_debt / self.total_equity, 2)
        if self.total_assets:
            multiples['Debt/Assets'] = round(self.net_debt / self.total_assets, 2)
        return multiples

    def plot_multiples(self):
        multiples = self.calc_multiples()
        labels = list(multiples.keys())
        values = list(multiples.values())

        plt.figure(figsize=(10, 6))
        bars = plt.bar(labels, values, color='skyblue')
        plt.title(f"Мультипликаторы для {self.name}")
        plt.ylabel("Значение")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{yval:.2f}", ha='center', va='bottom')
        plt.tight_layout()
        plt.show()


# Пример: компания Полюс
data_polyus = CompanyData(
    name="Полюс",
    projected_net_profit=269.1,     # для справки
    historical_pe=5,
    shares_outstanding=0.1349,
    revenue=603.2,
    operating_expenses=223.3,
    net_debt=622.7,
    interest_rate=0.07,
    total_assets=1200,
    total_equity=550,
    ebitda=370,
    free_cash_flow=250,
    market_cap=1600
)

print(f"Справедливая цена акций {data_polyus.name}: {data_polyus.fair_price()} руб")
print(f"Мультипликаторы {data_polyus.name}: {data_polyus.calc_multiples()}")

data_polyus.plot_multiples()
