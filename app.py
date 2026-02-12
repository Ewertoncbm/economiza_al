import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import os
from datetime import datetime
import streamlit as st
import pandas as pd

# (Opcional) prints de diagnóstico — pode remover depois
print("APP ROOT =", ROOT)
print("SRC PATH =", SRC)
print("SRC EXISTS =", SRC.exists())
print("sys.path =", sys.path[:3])

from ingest import load_feiras_excel, load_latest_from_inbound
from categorize import refine_category, normalize_item
from charts import plot_top_freq, plot_avg_by_category
from optimize import build_summary_table


st.set_page_config(page_title="Economiza - Feiras", layout="wide")

st.title("🛒 Feiras: Itens frequentes, histórico e (em breve) Economiza Alagoas")

with st.sidebar:
    st.header("Importação")
    mode = st.radio("Como importar?", ["Upload (manual)", "Automático (pasta data/inbound)"], index=0)

    st.divider()
    st.header("Configurações")
    show_raw = st.checkbox("Mostrar dados brutos extraídos", value=False)
    top_n = st.slider("Top N itens por frequência", 5, 50, 15)

    st.divider()
    st.header("Economiza Alagoas (API)")
    token = os.getenv("ECONOMIZA_APPTOKEN", "").strip()
    st.write("Status do token:", "✅ configurado" if token else "⏳ aguardando (rodando em modo offline)")

# --- Carregar dados ---
df_raw = None
source_name = ""

if mode == "Upload (manual)":
    up = st.file_uploader("Envie a planilha de feiras (.xlsx)", type=["xlsx"])
    if up:
        df_raw = load_feiras_excel(up)
        source_name = up.name
else:
    latest_path = load_latest_from_inbound("data/inbound")
    if latest_path:
        df_raw = load_feiras_excel(latest_path)
        source_name = os.path.basename(latest_path)
        st.info(f"Importado automaticamente: {source_name}")
    else:
        st.warning("Nenhum arquivo encontrado em data/inbound. Coloque um .xlsx lá ou use Upload.")
        st.stop()

if df_raw is None or df_raw.empty:
    st.stop()

# --- Normalização + categorização ---
df = df_raw.copy()
df["produto_norm"] = df["produto"].apply(normalize_item)
df["categoria"] = df["produto_norm"].apply(refine_category)

# --- Resumo (frequência, médio, min, max) ---
summary = build_summary_table(df)

# --- UI: filtros ---
st.subheader("📌 Resumo (itens mais frequentes + histórico de preços)")
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    categorias = ["(todas)"] + sorted(summary["categoria"].unique().tolist())
    cat_sel = st.selectbox("Categoria", categorias, index=0)

with col2:
    search = st.text_input("Buscar item (contém)")

with col3:
    order = st.selectbox("Ordenar por", ["frequencia desc", "preco_medio desc", "preco_min asc", "preco_max desc"])

f = summary.copy()
if cat_sel != "(todas)":
    f = f[f["categoria"] == cat_sel]
if search.strip():
    f = f[f["produto_norm"].str.contains(search.strip().lower(), na=False)]

if order == "frequencia desc":
    f = f.sort_values(["frequencia", "produto_norm"], ascending=[False, True])
elif order == "preco_medio desc":
    f = f.sort_values(["preco_medio", "produto_norm"], ascending=[False, True])
elif order == "preco_min asc":
    f = f.sort_values(["preco_min", "produto_norm"], ascending=[True, True])
else:
    f = f.sort_values(["preco_max", "produto_norm"], ascending=[False, True])

st.dataframe(f.head(top_n), use_container_width=True)

# ============================================
# ECONOMIZA AL - CONSULTA DE PREÇOS
# ============================================

st.subheader("🏷️ Economiza AL (consulta de preços)")

from economiza_api import economiza_search, extract_offers

if not os.getenv("ECONOMIZA_APPTOKEN", "").strip():
    st.warning("Token ECONOMIZA_APPTOKEN ainda não configurado.")
else:
    if st.button("🔎 Consultar no Economiza AL"):
        itens_consulta = f.head(15)["produto_norm"].tolist()

        offers_all = []
        prog = st.progress(0)

        for i, item_name in enumerate(itens_consulta, start=1):
            try:
                api = economiza_search(
                    descricao=item_name.upper(),
                    latitude=-9.6498,
                    longitude=-35.7089,
                    raio_km=15,
                    dias=7
                )
                offers = extract_offers(api)
                for o in offers:
                    o["item_consulta"] = item_name
                offers_all.extend(offers)
            except Exception as e:
                offers_all.append({"item_consulta": item_name, "erro": str(e)})

            prog.progress(i / len(itens_consulta))

        offers_df = pd.DataFrame(offers_all)
        st.dataframe(offers_df, use_container_width=True)
# --- Gráficos ---
st.subheader("📊 Gráficos")
g1, g2 = st.columns(2)
with g1:
    fig = plot_top_freq(summary, top_n=min(top_n, 20))
    st.pyplot(fig, clear_figure=True)
with g2:
    fig = plot_avg_by_category(summary)
    st.pyplot(fig, clear_figure=True)

# --- Exportar ---
st.subheader("⬇️ Exportar")
out_path = os.path.join("data/outputs", f"resumo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
if st.button("Gerar Excel do resumo"):
    os.makedirs("data/outputs", exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as w:
        summary.to_excel(w, index=False, sheet_name="Resumo")
        df.to_excel(w, index=False, sheet_name="Dados_Normalizados")
    st.success(f"Gerado: {out_path}")

# --- Debug / bruto ---
if show_raw:
    st.subheader("🧾 Dados brutos extraídos (primeiras linhas)")
    st.dataframe(df_raw.head(50), use_container_width=True)

st.caption(f"Fonte: {source_name} | Modo: {'online' if token else 'offline'}")
