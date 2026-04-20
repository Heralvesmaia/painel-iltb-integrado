import streamlit as st
import pandas as pd
import time
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SIG-ILTB - Prontuário Longitudinal", layout="wide", page_icon="🏥")

# Função para limpar IDs (CNS/CPF) e evitar erro de .0 ou espaços
def purificar_id(valor):
    if pd.isna(valor) or valor == "": return ""
    v = str(valor).strip().split('.')[0] # Remove .0 se houver
    return re.sub(r'[^0-9]', '', v) # Deixa só números

# 2. CENTRAL DE ACESSOS (Lista oficial)
USUARIOS = {
    "heraldo_admin": {"senha": "admin123", "nome_oficial": "TODAS"},
    "ist_hgni": {"senha": "ist_hgni", "nome_oficial": "AMBULATORIO DE IST DO HGNI"},
    "ubs_austin": {"senha": "ubs_austin", "nome_oficial": "UBS AUSTIN"},
    # Adicione as outras conforme a sua lista...
}

# 3. LOGIN
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔐 SIG-ILTB Login</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Utilizador").lower().strip()
            s = st.text_input("Senha", type="password").strip()
            if st.form_submit_button("Entrar"):
                if u in USUARIOS and USUARIOS[u]["senha"] == s:
                    st.session_state["autenticado"], st.session_state["usuario_atual"] = True, u
                    st.rerun()
                else: st.error("Utilizador ou Senha inválidos.")
    st.stop()

# 4. CARREGAMENTO DE DADOS
SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"

@st.cache_data(ttl=5) # Atualiza quase em tempo real
def buscar_dados():
    try:
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes"
        url_e = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes"
        
        # Lendo como string para não corromper CNS/CPF
        df_p = pd.read_csv(url_p, dtype=str).fillna("")
        df_e = pd.read_csv(url_e, dtype=str).fillna("")
        
        # Limpando nomes de colunas
        df_p.columns = df_p.columns.str.strip()
        df_e.columns = df_e.columns.str.strip()
        
        # Criando chaves de ligação limpas
        df_p['CHAVE'] = df_p['Cns_Cpf (Id)'].apply(purificar_id)
        df_e['CHAVE'] = df_e['Cns_Cpf (Id)'].apply(purificar_id)
        
        return df_p, df_e
    except Exception as e:
        st.error(f"Erro ao conectar com Google: {e}")
        return None, None

df_p, df_e = buscar_dados()

# 5. INTERFACE DO PRONTUÁRIO
if df_p is not None:
    # Filtro por unidade
    u_logado = st.session_state["usuario_atual"]
    nome_unidade = USUARIOS[u_logado]["nome_oficial"]
    if u_logado != "heraldo_admin":
        df_p = df_p[df_p["Unidade De Tratamento"].str.contains(nome_unidade, case=False, na=False)]

    tab1, tab2, tab3 = st.tabs(["🩺 Prontuário Longitudinal", "📋 Lista Geral", "📊 Base Global"])

    with tab1:
        st.markdown("### 🔍 Busca de Prontuário")
        nomes = ["Selecione..."] + sorted(df_p["Nome Do Paciente"].unique().tolist())
        paciente = st.selectbox("Escolha o Paciente:", nomes, label_visibility="collapsed")

        if paciente != "Selecione...":
            # Pega os dados do paciente na Aba 1
            dados = df_p[df_p["Nome Do Paciente"] == paciente].iloc[0]
            chave_paciente = dados['CHAVE']

            # Busca evoluções (Tenta por ID, se falhar tenta por Nome)
            historico = df_e[df_e['CHAVE'] == chave_paciente]
            if historico.empty:
                # Fallback: Busca por nome se o ID falhar
                historico = df_e[df_e['Cns_Cpf (Id)'].str.contains(paciente, case=False, na=False)]

            # Dados da última consulta para o cabeçalho
            peso_v = "-"; prox_v = "-"; sit_v = dados['Situação Atual']
            if not historico.empty:
                u_c = historico.iloc[-1]
                peso_v = u_c.get('Peso Corporal (kg)', '-')
                prox_v = u_c.get('Data Da Próxima Consulta', '-')
                sit_v = u_c.get('Nova Situação', sit_v)

            # --- EXIBIÇÃO DO CARTÃO ---
            st.markdown(f"## 👤 {paciente.upper()}")
            st.write(f"**CNS/CPF:** {dados['Cns_Cpf (Id)']} | **Raça/Cor:** {dados['Raça/Cor']} | **Nacionalidade:** {dados['Nacionalidade']}")
            
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"**Início TPT:** {dados['Início Tpt']}")
                    st.write(f"**Tratamento:** {dados['Medicamento']}")
                with c2:
                    st.write(f"**Gestante:** {dados['Gestante']}")
                    st.write(f"**Peso Atual:** {peso_v} kg")
                with c3:
                    st.write(f"**Posologia:** (Não mapeado no Cadastro)")
                    st.write(f"**Próxima Consulta:** :blue[{prox_v}]")
            
            # Status Colorido
            if "óbito" in sit_v.lower(): st.error(f"SITUAÇÃO: {sit_v.upper()}")
            elif "andamento" in sit_v.lower(): st.info(f"SITUAÇÃO: {sit_v.upper()}")
            else: st.success(f"SITUAÇÃO: {sit_v.upper()}")

            st.markdown("### 🗓️ Histórico Longitudinal de Evoluções")
            if not historico.empty:
                for _, row in historico.iloc[::-1].iterrows(): # Mais recente primeiro
                    with st.expander(f"📅 Consulta em {row['Data Da Consulta']} - {row['Tipo De Retorno (Mês)']}", expanded=True):
                        col_a, col_b = st.columns(2)
                        col_a.write(f"**Relato Clínico:**\n{row['Relato Clínico']}")
                        col_b.write(f"**Conduta:**\n{row['Conduta']}")
                        st.caption(f"Peso: {row['Peso Corporal (kg)']}kg | Situação na data: {row['Nova Situação']}")
            else:
                st.warning(f"⚠️ Nenhuma evolução encontrada para o ID {chave_paciente} ou Nome {paciente}.")

    with tab2: st.dataframe(df_p)
    with tab3: st.dataframe(df_e)

# Barra lateral
with st.sidebar:
    if st.button("🔄 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()
