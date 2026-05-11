import os
import re
import json
import torch
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from transformers import AutoTokenizer, T5ForConditionalGeneration, AutoModelForSeq2SeqLM


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


def summarize(text, max_len=600):
    inputs = sum_tokenizer([text], max_length=max_len, truncation=True, return_tensors="pt").to(DEVICE)
    out_ids = sum_model.generate(**inputs, no_repeat_ngram_size=4, num_beams=5, max_length=256)
    return sum_tokenizer.decode(out_ids[0], skip_special_tokens=True)

def extract_events(summary, max_len=256):
    inputs = event_tokenizer(summary, return_tensors="pt", truncation=True, max_length=max_len).to(DEVICE)
    with torch.no_grad():
        out_ids = event_model.generate(**inputs, max_length=max_len)
    return event_tokenizer.decode(out_ids[0], skip_special_tokens=True)

def pipeline(text):
    summary = summarize(text)
    raw = extract_events(summary)
    vertices, edges = parse_output(raw)

    result = {
        "summary": summary,
        "raw_output": raw,
        "nodes": [{"id": vid, "text": vtext} for vid, vtext in vertices.items()],
        "edges": [{"source": src, "target": tgt, "type": rel} for src, tgt, rel in edges],
    }
    return result


if __name__ == "__main__":
    text = "Проект закрыли из-за нехватки бюджета. Команду перевели в другой отдел, потому что требовались узкопрофильные специалисты."
    result = pipeline(text)
    print(result)