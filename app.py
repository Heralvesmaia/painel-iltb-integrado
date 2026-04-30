import streamlit as st
import pandas as pd
import requests

# URL do seu Web App (Use sempre a que termina em /exec)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx_k0M-OK6sSjralFSjOTyGojh7noWZZ35Og6ce-puvFSSjUUILU55ZmvuAz5Sx4pn9bQ/exec"

def buscar_dados():
    try:
        # Faz a requisição com o parâmetro de leitura
        response = requests.get(URL_SCRIPT + "?read=true", timeout=15)
        
        # Se o status for 200 (Sucesso)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception:
                st.error("O Google enviou uma resposta que não é um JSON.")
                with st.expander("Ver resposta bruta do servidor"):
                    st.code(response.text) # Mostra o erro real que o Google está dando
                return None
        else:
            st.error(f"Erro no servidor Google: Status {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Falha na conexão: {e}")
        return None

# Interface do Streamlit
st.title("📊 Painel de Monitoramento ILTB")

if st.button("🔄 Atualizar Dados"):
    dados = buscar_dados()
    if dados:
        df = pd.DataFrame(dados)
        st.success(f"Conectado! {len(df)} registros encontrados.")
        st.dataframe(df)
    else:
        st.info("Aguardando dados ou planilha vazia.")
