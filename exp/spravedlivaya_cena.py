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
        warnings = {}

        if self.market_cap and self.projected_net_profit:
            pe = self.market_cap / self.projected_net_profit
            multiples['P/E'] = round(pe, 2)
            if pe > 20 or pe < 2:
                warnings['P/E'] = "Опасно"
            elif 2 <= pe <= 5 or 15 <= pe <= 20:
                warnings['P/E'] = "Погранично"
            else:
                warnings['P/E'] = "OK"

        if self.market_cap and self.total_equity:
            pbv = self.market_cap / self.total_equity
            multiples['P/BV'] = round(pbv, 2)
            if pbv < 0.3 or pbv > 3:
                warnings['P/BV'] = "Опасно"
            elif 0.3 <= pbv <= 0.5 or 2 <= pbv <= 3:
                warnings['P/BV'] = "Погранично"
            else:
                warnings['P/BV'] = "OK"

        if self.market_cap and self.free_cash_flow:
            pfcf = self.market_cap / self.free_cash_flow
            multiples['P/FCF'] = round(pfcf, 2)
            if pfcf > 20:
                warnings['P/FCF'] = "Опасно"
            elif 15 <= pfcf <= 20:
                warnings['P/FCF'] = "Погранично"
            else:
                warnings['P/FCF'] = "OK"

        if self.net_debt and self.ebitda:
            nde = self.net_debt / self.ebitda
            multiples['Net Debt/EBITDA'] = round(nde, 2)
            if nde > 3:
                warnings['Net Debt/EBITDA'] = "Опасно"
            elif 2 <= nde <= 3:
                warnings['Net Debt/EBITDA'] = "Погранично"
            else:
                warnings['Net Debt/EBITDA'] = "OK"

        if self.total_equity:
            de = self.net_debt / self.total_equity
            multiples['Debt/Equity'] = round(de, 2)
            if de > 3:
                warnings['Debt/Equity'] = "Опасно"
            elif 2 <= de <= 3:
                warnings['Debt/Equity'] = "Погранично"
            else:
                warnings['Debt/Equity'] = "OK"

        if self.total_assets:
            da = self.net_debt / self.total_assets
            multiples['Debt/Assets'] = round(da, 2)
            if da > 0.9:
                warnings['Debt/Assets'] = "Опасно"
            elif 0.7 <= da <= 0.9:
                warnings['Debt/Assets'] = "Погранично"
            else:
                warnings['Debt/Assets'] = "OK"

        return multiples, warnings

    def interpret_warnings(self, warnings):
        conclusions = []
        risk_score = 0

        if warnings.get('Net Debt/EBITDA') == "Опасно" or warnings.get('Debt/Equity') == "Опасно":
            conclusions.append("⚠ Финансовая устойчивость под угрозой: высокая долговая нагрузка")
            risk_score += 2
        if warnings.get('P/E') == "Опасно" and warnings.get('P/BV') == "Опасно":
            conclusions.append("📉 Возможен пузырь или сильная переоценка компании")
            risk_score += 2
        if warnings.get('P/E') == "Опасно" and warnings.get('P/BV') == "OK":
            conclusions.append("❓ Прибыль нестабильна, возможны искажения оценки")
            risk_score += 1
        if warnings.get('P/FCF') == "Опасно":
            conclusions.append("💸 Компания плохо генерирует денежный поток")
            risk_score += 1
        if warnings.get('Debt/Assets') == "Опасно":
            conclusions.append("🔥 Компания на грани дефолта по обязательствам")
            risk_score += 3

        if not conclusions:
            conclusions.append("✅ Существенных рисков по мультипликаторам не выявлено")

        # Определение итогового рейтинга риска
        if risk_score == 0:
            risk_level = "Низкий риск"
        elif 1 <= risk_score <= 3:
            risk_level = "Средний риск"
        else:
            risk_level = "Высокий риск"

        conclusions.append(f"🏁 Итоговый рейтинг риска: {risk_level}")

        return conclusions

    def plot_multiples(self):
        multiples, warnings = self.calc_multiples()
        labels = list(multiples.keys())
        values = list(multiples.values())

        plt.figure(figsize=(10, 6))

        colors = []
        for label in labels:
            if warnings.get(label) == "Опасно":
                colors.append('red')
            elif warnings.get(label) == "Погранично":
                colors.append('yellow')
            else:
                colors.append('green')

        bars = plt.bar(labels, values, color=colors)
        plt.title(f"Мультипликаторы для {self.name}")
        plt.ylabel("Значение")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        for bar, label in zip(bars, labels):
            yval = bar.get_height()
            warn = warnings.get(label, "")
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{yval:.2f} ({warn})", ha='center', va='bottom')
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
multiples, warnings = data_polyus.calc_multiples()
print(f"Мультипликаторы {data_polyus.name}: {multiples}")
print(f"Предупреждения: {warnings}")

conclusions = data_polyus.interpret_warnings(warnings)
print("Выводы:")
for c in conclusions:
    print(c)

data_polyus.plot_multiples()
