import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime
from fpdf import FPDF

# ==========================================
# 1. CONFIGURAÇÕES INICIAIS DA PÁGINA
# ==========================================
# Configura o layout da página para ocupar a tela toda (wide)
st.set_page_config(page_title="Prontuário Eletrônico ILTB", layout="wide")

# URL oficial do seu Google Apps Script (Porteiro dos dados)
URL_GOOGLE = "https://script.google.com/macros/s/AKfycbwaQrmEhaZ65W7Nw9NrsdaMPiMsE2qnKoKIi2lquxnGT6-cBTeAp5XW8Gk7QsyNuBkW/exec"

st.title("🩺 Prontuário Eletrônico - Gestão ILTB")

# ==========================================
# 2. FUNÇÃO ROBUSTA PARA BUSCAR DADOS
# ==========================================
# @st.cache_data armazena o resultado por 10 segundos para deixar o app rápido
@st.cache_data(ttl=10)
def buscar_dados():
    url_python = f"{URL_GOOGLE}?read=true"
    try:
        # Faz a requisição na internet esperando até 20 segundos
        resposta = requests.get(url_python, timeout=20)
        # Limpa o texto bruto e converte em formato JSON
        texto_puro = resposta.text.strip()
        return json.loads(texto_puro)
    except Exception as e:
        # Em caso de erro, exibe um alerta na tela
        st.error(f"Erro de comunicação com o servidor: {e}")
        return None

# ==========================================
# 3. INTERFACE PRINCIPAL E LÓGICA DO PAINEL
# ==========================================
# Botão manual para forçar a limpeza da memória cache e buscar novos dados
if st.button("🔄 Atualizar Base de Dados"):
    st.cache_data.clear()
    st.rerun()

dados_brutos = buscar_dados()

if dados_brutos:
    # Converte as listas de dados do Google em Tabelas dinâmicas (DataFrames Pandas)
    df_pacientes = pd.DataFrame(dados_brutos.get("pacientes", []))
    df_evolucoes = pd.DataFrame(dados_brutos.get("evolucoes", []))

    st.sidebar.header("🔍 Busca de Paciente")
    
    # Se existirem pacientes cadastrados, cria o menu de busca
    if not df_pacientes.empty:
        # Cria uma coluna virtual combinando o Nome e o CPF para a caixa de seleção
        df_pacientes["Busca"] = df_pacientes["Nome Do Paciente"].astype(str) + " - " + df_pacientes["Cns_Cpf (Id)"].astype(str)
        paciente_selecionado = st.sidebar.selectbox("Selecione o paciente:", df_pacientes["Busca"].tolist())

        # ==========================================
        # 4. EXIBIÇÃO DO PRONTUÁRIO LONGITUDINAL
        # ==========================================
        if paciente_selecionado:
            st.divider()
            
            # Filtra e isola os dados do paciente escolhido
            dados_paciente = df_pacientes[df_pacientes["Busca"] == paciente_selecionado].iloc[0]
            id_paciente = dados_paciente["Cns_Cpf (Id)"]

            st.subheader(f"👤 Paciente: {dados_paciente['Nome Do Paciente']}")
            
            # Organiza as informações do paciente em 3 colunas visuais
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
            # 5. LINHA DO TEMPO E EXPORTAÇÃO
            # ==========================================
            st.subheader("📝 Histórico Clínico")
            
            evolucoes_limpas = pd.DataFrame() # Tabela vazia como segurança
            
            # Garante que a aba de evoluções existe e tem a coluna de ligação (ID)
            if not df_evolucoes.empty and "Cns_Cpf (Id)" in df_evolucoes.columns:
                evolucoes_paciente = df_evolucoes[df_evolucoes["Cns_Cpf (Id)"] == id_paciente].copy()
                
                if not evolucoes_paciente.empty:
                    colunas_data = ["Carimbo De Tempo", "Data Da Consulta", "Próxima Consulta"]
                    
                    # Converte os textos das colunas para objetos Data reais no Python
                    for col in colunas_data:
                        if col in evolucoes_paciente.columns:
                            evolucoes_paciente[col] = pd.to_datetime(evolucoes_paciente[col], errors='coerce', dayfirst=True)
                    
                    # Ordena cronologicamente: do atendimento mais novo para o mais antigo
                    if "Data Da Consulta" in evolucoes_paciente.columns:
                        evolucoes_paciente = evolucoes_paciente.sort_values(by="Data Da Consulta", ascending=False)
                    
                    # Reaplica a máscara de Data (DD/MM/YYYY) para exibição bonita na tela
                    for col in colunas_data:
                        if col in evolucoes_paciente.columns:
                            evolucoes_paciente[col] = evolucoes_paciente[col].dt.strftime('%d/%m/%Y').fillna('-')

                    # Remove a coluna de ID apenas para não aparecer repetido na tabela
                    if "Cns_Cpf (Id)" in evolucoes_paciente.columns:
                        evolucoes_limpas = evolucoes_paciente.drop(columns=["Cns_Cpf (Id)"])

                    # Renderiza a tabela limpa
                    st.dataframe(evolucoes_limpas, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma evolução registrada para este paciente até o momento.")
            else:
                st.warning("Aba de evoluções vazia ou sem a coluna 'Cns_Cpf (Id)'.")

            # ==========================================
            # 6. MÓDULO DE GERAÇÃO E DOWNLOAD DE PDF
            # ==========================================
            st.write("") # Espaçamento
            st.subheader("📄 Exportar Prontuário")
            st.write("O arquivo PDF é gerado automaticamente baseando-se no histórico acima.")
            
            # Inicializa a criação do PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Título Principal
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Prontuario Eletronico - ILTB", ln=True, align='C')
            pdf.ln(5)
            
            # Data de emissão com máscara DD/MM/YYYY
            data_emissao = datetime.now().strftime("%d/%m/%Y")
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(200, 10, txt=f"Data de Emissao: {data_emissao}", ln=True, align='R')
            
            # Dados do Paciente inseridos no PDF
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 8, txt=f"Paciente: {dados_paciente['Nome Do Paciente']}", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.cell(200, 6, txt=f"ID (CNS/CPF): {id_paciente}", ln=True)
            pdf.cell(200, 6, txt=f"Unidade de Tratamento: {dados_paciente.get('Unidade De Tratamento', '-')}", ln=True)
            pdf.cell(200, 6, txt=f"Situacao Atual: {dados_paciente.get('Situação Atual', '-')}", ln=True)
            pdf.ln(5)
            
            # Cabeçalho das evoluções
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Historico de Evolucoes Clinicas", ln=True)
            pdf.ln(2)
            
            # Laço de repetição para escrever as evoluções no PDF
            pdf.set_font("Arial", size=10)
            if not evolucoes_limpas.empty:
                for index, row in evolucoes_limpas.iterrows():
                    # Tratamento de segurança (encoding) para acentos não quebrarem a biblioteca FPDF
                    dt_consulta = str(row.get('Data Da Consulta', '-')).encode('latin-1', 'replace').decode('latin-1')
                    situacao = str(row.get('Nova Situação', '-')).encode('latin-1', 'replace').decode('latin-1')
                    relato = str(row.get('Relato Clínico', '-')).encode('latin-1', 'replace').decode('latin-1')
                    conduta = str(row.get('Conduta', '-')).encode('latin-1', 'replace').decode('latin-1')
                    
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(200, 6, txt=f"Data da Consulta: {dt_consulta} | Situacao: {situacao}", ln=True)
                    
                    pdf.set_font("Arial", size=10)
                    pdf.multi_cell(0, 6, txt=f"Relato: {relato}")
                    pdf.multi_cell(0, 6, txt=f"Conduta: {conduta}")
                    pdf.ln(3) # Espaço visual entre as evoluções
            else:
                pdf.cell(200, 10, txt="Nenhum atendimento registrado no historico.", ln=True)
            
            # ----------------------------------------------------
            #  MÁGICA DO DOWNLOAD: Salva em memória e cria botão
            # ----------------------------------------------------
            # 1. Cria um arquivo temporário no servidor
            nome_arquivo_pdf = f"Prontuario_{id_paciente}.pdf"
            pdf.output(nome_arquivo_pdf)
            
            # 2. Abre o arquivo como "bytes" (Formato que os navegadores entendem para download)
            with open(nome_arquivo_pdf, "rb") as arquivo_pdf:
                pdf_bytes = arquivo_pdf.read()
            
            # 3. Exibe o botão de Download nativo do Streamlit na tela
            st.download_button(
                label="⬇️ Baixar Prontuário em PDF",
                data=pdf_bytes,
                file_name=nome_arquivo_pdf,
                mime="application/pdf"
            )

    else:
        st.warning("Nenhum paciente cadastrado na base de dados do Google Planilhas.")
else:
    st.info("Tentando conectar com a base de dados... Caso persista, recarregue a página.")
