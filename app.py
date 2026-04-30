import streamlit as st
import pandas as pd
import requests

# Documentação: Configuração básica da página do painel
st.set_page_config(page_title="Gestão ILTB", layout="wide")

# COLE AQUI A NOVA URL GERADA NO PASSO ANTERIOR DO GOOGLE
URL_GOOGLE = "COLE_SUA_URL_AQUI"

st.title("📊 Painel de Monitoramento ILTB em Tempo Real")

# Botão para atualizar os dados
if st.button("🔄 Buscar Dados no Servidor"):
    try:
        # A Mágica: Colocamos o "?read=true" no final da URL para pedir os dados ao porteiro
        url_python = f"{URL_GOOGLE}?read=true"
        
        # O Python bate na porta do Google
        resposta = requests.get(url_python)
        
        # Se o Google respondeu com sucesso (código 200 significa OK)
        if resposta.status_code == 200:
            # Transforma o pacote JSON em uma tabela visível (DataFrame)
            dados = resposta.json()
            df = pd.DataFrame(dados)
            
            st.success(f"Conexão estabelecida! {len(df)} pacientes carregados.")
            
            # Mostra a tabela na tela
            st.dataframe(df, use_container_width=True)
            
        else:
            st.error("Erro ao comunicar com o Google. O link pode estar restrito.")
            
    except Exception as e:
        # Método Educativo: Se falhar, mostramos o erro exato na tela para investigarmos
        st.error(f"Falha técnica na conexão: {e}")
