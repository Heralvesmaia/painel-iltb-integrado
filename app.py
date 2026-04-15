import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DO PAINEL
st.set_page_config(page_title="SIG-ILTB Nova Iguaçu", layout="wide", page_icon="📊")

# 2. LIGAÇÃO À PLANILHA
SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"
URL_PACIENTES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes"
URL_EVOLUCOES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes"

st.title("📊 Painel de Monitoramento SIG-ILTB")
st.subheader("Vigilância Epidemiológica - Nova Iguaçu")

# 3. BOTÃO DE ATUALIZAÇÃO NA BARRA LATERAL
if st.sidebar.button('🔄 ATUALIZAR DADOS AGORA'):
    st.cache_data.clear()
    st.rerun()

# 4. FUNÇÃO PARA LER OS DADOS
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        p = pd.read_csv(URL_PACIENTES)
        e = pd.read_csv(URL_EVOLUCOES)
        return p, e
    except:
        return None, None

df_p, df_e = carregar_dados()

if df_p is not None:
    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Pacientes", len(df_p))
    c2.metric("Tratamentos Ativos", len(df_p[df_p['Situação Atual'] == 'Em andamento']))
    c3.metric("Interrupções (Busca Ativa)", len(df_p[df_p['Situação Atual'] == 'Interrupção do tratamento']))

    # Tabelas
    t1, t2 = st.tabs(["📋 Lista de Pacientes", "📈 Evoluções Clínicas"])
    with t1:
        st.dataframe(df_p, use_container_width=True)
    with t2:
        st.dataframe(df_e, use_container_width=True)
else:
    st.info("Conectando à Planilha...")
