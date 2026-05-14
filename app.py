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
                        st.error("❌ Usuário ou senha incorretos. Tente novamente.")
        st.stop() 

verificar_login()

# ==========================================
# FUNÇÃO GERADORA DE PDF (PRONTUÁRIO)
# ==========================================
def gerar_pdf_prontuario(paciente, evolucoes):
    pdf = FPDF()
    pdf.add_page()
    
    # Função para evitar erro com acentuação no PDF
    def formatar_texto(texto):
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho do PDF
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, formatar_texto('SIG-ILTB NOVA IGUAÇU - PRONTUÁRIO LONGITUDINAL'), 0, 1, 'C')
    pdf.ln(5)

    # Dados do Paciente
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, formatar_texto(f"PACIENTE: {paciente.get('Nome de Registro', 'Não informado')}"), 0, 1)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, formatar_texto(f"ID (CNS/CPF): {paciente.get('Cns_Cpf (Id)', '-')}    Idade: {paciente.get('Idade', '-')}    Sexo: {paciente.get('Sexo', '-')}"), 0, 1)
    pdf.cell(0, 6, formatar_texto(f"Unidade de Acompanhamento: {paciente.get('Unidade de Saúde', '-')}"), 0, 1)
    pdf.cell(0, 6, formatar_texto(f"Data de Início TPT: {paciente.get('Data Início TPT', '-')}    Término Previsto: {paciente.get('Término Previsto', '-')}"), 0, 1)
    pdf.cell(0, 6, formatar_texto(f"Esquema: {paciente.get('Medicamento', '-')} - {paciente.get('Posologia', '-')}"), 0, 1)
    pdf.cell(0, 6, formatar_texto(f"Situação Atual: {paciente.get('Situação Atual', '-')}"), 0, 1)
    
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)

    # Evoluções
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, formatar_texto("HISTÓRICO DE EVOLUÇÕES CLÍNICAS"), 0, 1)
    
    if evolucoes.empty:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 8, formatar_texto("Nenhuma evolução registrada para este paciente até o momento."), 0, 1)
    else:
        for idx, evo in evolucoes.iterrows():
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, formatar_texto(f"Data: {evo.get('Data Da Consulta', '-')} | Situação: {evo.get('Nova Situação', '-')} | Peso: {evo.get('Peso Corporal (kg)', '-')} kg"), 0, 1)
            
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 6, formatar_texto(f"Relato Clínico: {evo.get('Relato Clínico', '-')}"))
            pdf.multi_cell(0, 6, formatar_texto(f"Conduta: {evo.get('Conduta', '-')}"))
            pdf.cell(0, 6, formatar_texto(f"Próxima Consulta Agendada: {evo.get('Próxima Consulta', '-')}"), 0, 1)
            pdf.ln(3)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 1. CONEXÃO COM O BANCO DE DADOS (GOOGLE)
# ==========================================
API_URL = "https://script.google.com/macros/s/AKfycbyTyHorAMicNY7lNO6cVWG-pyAe03pTR8obS3NGOGDlZxXY-eS5Jt2O9Y4gzxtGW-a3rg/exec"

@st.cache_data(ttl=60)
def carregar_dados():
    try: 
        response = requests.get(f"{API_URL}?read=true", allow_redirects=True)
        if response.status_code == 200:
            try:
                dados = response.json()
            except ValueError:
                st.error("🚨 BLOQUEIO DO GOOGLE: A URL retornou uma página de login.")
                return pd.DataFrame(), pd.DataFrame()
                
            df_pacientes = pd.DataFrame(dados.get("pacientes", []))
            df_evolucoes = pd.DataFrame(dados.get("evolucoes", []))
            return df_pacientes, df_evolucoes
        else:
            return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

df_pacientes, df_evolucoes = carregar_dados()

# ==========================================
# 2. VERIFICAÇÃO DE SEGURANÇA E LIMPEZA
# ==========================================
if df_pacientes.empty:
    st.warning("Nenhum paciente cadastrado ou aguardando sincronização com o banco de dados.")
    
    # Botão de atualizar caso esteja vazio
    if st.button("🔄 Sincronizar Agora"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

coluna_id = "Cns_Cpf (Id)" if "Cns_Cpf (Id)" in df_pacientes.columns else "Cns_Cpf" if "Cns_Cpf" in df_pacientes.columns else None

if coluna_id:
    df_pacientes[coluna_id] = df_pacientes[coluna_id].fillna("S/N").astype(str)
else:
    df_pacientes["Cns_Cpf_Temp"] = "S/N"
    coluna_id = "Cns_Cpf_Temp"

coluna_nome = "Nome de Registro" if "Nome de Registro" in df_pacientes.columns else "Nome Do Paciente" if "Nome Do Paciente" in df_pacientes.columns else None

if coluna_nome:
    df_pacientes["Busca"] = df_pacientes[coluna_nome].astype(str) + " - ID: " + df_pacientes[coluna_id]
else:
    st.error("A coluna de Nome não foi encontrada na Planilha Google.")
    st.stop()

# ==========================================
# 3. INTERFACE LATERAL (FILTROS)
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Bras%C3%A3o_de_Nova_Igua%C3%A7u.svg/1200px-Bras%C3%A3o_de_Nova_Igua%C3%A7u.svg.png", width=150)
st.sidebar.title("Bem-vindo, Administrador!")

# BOTÃO DE ATUALIZAR MANUALMENTE
if st.sidebar.button("🔄 Sincronizar Agora", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros Gerenciais")

if "Unidade de Saúde" in df_pacientes.columns:
    unidades_disponiveis = ["Todas"] + sorted(df_pacientes["Unidade de Saúde"].dropna().unique().tolist())
    unidade_selecionada = st.sidebar.selectbox("Filtrar por Unidade de Saúde", unidades_disponiveis)

    if unidade_selecionada != "Todas":
        df_pacientes = df_pacientes[df_pacientes["Unidade de Saúde"] == unidade_selecionada]

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair do Sistema"):
    st.session_state["autenticado"] = False
    st.rerun()

# ==========================================
# 4. CARTÕES DE INDICADORES (KPIs)
# ==========================================
st.title("🩺 Painel Gerencial - ILTB Nova Iguaçu")

if "Situação Atual" not in df_pacientes.columns:
    df_pacientes["Situação Atual"] = "Sem informação"

total_pacientes = len(df_pacientes)
em_andamento = len(df_pacientes[df_pacientes["Situação Atual"] == "Em andamento"])
interrupcoes = len(df_pacientes[df_pacientes["Situação Atual"] == "Interrupção"])
altas = len(df_pacientes[df_pacientes["Situação Atual"] == "Tratamento completo"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Notificações", total_pacientes)
col2.metric("Tratamentos em Andamento", em_andamento)
col3.metric("Interrupções (Alerta)", interrupcoes, delta_color="inverse")
col4.metric("Tratamentos Completos", altas)

st.markdown("---")

# ==========================================
# 5. ABAS PRINCIPAIS (PRONTUÁRIO E GRÁFICOS)
# ==========================================
aba1, aba2 = st.tabs(["👤 Visão do Paciente (Prontuário)", "📊 Gráficos Epidemiológicos"])

with aba1:
    st.subheader("Busca Rápida de Pacientes")
    paciente_selecionado = st.selectbox("Digite o Nome, CNS ou CPF do paciente:", ["Selecione um paciente..."] + df_pacientes["Busca"].tolist())
    
    if paciente_selecionado != "Selecione um paciente...":
        dados_paciente = df_pacientes[df_pacientes["Busca"] == paciente_selecionado].iloc[0]
        paciente_id = dados_paciente[coluna_id]
        
        st.markdown(f"### {dados_paciente.get(coluna_nome, 'Nome não informado')}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.write(f"**Data de Nasc:** {dados_paciente.get('Nascimento', '-')}")
        c2.write(f"**Idade:** {dados_paciente.get('Idade', '-')}")
        c3.write(f"**Sexo:** {dados_paciente.get('Sexo', '-')}")
        c4.write(f"**Telefone:** {dados_paciente.get('Telefone', '-')}")
        
        st.write(f"**Unidade de Acompanhamento:** {dados_paciente.get('Unidade de Saúde', '-')}")
        st.info(f"**ESQUEMA E POSOLOGIA:** {dados_paciente.get('Medicamento', '-')} | {dados_paciente.get('Posologia', '-')}")
        
        c_t1, c_t2, c_t3 = st.columns(3)
        c_t1.write(f"**Início TPT:** {dados_paciente.get('Data Início TPT', '-')}")
        c_t2.write(f"**Término Previsto:** {dados_paciente.get('Término Previsto', '-')}")
        
        sit = dados_paciente.get('Situação Atual', '-')
        cor_sit = "green" if sit == "Tratamento completo" else "red" if sit == "Interrupção" else "orange"
        c_t3.markdown(f"**Situação Atual:** <span style='color:{cor_sit}; font-weight:bold;'>{sit}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # --- BLOCO DE EVOLUÇÕES E PDF ---
        col_evo1, col_evo2 = st.columns([3, 1])
        col_evo1.subheader("📋 Histórico de Evoluções")
        
        evos_paciente = pd.DataFrame()
        
        if not df_evolucoes.empty:
            col_id_evo = "Cns_Cpf (Id)" if "Cns_Cpf (Id)" in df_evolucoes.columns else "Cns_Cpf" if "Cns_Cpf" in df_evolucoes.columns else None
            
            if col_id_evo:
                df_evolucoes[col_id_evo] = df_evolucoes[col_id_evo].astype(str)
                evos_paciente = df_evolucoes[df_evolucoes[col_id_evo] == str(paciente_id)]
                
                if not evos_paciente.empty:
                    # Inverte para mostrar as mais recentes primeiro
                    evos_paciente = evos_paciente.iloc[::-1]
                    colunas_mostrar = [col for col in ["Data Da Consulta", "Peso Corporal (kg)", "Nova Situação", "Relato Clínico", "Conduta", "Próxima Consulta"] if col in evos_paciente.columns]
                    
                    if colunas_mostrar:
                        st.dataframe(evos_paciente[colunas_mostrar], hide_index=True)
                    else:
                        st.dataframe(evos_paciente, hide_index=True)
                else:
                    st.write("Nenhuma evolução registrada para este paciente.")
        else:
            st.write("Aba de evoluções ainda não sincronizada.")
            
        # BOTÃO GERAR PDF
        with col_evo2:
            pdf_bytes = gerar_pdf_prontuario(dados_paciente, evos_paciente)
            nome_arquivo = f"Prontuario_{str(paciente_id).replace('.', '').replace('-', '')}.pdf"
            
            st.download_button(
                label="📄 Baixar PDF do Prontuário",
                data=pdf_bytes,
                file_name=nome_arquivo,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

with aba2:
    st.subheader("Visão Epidemiológica")
    
    g1, g2 = st.columns(2)
    
    with g1:
        contagem_sit = df_pacientes["Situação Atual"].value_counts().reset_index()
        contagem_sit.columns = ["Situação", "Quantidade"]
        fig_sit = px.pie(contagem_sit, names="Situação", values="Quantidade", title="Distribuição por Status de Tratamento", hole=0.4)
        st.plotly_chart(fig_sit)
        
    with g2:
        if "Medicamento" in df_pacientes.columns:
            contagem_med = df_pacientes["Medicamento"].value_counts().reset_index()
            contagem_med.columns = ["Esquema", "Quantidade"]
            fig_med = px.bar(contagem_med, x="Esquema", y="Quantidade", title="Tratamentos por Esquema", text="Quantidade", color="Esquema")
            st.plotly_chart(fig_med)
        
    st.markdown("---")
    
    if "Unidade de Saúde" in df_pacientes.columns:
        st.write("**Volume de Pacientes por Unidade de Saúde**")
        contagem_uni = df_pacientes["Unidade de Saúde"].value_counts().reset_index()
        contagem_uni.columns = ["Unidade", "Quantidade"]
        fig_uni = px.bar(contagem_uni, y="Unidade", x="Quantidade", orientation='h', title="Pacientes Ativos por Unidade", text="Quantidade")
        fig_uni.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_uni)
