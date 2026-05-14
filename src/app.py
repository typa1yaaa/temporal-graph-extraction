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

    parts = re.split(r"(?i)relationship[_\s]*list[:\s]*", text)
    vblock = parts[0] if parts else ""
    rblock = parts[1] if len(parts) > 1 else ""

    vertex_parts = re.split(r"(?i)(v\d+)\s*:", vblock)
    for i in range(1, len(vertex_parts), 2):
        raw_id = vertex_parts[i]
        vid = f"V{re.sub(r'[^0-9]', '', raw_id)}"
        content = vertex_parts[i+1].strip() if i+1 < len(vertex_parts) else ""
        
        if not content or "relationship" in content.lower():
            continue
            
        if "|" in content:
            chunks = [c.strip() for c in content.split("|")]
            raw_date = chunks[0] if len(chunks) > 0 else "-"
            person = chunks[1] if len(chunks) > 1 else "Не указан"
            event_text = chunks[2] if len(chunks) > 2 else " ".join(chunks[1:])
        else:
            raw_date = "-"
            person = "Не указан"
            event_text = content

        date = "Не указана"
        if raw_date != "-":
            match = re.search(r'\b(\d{4})\b', raw_date)
            if match:
                date = match.group(1)
            else:
                date = raw_date

        vertices[vid] = {
            "id": vid,
            "date": date,
            "person": person if person != "-" else "Не указан",
            "text": event_text
        }

    for m in re.finditer(r"(v\d+)\s*->\s*(v\d+)\s+(\w+)", rblock, re.IGNORECASE):
        edges.append((
            m.group(1).upper(),
            m.group(2).upper(),
            m.group(3).lower()  
        ))

    return vertices, edges

def pipeline(text, use_summary=True):
    if use_summary:
        inputs = sum_tokenizer([text], max_length=600, truncation=True, return_tensors="pt").to(DEVICE)
        out_ids = sum_model.generate(**inputs, no_repeat_ngram_size=4, num_beams=5, max_length=256)
        processed_text = sum_tokenizer.decode(out_ids[0], skip_special_tokens=True)
    else:
        processed_text = text
        max_len = 1024 
        if len(processed_text) > max_len:
            processed_text = processed_text[:max_len]

    ev_inputs = event_tokenizer(processed_text, return_tensors="pt", truncation=True, max_length=256).to(DEVICE)
    with torch.no_grad():
        ev_out = event_model.generate(**ev_inputs, max_length=256)
    raw = event_tokenizer.decode(ev_out[0], skip_special_tokens=True)
    
    vertices, edges = parse_output(raw)
    nodes_data = list(vertices.values())
    
    return {
        "summary": processed_text if use_summary else None,  
        "nodes": nodes_data,
        "edges": [{"source": src, "target": tgt, "type": rel} for src, tgt, rel in edges],
    }

def build_graph_html(graph_json):
    G = nx.DiGraph()

    for n in graph_json["nodes"]:
        label = n["id"]                       
        hover_text = (
            f"Событие: {n['text']}\n"
            f"Участник: {n['person']}\n"
            f"Дата: {n['date']}"
        )
        G.add_node(
            n["id"],
            label=label,
            title=hover_text
        )

    edge_colors = {
        "temporal": "blue",
        "causal": "red",
        "causes": "orange",
        "leads to": "green"
    }
    for e in graph_json["edges"]:
        color = edge_colors.get(e["type"], "gray")
        G.add_edge(
            e["source"],
            e["target"],
            label=e["type"],
            title=e["type"],
            color=color
        )

    net = Network(height="900px", width="100%", directed=True, bgcolor="#1E1E1E", font_color="white")
    net.from_nx(G)

    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": true
      },
      "edges": {
        "arrows": { "to": true },
        "font": { "size": 12 }
      },
      "nodes": {
        "font": { "size": 20, "face": "arial" },
        "shape": "circle",
        "size": 30
      },
      "interaction": {
        "zoomView": true,
        "dragView": true
      }
    }
    """)

    html_path = "temp_graph.html"
    net.write_html(html_path)
    return html_path

st.title("Генерация графа событий из текста 🕸️")

text_input = st.text_area("Введите текст для анализа:", height=150, value="...")

use_summary = st.checkbox("📄 Сначала сжать текст (суммаризация)", value=True)

if st.button("Сгенерировать граф событий", type="primary"):
    with st.spinner("Обработка текста..."):
        result = pipeline(text_input, use_summary=use_summary)
        st.session_state['result'] = result
        st.session_state['graph_html'] = build_graph_html(result)

if 'result' in st.session_state:
    res = st.session_state['result']
    with st.expander("📝 Просмотр текста (саммари / исходный)", expanded=False):
        if res["summary"] is not None:
            st.write(res["summary"])
        else:
            st.write("Суммаризация не применялась. Модель работала по исходному тексту:\n\n" + text_input[:1000])

    col1, col2 = st.columns([5, 3])

    with col1:
        st.subheader("Интерактивный граф")
        st.caption("💡 Наведите курсор на вершину, чтобы увидеть полное событие. Цвет рёбер указывает на тип связи.")
        HtmlFile = open(st.session_state['graph_html'], 'r', encoding='utf-8')
        components.html(HtmlFile.read(), height=800, width=1000)  

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
                    st.caption(f"**Участник:** {node['person']}")
                    st.caption(f"**Дата:** {node['date']}")
                    st.divider()
            
            if not found_any:
                st.warning("Событий по вашему запросу не найдено.")