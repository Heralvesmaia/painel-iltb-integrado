import streamlit as st
import pandas as pd
import time
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SIG-ILTB - Prontuário Eletrônico", layout="wide", page_icon="🏥")

# Função para garantir que o ID (CNS/CPF) seja lido como texto puro e sem .0
def limpar_id(valor):
    if pd.isna(valor) or valor == "": return ""
    v = str(valor).strip()
    if v.endswith('.0'): v = v[:-2]
    return re.sub(r'[^0-9]', '', v) # Mantém apenas números

# 2. CENTRAL DE ACESSOS (Mantida conforme solicitado)
USUARIOS = {
    "heraldo_admin": {"senha": "admin123", "nome_oficial": "TODAS"},
    "ist_hgni": {"senha": "ist_hgni", "nome_oficial": "AMBULATORIO DE IST DO HGNI"},
    "cf_austin": {"senha": "cf_austin", "nome_oficial": "UBS AUSTIN"},
    # ... (Suas outras unidades aqui)
}

# 3. FUNÇÃO DE LOGIN
def tela_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        st.markdown("<h1 style='text-align: center;'>🔐 Sistema SIG-ILTB</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login"):
                u = st.text_input("Utilizador").lower().strip()
                s = st.text_input("Senha", type="password").strip()
                if st.form_submit_button("Entrar"):
                    # Verificação simplificada para teste, use seu dicionário USUARIOS real aqui
                    if u == "heraldo_admin" and s == "admin123":
                        st.session_state["autenticado"] = True
                        st.session_state["usuario_atual"] = u
                        st.rerun()
                    else: st.error("Incorreto")
        return False
    return True

if tela_login():
    st.markdown("""<style>.main { background-color: #f4f6f9; } .stMetric { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #0056b3; }</style>""", unsafe_allow_html=True)
    
    SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"
    
    @st.cache_data(ttl=10)
    def carregar_dados():
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes"
        url_e = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes"
        # Lemos tudo como string para evitar o erro do .0 nos documentos
        df_p = pd.read_csv(url_p, dtype=str).fillna("")
        df_e = pd.read_csv(url_e, dtype=str).fillna("")
        
        # Limpeza de colunas e IDs
        df_p.columns = df_p.columns.str.strip()
        df_e.columns = df_e.columns.str.strip()
        
        df_p['ID_LINK'] = df_p['Cns_Cpf (Id)'].apply(limpar_id)
        df_e['ID_LINK'] = df_e['Cns_Cpf (Id)'].apply(limpar_id)
        return df_p, df_e

    df_pacientes, df_evolucoes = carregar_dados()

    if df_pacientes is not None:
        tab1, tab2, tab3 = st.tabs(["🩺 Prontuário Longitudinal", "📋 Lista de Pacientes", "📈 Base Global"])

        with tab1:
            st.markdown("### 🔍 Busca de Prontuário")
            nomes = ["Selecione..."] + sorted(df_pacientes["Nome Do Paciente"].unique().tolist())
            escolha = st.selectbox("Paciente:", nomes, label_visibility="collapsed")

            if escolha != "Selecione...":
                p = df_pacientes[df_pacientes["Nome Do Paciente"] == escolha].iloc[0]
                id_paciente = p['ID_LINK']
                
                # Busca evoluções deste paciente
                evols = df_evolucoes[df_evolucoes['ID_LINK'] == id_paciente]
                
                # Dados dinâmicos vindos da última evolução (se existir)
                prox_con = "-"
                sit_final = p['Situação Atual']
                peso_atual = "-"
                
                if not evols.empty:
                    ultima = evols.iloc[-1] # Pega a última linha da Aba Evoluções
                    prox_con = ultima['Data Da Próxima Consulta']
                    sit_final = ultima['Nova Situação']
                    peso_atual = ultima['Peso Corporal (kg)']

                st.markdown("---")
                # --- CABEÇALHO DO PRONTUÁRIO ---
                st.subheader(f"👤 {escolha.upper()}")
                st.write(f"**CNS/CPF:** {p['Cns_Cpf (Id)']} &nbsp;|&nbsp; **Raça/Cor:** {p['Raça/Cor']} &nbsp;|&nbsp; **Nacionalidade:** {p['Nacionalidade']}")
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"**Início TPT:** {p['Início Tpt']}")
                    c1.markdown(f"**Tratamento:** {p['Medicamento']}")
                    
                    c2.markdown(f"**Gestante:** {p['Gestante']}")
                    c2.markdown(f"**Peso Atual:** {peso_atual} kg")
                    
                    # Como "Posologia" e "Término" não existem como colunas na sua planilha, 
                    # o sistema avisa ou calcula (Término não foi mapeado no seu formulário)
                    c3.markdown(f"**Posologia:** (Não mapeado)")
                    c3.markdown(f"**Próxima Consulta:** :blue[{prox_con}]")
                
                if "óbito" in sit_final.lower(): st.error(f"SITUAÇÃO: {sit_final.upper()}")
                elif "andamento" in sit_final.lower(): st.info(f"SITUAÇÃO: {sit_final.upper()}")
                else: st.success(f"SITUAÇÃO: {sit_final.upper()}")

                st.markdown("### 🗓️ Histórico Longitudinal de Evoluções")
                if not evols.empty:
                    # Inverter para mostrar a mais recente primeiro
                    for _, row in evols.iloc[::-1].iterrows():
                        with st.container(border=True):
                            st.markdown(f"**📅 {row['Data Da Consulta']} - {row['Tipo De Retorno (Mês)']}**")
                            st.write(f"**Relato Clínico:** {row['Relato Clínico']}")
                            st.write(f"**Conduta:** {row['Conduta']}")
                            st.caption(f"Peso: {row['Peso Corporal (kg)']}kg | Medicamento: {row['Medicamento']}")
                else:
                    st.warning("⚠️ Nenhuma evolução encontrada na aba 'Evolucoes' para este ID.")

        with tab2: st.dataframe(df_pacientes)
        with tab3: st.dataframe(df_evolucoes)
