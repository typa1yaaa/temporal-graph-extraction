import os
import re
import json
import torch
import networkx as nx
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from transformers import AutoTokenizer, T5ForConditionalGeneration, AutoModelForSeq2SeqLM


st.set_page_config(page_title="Генератор Графа Событий", layout="wide")


@st.cache_resource
def load_models():
    SUM_MODEL = "IlyaGusev/rut5_base_sum_gazeta"
    sum_tokenizer = AutoTokenizer.from_pretrained(SUM_MODEL)
    sum_model = T5ForConditionalGeneration.from_pretrained(SUM_MODEL)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EVENT_MODEL_PATH = os.path.join(BASE_DIR, "model_rut5")

    event_tokenizer = AutoTokenizer.from_pretrained(EVENT_MODEL_PATH, local_files_only=True)
    event_model = AutoModelForSeq2SeqLM.from_pretrained(EVENT_MODEL_PATH, local_files_only=True)

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    sum_model.to(DEVICE)
    event_model.to(DEVICE)
    
    return sum_tokenizer, sum_model, event_tokenizer, event_model, DEVICE

sum_tokenizer, sum_model, event_tokenizer, event_model, DEVICE = load_models()


def parse_output(text):
    vertices = {}
    edges = []

    if not text:
        return vertices, edges

    text = re.sub(r"\s+", " ", text).strip()

    v_match = re.search(r"VERTEX_LIST:\s*(.*?)(?:RELATIONSHIPS_LIST:|$)", text)
    r_match = re.search(r"RELATIONSHIPS_LIST:\s*(.*)$", text)

    vblock = v_match.group(1).strip() if v_match else ""
    rblock = r_match.group(1).strip() if r_match else ""

    for m in re.finditer(r"(V\d+)\s*:\s*(.+?)(?=\s+V\d+\s*:|$)", vblock):
        vid, vtext = m.group(1), m.group(2).strip()
        vertices[vid] = vtext

    for m in re.finditer(r"(V\d+)\s*->\s*(V\d+)\s+(\w+)", rblock):
        edges.append((m.group(1), m.group(2), m.group(3)))

    return vertices, edges

def pipeline(text):
    inputs = sum_tokenizer([text], max_length=600, truncation=True, return_tensors="pt").to(DEVICE)
    out_ids = sum_model.generate(**inputs, no_repeat_ngram_size=4, num_beams=5, max_length=256)
    summary = sum_tokenizer.decode(out_ids[0], skip_special_tokens=True)

    ev_inputs = event_tokenizer(summary, return_tensors="pt", truncation=True, max_length=256).to(DEVICE)
    with torch.no_grad():
        ev_out = event_model.generate(**ev_inputs, max_length=256)
    raw = event_tokenizer.decode(ev_out[0], skip_special_tokens=True)
    
    vertices, edges = parse_output(raw)
    
    nodes_data = [
        {
            "id": vid, 
            "text": vtext, 
            "date": "Не указана"
        } 
        for vid, vtext in vertices.items()
    ]
    
    return {
        "summary": summary,
        "nodes": nodes_data,
        "edges": [{"source": src, "target": tgt, "type": rel} for src, tgt, rel in edges],
    }

def build_graph_html(graph_json):
    G = nx.DiGraph()
    for n in graph_json["nodes"]:
        hover_text = f"Событие: {n['text']}\nДата: {n['date']}"
        G.add_node(n["id"], label=n["id"], title=hover_text)
        
    for e in graph_json["edges"]:
        G.add_edge(e["source"], e["target"], label=e["type"], title=e["type"])

    net = Network(height="600px", width="100%", directed=True, bgcolor="#1E1E1E", font_color="white")
    net.from_nx(G)

    html_path = "temp_graph.html"
    net.write_html(html_path)
    return html_path


st.title("Генерация графа событий из текста 🕸️")

text_input = st.text_area("Введите текст для анализа:", height=150, 
    value="Проект закрыли из-за нехватки бюджета. Команду перевели в другой отдел, потому что требовались узкопрофильные специалисты.")

if st.button("Сгенерировать граф событий", type="primary"):
    with st.spinner("Анализируем текст и строим граф..."):
        result = pipeline(text_input)
        st.session_state['result'] = result
        st.session_state['graph_html'] = build_graph_html(result)

if 'result' in st.session_state:
    res = st.session_state['result']
    
    with st.expander("📝 Посмотреть сгенерированное саммари", expanded=False):
        st.write(res["summary"])

    col1, col2 = st.columns([5, 3])

    with col1:
        st.subheader("Интерактивный граф")
        st.caption("💡 Наведите курсор на вершину (V1, V2), чтобы прочитать событие и дату.")
        HtmlFile = open(st.session_state['graph_html'], 'r', encoding='utf-8')
        components.html(HtmlFile.read(), height=650)

    with col2:
        st.subheader("Список событий")
        search_query = st.text_input("🔍 Поиск по тексту события:", placeholder="Например: проект")
        st.write("---")
        

        events_container = st.container(height=530)
        
        with events_container:
            found_any = False
            for node in res["nodes"]:
                if search_query.lower() in node["text"].lower():
                    found_any = True
                    st.markdown(f"### 📍 Узел `{node['id']}`")
                    st.markdown(f"**Событие:** {node['text']}")
                    st.caption(f"🗓 **Дата:** {node['date']}")
                    st.divider()
            
            if not found_any:
                st.warning("Событий по вашему запросу не найдено.")