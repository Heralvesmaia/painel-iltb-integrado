import streamlit as st
import pandas as pd

# Configuração visual do Painel
st.set_page_config(page_title="Monitor SIG-ILTB Nova Iguaçu", layout="wide")

# Link direto para exportação CSV das abas da sua planilha
SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"
URL_PACIENTES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes"
URL_EVOLUCOES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes"

st.title("📊 Painel de Monitoramento SIG-ILTB")
st.subheader("Vigilância Longitudinal de Nova Iguaçu")

# Função para carregar os dados em tempo real
@st.cache_data(ttl=60) 
def carregar_dados():
    try:
        p = pd.read_csv(URL_PACIENTES)
        e = pd.read_csv(URL_EVOLUCOES)
        return p, e
    except Exception as e:
        return None, None

df_p, df_e = carregar_dados()

if df_p is not None:
    # Métricas no topo do Painel
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Pacientes", len(df_p))
    
    # Filtro de situação
    situacao_col = 'Situação Atual' if 'Situação Atual' in df_p.columns else df_p.columns[-1]
    col2.metric("Tratamentos Ativos", len(df_p[df_p[situacao_col] == 'Em andamento']))
    col3.metric("Total de Consultas", len(df_e))

    # Abas de visualização
    tab_geral, tab_consultas = st.tabs(["📋 Lista de Pacientes", "📈 Histórico de Evoluções"])

    with tab_geral:
        st.dataframe(df_p, use_container_width=True)

    with tab_consultas:
        st.write("Histórico das últimas evoluções registradas:")
        st.dataframe(df_e, use_container_width=True)
else:
    st.info("Aguardando os primeiros dados serem inseridos no formulário para gerar o monitoramento.")
