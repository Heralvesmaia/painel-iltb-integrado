import streamlit as st
import pandas as pd
import requests

# 1. Configuração básica da página do painel
st.set_page_config(page_title="Gestão ILTB", layout="wide")

# 2. AQUI ESTÁ A CORREÇÃO: Sua URL real do Google Apps Script
URL_GOOGLE = "https://script.google.com/macros/s/AKfycbwJIGdxw5P0xxjsyCTKbqgbhoghJNCAyrGAPHIlT33GKbRTYc6iTTIM_HEofIYuUuXyLA/exec"

st.title("📊 Painel de Monitoramento ILTB em Tempo Real")

# 3. Botão para atualizar os dados
if st.button("🔄 Buscar Dados no Servidor"):
    try:
        # A Mágica: Colocamos o "?read=true" no final da URL para pedir os dados ao Google
        url_python = f"{URL_GOOGLE}?read=true"
        
        # O Python bate na porta do Google
        resposta = requests.get(url_python, timeout=15)
        
        # Se o Google respondeu com sucesso (código 200 significa OK)
        if resposta.status_code == 200:
            try:
                # Transforma o pacote JSON em uma tabela visível (DataFrame)
                dados = resposta.json()
                df = pd.DataFrame(dados)
                
                # Exibe uma mensagem de sucesso
                st.success(f"Conexão estabelecida! {len(df)} pacientes carregados.")
                
                # Mostra a tabela na tela do Streamlit
                st.dataframe(df, use_container_width=True)
                
            except Exception:
                st.error("O Google enviou uma resposta, mas não no formato esperado (JSON). Verifique as permissões de 'Qualquer pessoa' no Apps Script.")
                with st.expander("Ver resposta bruta do servidor"):
                    st.code(resposta.text)
                    
        else:
            st.error(f"Erro ao comunicar com o Google. Status do servidor: {resposta.status_code}")
            
    except Exception as e:
        # Método Educativo: Se a internet falhar ou a URL estiver errada, mostramos o erro aqui
        st.error(f"Falha técnica na conexão: {e}")
