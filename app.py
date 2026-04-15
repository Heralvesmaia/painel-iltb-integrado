import streamlit as st
import pandas as pd
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Dashboard SIG-ILTB", layout="wide")
st.title("📊 Painel de Monitorização SIG-ILTB - Nova Iguaçu")

# 2. BOTÃO DE SINCRONIZAÇÃO FORÇADA
# Este botão limpa a memória do site e força a leitura de novos dados da planilha
if st.sidebar.button('🔄 ATUALIZAR DADOS AGORA'):
    st.cache_data.clear()
    st.rerun()

# 3. LIGAÇÃO DIRETA À PLANILHA GOOGLE
# Usamos um "timestamp" (carimbo de tempo) para forçar o Google a enviar a versão mais recente
SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"
timestamp = int(time.time())

URL_PACIENTES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes&t={timestamp}"
URL_EVOLUCOES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes&t={timestamp}"

# Função para carregar os dados de forma segura
@st.cache_data(ttl=60) # Guarda os dados por 60 segundos
def carregar_dados():
    try:
        df_pacientes = pd.read_csv(URL_PACIENTES)
        df_evolucoes = pd.read_csv(URL_EVOLUCOES)
        return df_pacientes, df_evolucoes
    except Exception as e:
        return None, None

df_pacientes, df_evolucoes = carregar_dados()

# 4. CONSTRUÇÃO DO PAINEL VISUAL
if df_pacientes is not None and not df_pacientes.empty:
    
    # --- MÉTRICAS PRINCIPAIS ---
    st.markdown("### Resumo Geral")
    col1, col2, col3 = st.columns(3)
    
    total_pacientes = len(df_pacientes)
    
    # A procurar na Coluna de Situação Atual (ajuste o nome se estiver diferente na linha 1 da sua planilha)
    nome_coluna_situacao = df_pacientes.columns[23] if len(df_pacientes.columns) >= 24 else df_pacientes.columns[-1]
    
    ativos = len(df_pacientes[df_pacientes[nome_coluna_situacao].astype(str).str.contains('Em andamento', na=False, case=False)])
    interrompidos = len(df_pacientes[df_pacientes[nome_coluna_situacao].astype(str).str.contains('Interrupção', na=False, case=False)])
    
    col1.metric("Total de Cadastros", total_pacientes)
    col2.metric("Tratamentos Ativos", ativos)
    col3.metric("Busca Ativa (Interrupções)", interrompidos)
    
    st.divider()

    # --- TABELAS DE DADOS ---
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
    st.error("⚠️ Não foi possível carregar os dados. Verifique se a sua Planilha do Google está com o acesso definido como 'Qualquer pessoa com a ligação'.")
