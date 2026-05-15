import streamlit as st
import pandas as pd
import os

from simulator import Simulator

st.title("Energy Grid Simulator")

if not os.path.exists("tests"):
    st.error("Папка tests не найдена")
    st.stop()

with st.sidebar:
    st.header("Настройки")
    
    test_files = [f"tests/{f}" for f in os.listdir("tests") if f.endswith(".json")]
    testfile = st.selectbox("Выберите тест", test_files)
    method = st.radio("Алгоритм", ["brute", "dp"])
    
    run = st.button("Запустить симуляцию")

if run:
    sim = Simulator()
    st.session_state.data = sim.simulate(testfile, method)
    st.session_state.last_testfile = testfile

if "data" in st.session_state:
    data = st.session_state.data

    total_cost = sum(h.optimal_cost for h in data)
    deficit_hours = sum(1 for h in data if len(h.consumers_not_served) > 0)

    st.metric("Общая стоимость", total_cost)
    st.metric("Часов с дефицитом", deficit_hours)

    df = pd.DataFrame({
        "Час": range(24),
        "Спрос": [h.full_demand for h in data],
        "Генерация": [h.max_output for h in data],
        "Стоимость": [h.optimal_cost for h in data],
        "Обслужено": [len(h.consumers_served) for h in data],
        "Отключено": [len(h.consumers_not_served) for h in data],
    })

    st.subheader("Спрос vs Генерация")
    st.line_chart(df.set_index("Час")[["Спрос", "Генерация"]])

    st.subheader("Стоимость по часам")
    st.bar_chart(df.set_index("Час")["Стоимость"])

    st.subheader("Детали по часу")
    hour = st.slider("Выбери час", 0, 23, 0)

    hour_data = data[hour]

    col1, col2, col3 = st.columns(3)
    col1.metric("Спрос", f"{hour_data.full_demand:.1f} кВтч")
    col2.metric("Генерация", f"{hour_data.max_output:.1f} кВтч")
    col3.metric("Стоимость", f"{hour_data.optimal_cost:.1f}")

    st.write("**Генераторы:**")
    for g in hour_data.used_gens:
        st.write(f"{g.name}: генерация {g.output[hour]:.1f} кВтч, стоимость {g.output[hour] * g.cost:.1f}")

    st.write("**Обслужены:**")
    for c in hour_data.consumers_served:
        st.write(f"{c.name}: {c.demand[hour]:.1f} кВтч")

    if hour_data.consumers_not_served:
        st.error("Отключённые потребители:")
        for c in hour_data.consumers_not_served:
            st.write(f"{c.name}: {c.demand[hour]:.1f} кВтч")
    elif not hour_data.anybody_served:
        st.info("В этот час нет потребителей")
    else:
        st.success("Все потребители обслужены в этот час")  
else:
    st.info("Выберите тест и нажмите 'Запустить симуляцию'")