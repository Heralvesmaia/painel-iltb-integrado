import streamlit as st
import pandas as pd
import time
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SIG-ILTB - PEP Longitudinal", layout="wide", page_icon="🏥")

# Função para garantir que o ID seja comparado corretamente (remove .0 e espaços)
def limpar_id(valor):
    if pd.isna(valor) or valor == "": return ""
    v = str(valor).strip().split('.')[0]
    return re.sub(r'[^0-9]', '', v)

# 2. CENTRAL DE ACESSOS (SUA LISTA)
USUARIOS = {
    "heraldo_admin": {"senha": "admin123", "nome_oficial": "TODAS"},
    "ist_hgni": {"senha": "ist_hgni", "nome_oficial": "AMBULATORIO DE IST DO HGNI"},
    "ubs_austin": {"senha": "ubs_austin", "nome_oficial": "UBS AUSTIN"},
    # ... adicione as outras conforme necessário
}

# 3. LOGIN
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔐 SIG-ILTB Login</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Utilizador").lower().strip()
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                if u in USUARIOS and USUARIOS[u]["senha"] == s:
                    st.session_state.update({"autenticado": True, "usuario_atual": u})
                    st.rerun()
                else: st.error("Login inválido")
    st.stop()

# 4. CARREGAMENTO COM NOMES DE COLUNAS EXATOS
SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"

@st.cache_data(ttl=5)
def carregar_base():
    url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes"
    url_e = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes"
    
    # Lê tudo como texto para evitar corromper números longos
    df_p = pd.read_csv(url_p, dtype=str).fillna("")
    df_e = pd.read_csv(url_e, dtype=str).fillna("")
    
    # Limpeza forçada dos nomes das colunas
    df_p.columns = df_p.columns.str.strip()
    df_e.columns = df_e.columns.str.strip()
    
    # Cria chaves de ligação puras
    df_p['CHAVE'] = df_p['Cns_Cpf (Id)'].apply(limpar_id)
    df_e['CHAVE'] = df_e['Cns_Cpf (Id)'].apply(limpar_id)
    
    return df_p, df_e

df_pacientes, df_evolucoes = carregar_base()

if df_pacientes is not None:
    # Filtro por unidade
    if st.session_state["usuario_atual"] != "heraldo_admin":
        unidade = USUARIOS[st.session_state["usuario_atual"]]["nome_oficial"]
        df_pacientes = df_pacientes[df_pacientes["Unidade De Tratamento"].str.contains(unidade, case=False, na=False)]

    tab1, tab2 = st.tabs(["🩺 Prontuário Longitudinal", "📋 Lista de Pacientes"])

    with tab1:
        st.markdown("### 🔍 Busca de Prontuário")
        nomes = ["Selecione..."] + sorted(df_pacientes["Nome Do Paciente"].unique().tolist())
        paciente_sel = st.selectbox("Paciente:", nomes, label_visibility="collapsed")

        if paciente_sel != "Selecione...":
            # Dados da Aba 1 (Pacientes)
            d = df_pacientes[df_pacientes["Nome Do Paciente"] == paciente_sel].iloc[0]
            chave = d['CHAVE']
            
            # Busca histórico na Aba 2 (Evoluções)
            hist = df_evolucoes[df_evolucoes['CHAVE'] == chave]
            
            # Variáveis dinâmicas
            sit_atual = d.get('Situação Atual', 'Em andamento')
            peso_val = "-"; prox_val = "-"
            
            if not hist.empty:
                ult = hist.iloc[-1]
                sit_atual = ult.get('Nova Situação', sit_atual)
                peso_val = ult.get('Peso Corporal (kg)', '-')
                prox_val = ult.get('Data Da Próxima Consulta', '-')

            # --- VISUAL DO PRONTUÁRIO ---
            st.markdown(f"## 👤 {paciente_sel.upper()}")
            st.write(f"**CNS/CPF:** {d.get('Cns_Cpf (Id)', '-')} | **Raça/Cor:** {d.get('Raça/Cor', '-')} | **Nacionalidade:** {d.get('Nacionalidade', '-')}")
            
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Início TPT:** {d.get('Início Tpt', '-')}")
                c1.markdown(f"**Tratamento:** {d.get('Medicamento', '-')}")
                
                c2.markdown(f"**Gestante:** {d.get('Gestante', '-')}")
                c2.markdown(f"**Peso Atual:** {peso_val} kg")
                
                # Posologia sugerida baseada no medicamento
                poso = "900mg Iso + 900mg Rifapentina (3 comp) / semana" if "3HP" in d.get('Medicamento','') else "Consultar Esquema"
                c3.markdown(f"**Posologia:** {poso}")
                c3.markdown(f"**Próxima Consulta:** :blue[{prox_val}]")

            # Cor do Status
            if "óbito" in sit_atual.lower(): st.error(f"SITUAÇÃO: {sit_atual.upper()}")
            elif "andamento" in sit_atual.lower(): st.info(f"SITUAÇÃO: {sit_atual.upper()}")
            else: st.success(f"SITUAÇÃO: {sit_atual.upper()}")

            st.markdown("### 🗓️ Histórico Longitudinal de Evoluções")
            if not hist.empty:
                for _, row in hist.iloc[::-1].iterrows():
                    with st.container(border=True):
                        st.markdown(f"**📅 {row.get('Data Da Consulta','-')} - {row.get('Tipo De Retorno (Mês)','-')}**")
                        st.write(f"**Relato Clínico:** {row.get('Relato Clínico', '-')}")
                        st.write(f"**Conduta:** {row.get('Conduta', '-')}")
                        st.caption(f"Peso: {row.get('Peso Corporal (kg)','-')}kg | Situação: {row.get('Nova Situação','-')} | Medicamento: {row.get('Medicamento','-')}")
            else:
                st.warning(f"⚠️ Nenhuma evolução encontrada para o ID {chave}. Verifique se o ID na aba Evoluções está exatamente igual.")

with st.sidebar:
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
