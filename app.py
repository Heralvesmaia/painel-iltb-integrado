import streamlit as st
import pandas as pd
import time

# O ID da sua planilha (Mantenha o seu original aqui)
SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"

# 1. BOTÃO DE ATUALIZAÇÃO FORÇADA
if st.sidebar.button('🔄 ATUALIZAR DADOS AGORA'):
    st.cache_data.clear() # Limpa a memória do Streamlit
    st.rerun()            # Reinicia o site

# 2. O TRUQUE PARA ENGANAR O GOOGLE
@st.cache_data(ttl=10) # Guarda a memória por no máximo 10 segundos
def carregar_dados():
    try:
        # A MÁGICA: Colocamos a hora atual dentro do link. 
        # Como a hora muda a cada segundo, o Google é forçado a gerar um arquivo CSV novo!
        agora = int(time.time()) 
        
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes&nocache={agora}"
        url_e = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes&nocache={agora}"
        
        df_pacientes = pd.read_csv(url_p)
        df_evolucoes = pd.read_csv(url_e)
        return df_pacientes, df_evolucoes
   except Exception as e:
        st.error(f"Ocorreu um erro ao ler o Google: {e}")
        return None, None

# Carrega as planilhas
df_pacientes, df_evolucoes = carregar_dados()
