import streamlit as st
import pandas as pd
import requests

# Configurações da página
st.set_page_config(page_title="Gestão ILTB - Real Time", layout="wide")

# URL do seu Google Apps Script (Sua URL Web App)
URL_GOOGLE = "https://script.google.com/macros/s/AKfycbx_k0M-OK6sSjralFSjOTyGojh7noWZZ35Og6ce-puvFSSjUUILU55ZmvuAz5Sx4pn9bQ/exec"

st.title("📊 Painel de Monitoramento ILTB")
st.write("Dados atualizados em tempo real vindos do Google Sheets.")

# Função para buscar dados
def buscar_dados():
    try:
        # Chamamos a URL com o parâmetro ?read=true que criamos no Passo 1
        response = requests.get(URL_GOOGLE + "?read=true")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Erro ao acessar o Google Scripts.")
            return []
    except Exception as e:
        st.error(f"Falha na conexão: {e}")
        return []

# Processamento dos dados
dados_brutos = buscar_dados()

if dados_brutos:
    # Cria o DataFrame (Tabela)
    df = pd.DataFrame(dados_brutos)
    
    # --- CORREÇÃO IMPORTANTE: TRATAR IDENTIFICADOR COMO TEXTO ---
    # Isso evita que o Python corte o CPF/CNS ou transforme em número científico
    if 'Cns_Cpf (Id)' in df.columns:
        df['Cns_Cpf (Id)'] = df['Cns_Cpf (Id)'].astype(str)
    
    # Exibe métricas rápidas
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Pacientes", len(df))
    if 'Situacao Atual' in df.columns:
        c2.metric("Em Tratamento", len(df[df['Situacao Atual'] == 'Em andamento']))
        c3.metric("Interrupções", len(df[df['Situacao Atual'] == 'Interrupção']))

    # Tabela principal
    st.subheader("Lista Geral de Notificações")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("Nenhum dado encontrado ou a planilha está vazia.")
