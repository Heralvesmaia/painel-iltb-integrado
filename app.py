import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Dashboard SIG-ILTB", layout="wide")
st.title("📊 Painel de Monitorização SIG-ILTB - Nova Iguaçu")

SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"

if st.sidebar.button('🔄 ATUALIZAR DADOS AGORA'):
    st.cache_data.clear()
    st.rerun()

st.info("⏳ Passo 1: O site acordou e está a preparar-se para ler o Google...")

@st.cache_data(ttl=10)
def carregar_dados():
    try:
        agora = int(time.time())
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes&nocache={agora}"
        url_e = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes&nocache={agora}"
        
        # O parâmetro on_bad_lines impede que o site trave se o Google mandar uma página de erro
        df_pacientes = pd.read_csv(url_p, on_bad_lines='skip')
        df_evolucoes = pd.read_csv(url_e, on_bad_lines='skip')
        
        return df_pacientes, df_evolucoes
    except Exception as e:
        return str(e), None

st.warning("⏳ Passo 2: A bater na porta do Google Drive...")
df_pacientes, df_evolucoes = carregar_dados()

# Teste de Erro Visual
if isinstance(df_pacientes, str):
    st.error(f"🚨 O Google bloqueou a entrada! Erro: {df_pacientes}")
elif df_pacientes is not None and not df_pacientes.empty:
    st.success("✅ Passo 3: SUCESSO! A porta abriu e os dados entraram.")
    
    # --- O PAINEL VOLTA AO NORMAL AQUI ---
    st.markdown("### Resumo Geral")
    col1, col2, col3 = st.columns(3)
    total_pacientes = len(df_pacientes)
    nome_coluna_situacao = df_pacientes.columns[23] if len(df_pacientes.columns) >= 24 else df_pacientes.columns[-1]
    
    ativos = len(df_pacientes[df_pacientes[nome_coluna_situacao].astype(str).str.contains('Em andamento', na=False, case=False)])
    interrompidos = len(df_pacientes[df_pacientes[nome_coluna_situacao].astype(str).str.contains('Interrupção', na=False, case=False)])
    
    col1.metric("Total de Cadastros", total_pacientes)
    col2.metric("Tratamentos Ativos", ativos)
    col3.metric("Busca Ativa (Interrupções)", interrompidos)
    st.divider()

    tab1, tab2 = st.tabs(["📋 Fichas", "📈 Evoluções"])
    with tab1:
        st.dataframe(df_pacientes, use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(df_evolucoes, use_container_width=True, hide_index=True)
else:
    st.error("⚠️ A planilha abriu, mas o site achou que ela estava vazia. Verifique o nome da aba 'Pacientes'.")
