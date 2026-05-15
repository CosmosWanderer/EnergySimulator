import streamlit as st
import pandas as pd
import re
import json
import os

st.title("Редактор тестов")

if "consumers" not in st.session_state:
    st.session_state.consumers = []
if "generators" not in st.session_state:
    st.session_state.generators = []

st.subheader("Потребители")

if st.button("Добавить потребителя"):
    st.session_state.consumers.append({"name": "Потребитель", "demand": [0.0] * 24})

for i, consumer in enumerate(st.session_state.consumers):
    st.write(f"**{consumer['name']}**")
    consumer["name"] = st.text_input("Имя", value=consumer["name"], key=f"cname_{i}")
    
    df = pd.DataFrame([consumer["demand"]], columns=[str(h) for h in range(24)])
    edited = st.data_editor(df, hide_index=True, key=f"cdata_{i}",
        column_config={str(h): st.column_config.NumberColumn(str(h), width="small") for h in range(24)})
    consumer["demand"] = edited.iloc[0].tolist()

    col1, col2 = st.columns(2)
    if col1.button("Дублировать", key=f"cdup_{i}"):
        st.session_state.consumers.append(consumer.copy())
        st.rerun()
    if col2.button("Удалить", key=f"cdel_{i}"):
        st.session_state.consumers.pop(i)
        st.rerun()
    
    st.divider()

st.subheader("Генераторы")

col1, col2 = st.columns(2)
if col1.button("Добавить с постоянной генерацией"):
    st.session_state.generators.append({
        "name": "Генератор",
        "gen_type": "constant",
        "output": 0.0,
        "cost": 0.0
    })
if col2.button("Добавить с переменной генерацией"):
    st.session_state.generators.append({
        "name": "Генератор",
        "gen_type": "variable",
        "output": [0.0] * 24,
        "cost": 0.0
    })

for i, generator in enumerate(st.session_state.generators): 
    st.write(f"**{generator['name']}**")
    generator["name"] = st.text_input("Имя", value=generator["name"], key=f"gname_{i}")
    generator["cost"] = st.number_input("Стоимость за кВтч", value=generator["cost"], key=f"gcost_{i}")

    if generator["gen_type"] == "variable":
        df = pd.DataFrame([generator["output"]], columns=[str(h) for h in range(24)])
        edited = st.data_editor(df, hide_index=True, key=f"gdata_{i}",
            column_config={str(h): st.column_config.NumberColumn(str(h), width="small") for h in range(24)})
        generator["output"] = edited.iloc[0].tolist()
    else:
        generator["output"] = st.number_input("Мощность (кВтч)", value=generator["output"], key=f"goutput_{i}")

    col1, col2 = st.columns(2)
    if col1.button("Дублировать", key=f"gdup_{i}"): 
        st.session_state.generators.append(generator.copy())
        st.rerun()
    if col2.button("Удалить", key=f"gdel_{i}"): 
        st.session_state.generators.pop(i)
        st.rerun()

    st.divider()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(BASE_DIR, "tests")
st.subheader("Сохранить")
filename = st.text_input("Имя файла", value="my_test.json")
if not filename.endswith(".json"):
    st.error("Имя файла должно заканчиваться на .json")
    st.stop()
if "/" in filename or "\\" in filename:
    st.error("Имя файла не должно содержать путь")
    st.stop()

if st.button("Сохранить"):
    if not st.session_state.consumers:
        st.error("Добавьте хотя бы одного потребителя")
    elif not st.session_state.generators:
        st.error("Добавьте хотя бы один генератор")
    else:
        os.makedirs(TESTS_DIR, exist_ok=True)
        data = {"consumers": st.session_state.consumers, "generators": st.session_state.generators}
        filepath = os.path.join(TESTS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            output = json.dumps(data, ensure_ascii=False, indent=2)
            output = re.sub(
                r'\[\n\s+(-?\d+\.?\d*(?:,\n\s+-?\d+\.?\d*)*)\n\s+\]',
                lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']',
                output
            )
            f.write(output)
        st.success(f"Сохранено в {filepath}")