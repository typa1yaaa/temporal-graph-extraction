import os

import requests
import streamlit as st
import streamlit.components.v1 as components

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Temporal Graph Extraction", layout="wide")
st.title("Генерация графа событий из текста 🕸️")
st.caption("Вставьте текст — модель выделит события, участников, даты и связи между ними")

text_input = st.text_area("Введите текст для анализа:", height=150)
use_summary = st.checkbox("📄 Сначала сжать текст (суммаризация)", value=True)

if st.button("Сгенерировать граф событий", type="primary", disabled=not text_input.strip()):
    with st.spinner("Обработка текста..."):
        try:
            resp = requests.post(
                f"{API_URL}/extract",
                json={"text": text_input, "use_summary": use_summary},
                timeout=60,
            )
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка запроса к API: {e}")
            st.stop()

    st.session_state["result"] = result

    if result["nodes"]:
        try:
            html_resp = requests.post(
                f"{API_URL}/graph/html",
                json={"nodes": result["nodes"], "edges": result["edges"]},
                timeout=30,
            )
            html_resp.raise_for_status()
            st.session_state["graph_html"] = html_resp.text
        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка построения графа: {e}")
            st.session_state["graph_html"] = None
    else:
        st.session_state["graph_html"] = None

if "result" in st.session_state:
    res = st.session_state["result"]

    with st.expander("📝 Просмотр текста (саммари / исходный)", expanded=False):
        if res["summary"]:
            st.write(res["summary"])
        else:
            st.write("Суммаризация не применялась. Модель работала по исходному тексту.")

    if not res["nodes"]:
        st.warning("Событий в тексте не обнаружено.")
    else:
        col1, col2 = st.columns([5, 3])

        with col1:
            st.subheader("Интерактивный граф")
            st.caption("💡 Наведите курсор на вершину, чтобы увидеть полное событие. Цвет рёбер указывает на тип связи.")
            if st.session_state.get("graph_html"):
                components.html(st.session_state["graph_html"], height=800, width=1000)

        with col2:
            st.subheader("Список событий")
            search_query = st.text_input("🔍 Поиск по тексту события:", placeholder="Например: проект")
            st.divider()

            events_container = st.container(height=530)
            with events_container:
                found_any = False
                for node in res["nodes"]:
                    if search_query.lower() in node["text"].lower():
                        found_any = True
                        st.markdown(f"### 📍 Узел `{node['id']}`")
                        st.markdown(f"**Событие:** {node['text']}")
                        st.caption(f"**Участник:** {node['person']}")
                        st.caption(f"**Дата:** {node['date']}")
                        st.divider()

                if not found_any:
                    st.warning("Событий по вашему запросу не найдено.")
