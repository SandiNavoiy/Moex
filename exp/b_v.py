import streamlit as st
import pandas as pd

#  Запуск - streamlit run D:\python\Moex\exp\b_v.py
st.title("Beneish M-Score Калькулятор")

st.write("""
Здесь можно рассчитать вероятность манипуляций в отчётности по модели Бениша.  
Введи данные за два года (текущий год — **t**, предыдущий — **t-1**).
""")

# Список показателей и подсказок
inputs = {
    "revenue": "Выручка",
    "receivables": "Дебиторская задолженность",
    "cogs": "Себестоимость",
    "current_assets": "Оборотные активы",
    "total_assets": "Итого активы",
    "depreciation": "Амортизация",
    "ppe": "Основные средства (PPE)",
    "sg_and_a": "Коммерческие и управленческие расходы (SG&A)",
    "total_liabilities": "Обязательства",
    "net_income": "Чистая прибыль",
    "cash_from_ops": "Денежный поток от операций (CFO)"
}

data = {}
for key, label in inputs.items():
    data[f"{key}_t"] = st.number_input(f"{label} (год t)", value=0.0)
    data[f"{key}_t_1"] = st.number_input(f"{label} (год t-1)", value=0.0)

def calculate_beneish(data):
    try:
        DSRI = (data["receivables_t"] / data["revenue_t"]) / (data["receivables_t_1"] / data["revenue_t_1"])
        GMI = ((data["revenue_t_1"] - data["cogs_t_1"]) / data["revenue_t_1"]) / \
              ((data["revenue_t"] - data["cogs_t"]) / data["revenue_t"])
        AQI = (1 - (data["current_assets_t"] + data["ppe_t"]) / data["total_assets_t"]) / \
              (1 - (data["current_assets_t_1"] + data["ppe_t_1"]) / data["total_assets_t_1"])
        SGI = data["revenue_t"] / data["revenue_t_1"]
        DEPI = (data["depreciation_t_1"] / (data["depreciation_t_1"] + data["ppe_t_1"])) / \
               (data["depreciation_t"] / (data["depreciation_t"] + data["ppe_t"]))
        SGAI = (data["sg_and_a_t"] / data["revenue_t"]) / (data["sg_and_a_t_1"] / data["revenue_t_1"])
        LVGI = (data["total_liabilities_t"] / data["total_assets_t"]) / \
               (data["total_liabilities_t_1"] / data["total_assets_t_1"])
        TATA = (data["net_income_t"] - data["cash_from_ops_t"]) / data["total_assets_t"]

        m_score = (-4.84 + 0.92*DSRI + 0.528*GMI + 0.404*AQI +
                   0.892*SGI + 0.115*DEPI - 0.172*SGAI +
                   4.679*TATA - 0.327*LVGI)

        return {
            "DSRI": (DSRI, "Рост дебиторки к продажам. >1 — компания может гнать выручку в кредит."),
            "GMI": (GMI, "Изменение валовой маржи. >1 — маржа падает, риск манипуляций."),
            "AQI": (AQI, "Качество активов. >1 — растёт доля нематериальных и сомнительных активов."),
            "SGI": (SGI, "Рост продаж. >1 — быстрый рост может толкать к приукрашиванию."),
            "DEPI": (DEPI, "Амортизация. >1 — сниженные списания могут приукрашивать прибыль."),
            "SGAI": (SGAI, "Доля SG&A в выручке. >1 — расходы растут быстрее продаж."),
            "LVGI": (LVGI, "Финансовый рычаг. >1 — увеличивается долговая нагрузка."),
            "TATA": (TATA, "Начисления к активам. >0.1 — тревожный сигнал."),
            "M-score": (m_score, "Главный показатель. > -2.22 = высокая вероятность манипуляций.")
        }
    except ZeroDivisionError:
        return None

if st.button("Рассчитать"):
    result = calculate_beneish(data)
    if result:
        st.subheader("Результаты с пояснениями")
        for k, (val, desc) in result.items():
            st.write(f"**{k}:** {val:.4f} — {desc}")
        st.markdown("---")
        if result["M-score"][0] > -2.22:
            st.error("⚠️ Итог: высокая вероятность манипуляций в отчётности.")
        else:
            st.success("✅ Итог: вероятность манипуляций низкая.")
    else:
        st.warning("Проверь данные — где-то деление на ноль.")
