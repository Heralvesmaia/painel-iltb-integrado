import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from fpdf import FPDF

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Gestão ILTB - Nova Iguaçu", page_icon="🩺", layout="wide")

# ==========================================
# 0. TELA DE LOGIN (SEGURANÇA)
# ==========================================
def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Bras%C3%A3o_de_Nova_Igua%C3%A7u.svg/1200px-Bras%C3%A3o_de_Nova_Igua%C3%A7u.svg.png", width=100)
            st.title("🔒 Acesso Restrito")
            st.write("Painel Gerencial SIG-ILTB")
            
            with st.form("login_form"):
                usuario = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar no Sistema")
                
                if submit:
                    if usuario == "heraldo_admin" and senha == "admin-123456": 
                        st.session_state["autenticado"] = True
                        st.rerun() 
                    else:
                        st.error("❌ Usuário ou senha incorretos.")
        st.stop() 

verificar_login()

# ==========================================
# FUNÇÃO GERADORA DE PDF BLINDADA
# ==========================================
def gerar_pdf_prontuario(paciente, evolucoes, situacao_real):
    pdf = FPDF()
    pdf.add_page()
    
    def formatar_texto(texto):
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(w=190, h=10, txt=formatar_texto('SIG-ILTB NOVA IGUAÇU - PRONTUÁRIO LONGITUDINAL'), border=0, ln=1, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(w=190, h=8, txt=formatar_texto(f"PACIENTE: {paciente.get('Nome de Registro', 'Não informado')}"), border=0, ln=1)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(w=190, h=6, txt=formatar_texto(f"ID: {paciente.get('Cns_Cpf (Id)', paciente.get('Cns_Cpf', '-'))} | Idade: {paciente.get('Idade', '-')}"), border=0, ln=1)
    pdf.cell(w=190, h=6, txt=formatar_texto(f"Esquema: {paciente.get('Medicamento', '-')} | Situação Atual: {situacao_real}"), border=0, ln=1)
    
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(w=190, h=10, txt=formatar_texto("HISTÓRICO DE EVOLUÇÕES"), border=0, ln=1)
    
    if evolucoes.empty:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(w=190, h=8, txt=formatar_texto("Nenhuma evolução registrada."), border=0, ln=1)
    else:
        for idx, evo in evolucoes.iterrows():
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(w=190, h=6, txt=formatar_texto(f"Data: {evo.get('Data Da Consulta', '-')} | Status: {evo.get('Nova Situação', '-')}"), border=0, ln=1)
            pdf.set_font("Arial", '', 10)
            pdf.set_x(10)
            pdf.multi_cell(w=190, h=6, txt=formatar_texto(f"Conduta: {evo.get('Conduta', '-')}"))
            pdf.ln(2)

    try:
        return bytes(pdf.output()) 
    except:
        return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 1. CONEXÃO E CARREGAMENTO
# ==========================================
API_URL = "https://script.google.com/macros/s/AKfycbyTyHorAMicNY7lNO6cVWG-pyAe03pTR8obS3NGOGDlZxXY-eS5Jt2O9Y4gzxtGW-a3rg/exec"

@st.cache_data(ttl=60)
def carregar_dados():
    try: 
        response = requests.get(f"{API_URL}?read=true", allow_redirects=True)
        if response.status_code == 200:
            dados = response.json()
            return pd.DataFrame(dados.get("pacientes", [])), pd.DataFrame(dados.get("evolucoes", []))
    except:
        pass
    return pd.DataFrame(), pd.DataFrame()

df_pacientes, df_evolucoes = carregar_dados()

# ==========================================
# 2. PADRONIZAÇÃO E SINCRONIZAÇÃO DE STATUS
# ==========================================
def obter_situacao_real(paciente_id, situacao_cadastro):
    # Normaliza o status do cadastro (Tratamento completo -> Tratamento Completo)
    situacao_cadastro = str(situacao_cadastro).replace("completo", "Completo")
    
    if not df_evolucoes.empty:
        col_id_evo = "Cns_Cpf (Id)" if "Cns_Cpf (Id)" in df_evolucoes.columns else "Cns_Cpf"
        evos = df_evolucoes[df_evolucoes[col_id_evo].astype(str) == str(paciente_id)]
        if not evos.empty:
            # Pega o status da evolução mais recente (última linha salva no Google)
            ultima_situacao = evos.iloc[-1].get("Nova Situação", situacao_cadastro)
            return str(ultima_situacao).replace("completo", "Completo")
            
    return situacao_cadastro

if not df_pacientes.empty:
    col_id_pac = "Cns_Cpf (Id)" if "Cns_Cpf (Id)" in df_pacientes.columns else "Cns_Cpf"
    # Atualiza a coluna de Situação para ser dinâmica baseada na evolução
    df_pacientes["Situação Atual"] = df_pacientes.apply(
        lambda row: obter_situacao_real(row[col_id_pac], row.get("Situação Atual", "Em andamento")), axis=1
    )

# ==========================================
# 3. INTERFACE E KPIs
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Bras%C3%A3o_de_Nova_Igua%C3%A7u.svg/1200px-Bras%C3%A3o_de_Nova_Igua%C3%A7u.svg.png", width=150)
if st.sidebar.button("🔄 Sincronizar Agora", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.title("🩺 Painel Gerencial - ILTB Nova Iguaçu")

if not df_pacientes.empty:
    total = len(df_pacientes)
    em_andamento = len(df_pacientes[df_pacientes["Situação Atual"] == "Em andamento"])
    interrupcoes = len(df_pacientes[df_pacientes["Situação Atual"] == "Interrupção"])
    # Conta tanto "Tratamento completo" quanto "Tratamento Completo"
    concluidos = len(df_pacientes[df_pacientes["Situação Atual"] == "Tratamento Completo"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Notificações", total)
    c2.metric("Em Andamento", em_andamento)
    c3.metric("Interrupções", interrupcoes, delta_color="inverse")
    c4.metric("Tratamento Completo", concluidos)

    aba1, aba2 = st.tabs(["👤 Prontuário", "📊 Epidemiologia"])

    with aba1:
        col_id = "Cns_Cpf (Id)" if "Cns_Cpf (Id)" in df_pacientes.columns else "Cns_Cpf"
        col_nome = "Nome de Registro" if "Nome de Registro" in df_pacientes.columns else "Nome Do Paciente"
        df_pacientes["Busca"] = df_pacientes[col_nome].astype(str) + " - ID: " + df_pacientes[col_id].astype(str)
        
        escolha = st.selectbox("Buscar Paciente:", ["Selecione..."] + df_pacientes["Busca"].tolist())
        
        if escolha != "Selecione...":
            dados = df_pacientes[df_pacientes["Busca"] == escolha].iloc[0]
            id_pac = dados[col_id]
            sit_real = dados["Situação Atual"]
            
            st.subheader(f"Paciente: {dados[col_nome]}")
            st.markdown(f"### Status Atual: **{sit_real}**")
            
            evos_p = df_evolucoes[df_evolucoes[col_id].astype(str) == str(id_pac)].iloc[::-1] if not df_evolucoes.empty else pd.DataFrame()
            
            col_e1, col_e2 = st.columns([3, 1])
            col_e1.dataframe(evos_p, hide_index=True)
            
            with col_e2:
                pdf_b = gerar_pdf_prontuario(dados, evos_p, sit_real)
                st.download_button("📄 Baixar PDF", pdf_b, f"Prontuario_{id_pac}.pdf", "application/pdf")

    with aba2:
        fig = px.pie(df_pacientes, names="Situação Atual", title="Distribuição Real dos Tratamentos", hole=0.3)
        st.plotly_chart(fig)
else:
    st.warning("Nenhum dado encontrado.")
