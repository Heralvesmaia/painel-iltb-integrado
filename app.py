import streamlit as st
import pandas as pd
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Dashboard SIG-ILTB", layout="wide")
st.title("📊 Painel de Monitorização SIG-ILTB - Nova Iguaçu")

SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"

# 2. BOTÃO DE SINCRONIZAÇÃO FORÇADA
if st.sidebar.button('🔄 ATUALIZAR DADOS AGORA'):
    st.cache_data.clear()
    st.rerun()

# 3. FUNÇÃO BLINDADA CONTRA O CACHE DO GOOGLE
@st.cache_data(ttl=10) # Guarda no máximo por 10 segundos
def carregar_dados():
    try:
        # Colocamos o time.time() AQUI DENTRO para gerar um link novo a cada clique
        agora = int(time.time())
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes&nocache={agora}"
        url_e = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes&nocache={agora}"
        
        df_pacientes = pd.read_csv(url_p)
        df_evolucoes = pd.read_csv(url_e)
        return df_pacientes, df_evolucoes
    except Exception as e:
        return None, None

df_pacientes, df_evolucoes = carregar_dados()

# 4. CONSTRUÇÃO DO PAINEL VISUAL
if df_pacientes is not None and not df_pacientes.empty:
    
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

    tab1, tab2 = st.tabs(["📋 Fichas de Pacientes", "📈 Histórico de Evoluções"])
    
    with tab1:
        st.subheader("Base de Dados: Pacientes")
        st.dataframe(df_pacientes, use_container_width=True, hide_index=True)
        
    with tab2:
        st.subheader("Base de Dados: Evoluções")
        if df_evolucoes is not None and not df_evolucoes.empty:
            st.dataframe(df_evolucoes, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma evolução foi registada na planilha ou os dados ainda estão a ser processados.")
            
else:
    st.error("⚠️ Não foi possível carregar os dados. Verifique o link e o compartilhamento da planilha.")
