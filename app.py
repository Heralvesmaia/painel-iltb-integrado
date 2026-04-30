import streamlit as st
import pandas as pd
import requests
import json

# ==========================================
# 1. CONFIGURAÇÕES INICIAIS DA PÁGINA
# ==========================================
st.set_page_config(page_title="Prontuário Eletrônico ILTB", layout="wide")

# 👇 COLE A SUA URL DO GOOGLE AQUI (Entre as aspas) 👇
URL_GOOGLE = "COLE_AQUI_A_SUA_URL_TERMINADA_EM_/exec"

st.title("🩺 Prontuário Eletrônico - Gestão ILTB")

# ==========================================
# 2. FUNÇÃO ROBUSTA PARA BUSCAR DADOS
# ==========================================
@st.cache_data(ttl=10) # Guarda os dados por 10 segundos
def buscar_dados():
    url_python = f"{URL_GOOGLE}?read=true"
    try:
        # Aumentamos o timeout para dar tempo ao Google de processar a planilha
        resposta = requests.get(url_python, timeout=20)
        
        # Lê o texto bruto e converte para JSON de forma segura, ignorando cabeçalhos do servidor
        texto_puro = resposta.text.strip()
        dados = json.loads(texto_puro)
        return dados
        
    except json.JSONDecodeError:
        st.error("Falha ao converter os dados. A resposta do Google não pôde ser lida como JSON.")
        with st.expander("Ver resposta bruta do servidor para depuração"):
            st.code(texto_puro)
        return None
    except Exception as e:
        st.error(f"Erro de comunicação com o servidor: {e}")
        return None

# ==========================================
# 3. INTERFACE PRINCIPAL E LÓGICA DO PAINEL
# ==========================================
# Botão para limpar a memória e atualizar a tela com novos cadastros
if st.button("🔄 Atualizar Base de Dados"):
    st.cache_data.clear()
    st.rerun()

dados_brutos = buscar_dados()

if dados_brutos:
    # Converte os dados JSON em tabelas de dados dinâmicas (DataFrames Pandas)
    df_pacientes = pd.DataFrame(dados_brutos.get("pacientes", []))
    df_evolucoes = pd.DataFrame(dados_brutos.get("evolucoes", []))

    st.sidebar.header("🔍 Busca de Paciente")
    
    if not df_pacientes.empty:
        # Cria uma coluna virtual combinando Nome e CPF para facilitar a pesquisa visual
        df_pacientes["Busca"] = df_pacientes["Nome Do Paciente"].astype(str) + " - " + df_pacientes["Cns_Cpf (Id)"].astype(str)
        paciente_selecionado = st.sidebar.selectbox("Selecione o paciente:", df_pacientes["Busca"].tolist())

        # ==========================================
        # 4. EXIBIÇÃO DO PRONTUÁRIO LONGITUDINAL
        # ==========================================
        if paciente_selecionado:
            st.divider()
            
            # Filtra os dados apenas do paciente que foi selecionado na barra lateral
            dados_paciente = df_pacientes[df_pacientes["Busca"] == paciente_selecionado].iloc[0]
            id_paciente = dados_paciente["Cns_Cpf (Id)"]

            # Exibe o Cabeçalho de Identificação do Paciente
            st.subheader(f"👤 Paciente: {dados_paciente['Nome Do Paciente']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**ID (CNS/CPF):** {id_paciente}")
                st.write(f"**Idade:** {dados_paciente.get('Idade', 'N/A')}")
            with col2:
                st.write(f"**Data de Nascimento:** {dados_paciente.get('Data De Nascimento', 'N/A')}")
                st.write(f"**Unidade:** {dados_paciente.get('Unidade De Tratamento', 'N/A')}")
            with col3:
                st.write(f"**Situação Atual:** {dados_paciente.get('Situação Atual', 'N/A')}")
                st.write(f"**Início TPT:** {dados_paciente.get('Início Tpt', 'N/A')}")

            st.divider()

            # ==========================================
            # 5. LINHA DO TEMPO: EVOLUÇÕES CLÍNICAS
            # ==========================================
            st.subheader("📝 Histórico Clínico")
            
            # Garante que a tabela de evoluções tem dados e o campo do ID existe para cruzamento
            if not df_evolucoes.empty and "Cns_Cpf (Id)" in df_evolucoes.columns:
                evolucoes_paciente = df_evolucoes[df_evolucoes["Cns_Cpf (Id)"] == id_paciente].copy()
                
                if not evolucoes_paciente.empty:
                    # Mapeia as colunas de data baseadas no seu banco de dados real
                    colunas_data = ["Carimbo De Tempo", "Data Da Consulta", "Próxima Consulta"]
                    
                    # Converte texto em data real para o Python conseguir ordenar cronologicamente
                    for col in colunas_data:
                        if col in evolucoes_paciente.columns:
                            evolucoes_paciente[col] = pd.to_datetime(evolucoes_paciente[col], errors='coerce', dayfirst=True)
                    
                    # Ordena o prontuário: a consulta mais recente aparece primeiro no topo
                    if "Data Da Consulta" in evolucoes_paciente.columns:
                        evolucoes_paciente = evolucoes_paciente.sort_values(by="Data Da Consulta", ascending=False)
                    
                    # Reaplica a máscara visual DD/MM/YYYY estrita e substitui datas vazias por '-'
                    for col in colunas_data:
                        if col in evolucoes_paciente.columns:
                            evolucoes_paciente[col] = evolucoes_paciente[col].dt.strftime('%d/%m/%Y').fillna('-')

                    # Remove a coluna do CPF/CNS da tabela para não poluir a tela, já que o cabeçalho já mostra
                    if "Cns_Cpf (Id)" in evolucoes_paciente.columns:
                        evolucoes_paciente = evolucoes_paciente.drop(columns=["Cns_Cpf (Id)"])

                    # Renderiza a tabela limpa
                    st.dataframe(evolucoes_paciente, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma evolução registrada para este paciente até o momento.")
            else:
                st.warning("Aba de evoluções vazia ou sem a coluna 'Cns_Cpf (Id)' de ligação.")

    else:
        st.warning("Nenhum paciente cadastrado na base de dados do Google Planilhas.")
else:
    st.info("Tentando conectar com a base de dados... Caso persista, recarregue a página.")
