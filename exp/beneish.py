"""
beneish_report.py

Программа для расчёта Beneish M-Score (модель оценки вероятности манипуляции отчётностью).

Что делает скрипт:
1. Принимает таблицу с финансовыми данными компании за несколько лет (DataFrame).
2. Считает восемь индексов модели Бениша (DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA).
3. По этим индексам вычисляет итоговый показатель M-score.
4. Даёт текстовый отчёт с пояснениями по каждому индексу и интерпретацией M-score.

Ограничения:
- Для первого года в таблице индексы не рассчитываются (нет предыдущего периода для сравнения).
- Данные должны быть согласованы (одинаковая методика расчёта показателей).
"""

import pandas as pd
import numpy as np

# ---- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----

def safe_div(a, b):
    """Деление с защитой: если знаменатель = 0 или NaN → вернём NaN, а не ошибку."""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        res = np.where((b == 0) | np.isnan(b), np.nan, a / b)
    return res

# ---- ОСНОВНАЯ ФУНКЦИЯ ----

def compute_beneish(df):
    """
    Принимает DataFrame с годами (индекс) и столбцами:
    'revenue','receivables','cogs','current_assets','total_assets',
    'depreciation','ppe','sg_and_a','total_liabilities','net_income','cash_from_ops'

    Возвращает DataFrame с рассчитанными индексами и M-score.
    """

    # Проверка обязательных колонок
    required = ['revenue','receivables','cogs','current_assets','total_assets',
                'depreciation','ppe','sg_and_a','total_liabilities','net_income','cash_from_ops']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"В таблице не хватает колонок: {', '.join(missing)}")

    # Берём текущий год (t) и предыдущий год (t-1)
    t = df
    t_1 = df.shift(1)

    # Индексы Beneish
    DSRI = safe_div(safe_div(t['receivables'], t['revenue']),
                    safe_div(t_1['receivables'], t_1['revenue']))

    gm  = safe_div(t['revenue'] - t['cogs'], t['revenue'])
    gm_1 = safe_div(t_1['revenue'] - t_1['cogs'], t_1['revenue'])
    GMI = safe_div(gm_1, gm)

    AQI = safe_div(1 - safe_div(t['current_assets'], t['total_assets']),
                   1 - safe_div(t_1['current_assets'], t_1['total_assets']))

    SGI = safe_div(t['revenue'], t_1['revenue'])

    dep_ratio_t = safe_div(t['depreciation'], t['depreciation'] + t['ppe'])
    dep_ratio_1 = safe_div(t_1['depreciation'], t_1['depreciation'] + t_1['ppe'])
    DEPI = safe_div(dep_ratio_1, dep_ratio_t)

    SGAI = safe_div(safe_div(t['sg_and_a'], t['revenue']),
                    safe_div(t_1['sg_and_a'], t_1['revenue']))

    LVGI = safe_div(safe_div(t['total_liabilities'], t['total_assets']),
                    safe_div(t_1['total_liabilities'], t_1['total_assets']))

    TATA = safe_div((t['net_income'] - t['cash_from_ops']), t['total_assets'])

    # Итоговый Beneish M-score
    M = (-4.84
         + 0.92 * DSRI
         + 0.528 * GMI
         + 0.404 * AQI
         + 0.892 * SGI
         + 0.115 * DEPI
         - 0.172 * SGAI
         + 4.679 * TATA
         - 0.327 * LVGI)

    result = pd.DataFrame({
        'DSRI': DSRI,
        'GMI': GMI,
        'AQI': AQI,
        'SGI': SGI,
        'DEPI': DEPI,
        'SGAI': SGAI,
        'LVGI': LVGI,
        'TATA': TATA,
        'M_SCORE': M
    }, index=df.index)

    result['flag_manipulation'] = result['M_SCORE'] > -2.22

    return result

# ---- ФУНКЦИЯ ДЛЯ ТЕКСТОВОГО ОТЧЁТА ----

def beneish_report(row, year):
    """
    Формирует текстовый отчёт по одному году (строке DataFrame).
    row — строка DataFrame с индексами.
    year — год (индекс).
    """

    lines = [f"Год {year} — Beneish M-score анализ:"]
    if pd.isna(row['M_SCORE']):
        lines.append("  Недостаточно данных для расчёта (нет предыдущего года).")
        return "\n".join(lines)

    # Интерпретация каждого индекса
    lines.append(f"  DSRI = {row['DSRI']:.3f} → рост дебиторки к продажам. "
                 "Если >1, дебиторка растёт быстрее продаж (риск завышенной выручки).")

    lines.append(f"  GMI = {row['GMI']:.3f} → индекс валовой маржи. "
                 "Если >1, маржа снижается (признак проблем).")

    lines.append(f"  AQI = {row['AQI']:.3f} → качество активов. "
                 "Рост (>1) может означать больше нематериальных или проблемных активов.")

    lines.append(f"  SGI = {row['SGI']:.3f} → рост выручки. "
                 "Высокий рост часто связан с риском приукрашивания отчётности.")

    lines.append(f"  DEPI = {row['DEPI']:.3f} → индекс амортизации. "
                 "Если >1, возможно замедление списания (может скрывать падение прибыли).")

    lines.append(f"  SGAI = {row['SGAI']:.3f} → рост расходов SG&A. "
                 "Если >1, расходы растут быстрее выручки (тревожный сигнал).")

    lines.append(f"  LVGI = {row['LVGI']:.3f} → долговая нагрузка. "
                 "Если >1, доля обязательств растёт (рискованнее структура капитала).")

    lines.append(f"  TATA = {row['TATA']:.3f} → начисления/активы. "
                 "Чем выше, тем больше разница между прибылью и кэшем (подозрительно).")

    # Итог
    lines.append(f"  M_SCORE = {row['M_SCORE']:.3f}")
    if row['flag_manipulation']:
        lines.append("  ❗ M > -2.22 → модель сигналит: вероятность манипуляций повышена.")
    else:
        lines.append("  ✅ M ≤ -2.22 → признаков манипуляций не выявлено.")

    return "\n".join(lines)
"""
beneish.py
Вычисление Beneish M-Score (модель обнаружения манипуляций с отчётностью).

Ожидаемые столбцы (в DataFrame с индексом по году, где каждый год — строка):
  'revenue'            - Выручка (Sales, Net Sales)
  'receivables'        - Дебиторская задолженность (Accounts receivable)
  'cogs'               - Себестоимость (Cost of Goods Sold) или 'gross_profit' можно использовать для gross margin
  'current_assets'     - Оборотные активы
  'total_assets'       - Всего активов
  'depreciation'       - Накопленная или годовая амортизация (в зависимости от доступных данных; см. замечания)
  'ppe'                - Основные средства (Net PP&E или аналог)
  'sg_and_a'           - Коммерческие и управленческие расходы (SG&A)
  'total_liabilities'  - Обязательства (Total liabilities)
  'net_income'         - Чистая прибыль
  'cash_from_ops'      - Денежный поток от операционной деятельности (operating cash flow)

Обязательные поля (имена колонок в коде)

Код ожидает ровно эти названия. Можно адаптировать, но проще переименовать поля в файле.

revenue
— Выручка (Net Sales) за год.
— Источник: отчёт о прибылях и убытках (строка «Выручка», «Net sales»).
— Примеры: 1200000, 1.2e6.
— Если есть только «Gross profit», то cogs = revenue - gross_profit (см. ниже).

receivables
— Дебиторская задолженность (Accounts receivable), net (после резерва под сомнительные долги) — значение на конец года.
— Источник: баланс, «Дебиторская задолженность», «Trade receivables» или «Accounts receivable (net)».
— Важно: используй именно торговую дебиторку, а не дебиторку по прочим операциям, если есть выбор.

cogs
— Себестоимость продаж (Cost of Goods Sold) за год.
— Источник: ОПУ.
— Если COGS нет, но есть gross_profit, то cogs = revenue - gross_profit.

current_assets
— Оборотные активы на конец года (Current assets).
— Источник: баланс. Включает денежные средства, дебиторку, запасы и т.д.

total_assets
— Всего активов (Total assets) на конец года.
— Источник: баланс.

depreciation
— Накопленная амортизация (accumulated depreciation) на конец года (балансовая строка).
— Почему — см. ниже (DEPI).
— Если доступна только амортизация за год (depreciation expense), можно использовать, но это изменит смысл DEPI — и лучше отмечать это в отчёте.

ppe
— Net PP&E (основные средства после накопленной амортизации) — значение на конец года.
— Важно: если depreciation = накопленная амортизация, то depreciation + ppe ≈ gross PPE (брутто). Формула DEPI в коде строится именно на этом.

sg_and_a
— Расходы на selling, general & administrative (SG&A) за год (или суммарно коммерческие+управленческие).
— Источник: ОПУ. Если подвели отдельно «Selling» и «Administrative» — сложи их.

total_liabilities
— Сумма обязательств (Total liabilities) на конец года (текущие + долгосрочные).
— Источник: баланс. Можно посчитать как total_assets - equity, если явной строки нет.

net_income
— Чистая прибыль за год (Net income, profit after tax).
— Источник: ОПУ. Желательно использовать прибыль, относимую к владельцам компании (если есть группа/дочерние).

cash_from_ops
— Денежный поток от операционной деятельности (Operating cash flow) за год.
— Источник: отчёт о движении денежных средств (Cash flow statement). Нужна строка «Cash flows from operating activities».

Почему именно эти строки (коротко про смысл)

DSRI, GMI, AQI, SGI и др. — формулы смешивают балансовые (конец периода) и потоковые (за год) данные. Неправильный тип (напр., взять средние вместо концов) исказит индексы.

Для DEPI корректнее брать накопленную амортизацию и net PPE: тогда depreciation / (depreciation + ppe) = накопленная амортизация / брутто PPE. Это именно то, что ожидал Beneish.

Частые ситуации и как их решать

Нет depreciation (накопленной), есть только depreciation expense
— Лучше взять накопленную амортизацию (balance sheet). Если её нет, можно попытаться пересчитать:
accum_dep_t ≈ accum_dep_{t-1} + depreciation_expense_t - disposals_accum — но для этого нужны дополнительные строки (выбытия/пересчёты).
— Если нельзя — можно использовать ежегодную амортизацию как приближение, но обозначь это в отчёте: DEPI будет интерпретироваться иначе.

Нет cogs, есть только gross_profit
— cogs = revenue - gross_profit.

Нет sg_and_a как суммарной строки
— Сложи все статьи, относящиеся к продаже и управлению (selling + admin + marketing и т.п.).

receivables — брутто vs нетто
— Берём net (после резерва). Если есть только брутто — лучше взять брутто, но пометь это.

Единицы / разделители в CSV
— Убирай пробелы и нечисловые символы. Например: 1 200 000 → 1200000. Десятичные разделители — точка ..

Отсутствие предыдущего года
— Для первого года по каждой паре индексов получится NaN — нормально.

Интерпретация: чем выше M, тем выше вероятность манипуляций. Часто используется порог:
  M > -2.22  => подозрение на манипуляции (классический порог из статьи Beneish).
"""
# ---- ПРИМЕР ИСПОЛЬЗОВАНИЯ ----
if __name__ == "__main__":
    # Пример данных за 2 года
    data = {
        'revenue':           [1000.0, 1200.0],
        'receivables':       [80.0, 150.0],
        'cogs':              [600.0, 800.0],
        'current_assets':    [300.0, 350.0],
        'total_assets':      [1000.0, 1100.0],
        'depreciation':      [100.0, 90.0],
        'ppe':               [400.0, 420.0],
        'sg_and_a':          [120.0, 130.0],
        'total_liabilities': [600.0, 650.0],
        'net_income':        [80.0, 90.0],
        'cash_from_ops':     [60.0, 20.0],
    }
    years = [2023, 2024]
    df = pd.DataFrame(data, index=years)

    results = compute_beneish(df)
    print(results, "\n")

    # Печать текстового отчёта
    for year, row in results.iterrows():
        print(beneish_report(row, year))
        print("-" * 70)
