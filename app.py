import streamlit as st
import pandas as pd
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Dashboard SIG-ILTB", layout="wide", page_icon="📊")

# Estilo para remover o menu padrão do Streamlit e deixar mais limpo
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Painel de Monitorização SIG-ILTB")
st.subheader("Vigilância Ativa - Nova Iguaçu")

# ID DA PLANILHA (O seu ID oficial)
SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"

# 2. BARRA LATERAL (CONTROLOS)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1085/1085810.png", width=100)
    st.markdown("### Controlos de Dados")
    if st.button('🔄 ATUALIZAR PAINEL AGORA'):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption("Sistema de Monitorização V1.0")

# 3. FUNÇÃO DE CARREGAMENTO (BLINDADA)
@st.cache_data(ttl=15)
def carregar_dados_oficiais():
    try:
        agora = int(time.time())
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes&nocache={agora}"
        url_e = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes&nocache={agora}"
        
        df_p = pd.read_csv(url_p, on_bad_lines='skip')
        df_e = pd.read_csv(url_e, on_bad_lines='skip')
        return df_p, df_e
    except:
        return None, None

df_pacientes, df_evolucoes = carregar_dados_oficiais()

# 4. EXIBIÇÃO DO PAINEL
if df_pacientes is not None and not df_pacientes.empty:
    
    # --- MÉTRICAS ---
    col1, col2, col3 = st.columns(3)
    
    total = len(df_pacientes)
    # Tenta identificar a coluna de situação (ajuste o índice se necessário)
    try:
        col_sit = df_pacientes.columns[23] 
        ativos = len(df_pacientes[df_pacientes[col_sit].astype(str).str.contains('Em andamento', na=False, case=False)])
        interrupcoes = len(df_pacientes[df_pacientes[col_sit].astype(str).str.contains('Interrupção', na=False, case=False)])
    except:
        ativos = total
        interrupcoes = 0

    col1.metric("Total de Cadastros", total)
    col2.metric("Tratamentos Ativos", ativos)
    col3.metric("Busca Ativa (Interrupções)", interrupcoes)
    
    st.divider()

    # --- TABELAS ---
    tab1, tab2 = st.tabs(["📋 Lista de Pacientes", "📈 Histórico de Evoluções"])
    
    with tab1:
        st.dataframe(df_pacientes, use_container_width=True, hide_index=True)
        
    with tab2:
        if df_evolucoes is not None and not df_evolucoes.empty:
            st.dataframe(df_evolucoes, use_container_width=True, hide_index=True)
        else:
            st.info("Aguardando os primeiros registos de evolução...")
            
else:
    st.error("⚠️ Erro ao carregar dados. Verifique a ligação à internet ou se a Planilha está aberta para 'Qualquer pessoa com o link'.")
