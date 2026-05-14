import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Gestão ILTB - Nova Iguaçu", page_icon="🩺", layout="wide")

# ==========================================
# 1. CONEXÃO COM O BANCO DE DADOS (GOOGLE)
# ==========================================
# ⚠️ ATENÇÃO: Cole a sua URL real do Google Apps Script (terminada em /exec) abaixo:
API_URL = "https://script.google.com/macros/s/AKfycbyTyHorAMicNY7lNO6cVWG-pyAe03pTR8obS3NGOGDlZxXY-eS5Jt2O9Y4gzxtGW-a3rg/exec"

@st.cache_data(ttl=60) # Atualiza os dados a cada 60 segundos
def carregar_dados():
    try: 
        response = requests.get(f"{API_URL}?read=true")
        if response.status_code == 200:
            dados = response.json()
            df_pacientes = pd.DataFrame(dados.get("pacientes", []))
            df_evolucoes = pd.DataFrame(dados.get("evolucoes", []))
            return df_pacientes, df_evolucoes
        else:
            st.error("Erro ao conectar com o Google Sheets. Verifique a URL.")
            return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Falha na conexão: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Carregando os dados da nuvem
df_pacientes, df_evolucoes = carregar_dados()

# ==========================================
# 2. VERIFICAÇÃO DE SEGURANÇA E LIMPEZA
# ==========================================
if df_pacientes.empty:
    st.warning("Nenhum paciente cadastrado ou aguardando sincronização com o banco de dados.")
    st.stop()

# Garantindo que a coluna de ID seja texto para não quebrar a busca
if "Cns_Cpf (Id)" in df_pacientes.columns:
    df_pacientes["Cns_Cpf (Id)"] = df_pacientes["Cns_Cpf (Id)"].fillna("S/N").astype(str)
else:
    df_pacientes["Cns_Cpf (Id)"] = "S/N"

# Corrigindo o erro KeyError: Agora busca pelo novo nome "Nome de Registro"
if "Nome de Registro" in df_pacientes.columns:
    df_pacientes["Busca"] = df_pacientes["Nome de Registro"].astype(str) + " - ID: " + df_pacientes["Cns_Cpf (Id)"]
else:
    st.error("A coluna 'Nome de Registro' não foi encontrada na Planilha Google. Verifique os cabeçalhos!")
    st.stop()

# ==========================================
# 3. INTERFACE LATERAL (FILTROS)
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Bras%C3%A3o_de_Nova_Igua%C3%A7u.svg/1200px-Bras%C3%A3o_de_Nova_Igua%C3%A7u.svg.png", width=150)
st.sidebar.title("Filtros Gerenciais")

# Filtro inteligente de unidades (pega só as que têm pacientes)
if "Unidade de Saúde" in df_pacientes.columns:
    unidades_disponiveis = ["Todas"] + sorted(df_pacientes["Unidade de Saúde"].dropna().unique().tolist())
    unidade_selecionada = st.sidebar.selectbox("Filtrar por Unidade de Saúde", unidades_disponiveis)

    if unidade_selecionada != "Todas":
        df_pacientes = df_pacientes[df_pacientes["Unidade de Saúde"] == unidade_selecionada]

# ==========================================
# 4. CARTÕES DE INDICADORES (KPIs)
# ==========================================
st.title("🩺 Painel Gerencial - ILTB Nova Iguaçu")

# Prevenindo erros caso a coluna "Situação Atual" falte
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

# ------------------------------------------
# ABA 1: VISÃO DO PACIENTE (PRONTUÁRIO)
# ------------------------------------------
with aba1:
    st.subheader("Busca Rápida de Pacientes")
    paciente_selecionado = st.selectbox("Digite o Nome, CNS ou CPF do paciente:", ["Selecione um paciente..."] + df_pacientes["Busca"].tolist())
    
    if paciente_selecionado != "Selecione um paciente...":
        # Extraindo os dados do paciente selecionado
        dados_paciente = df_pacientes[df_pacientes["Busca"] == paciente_selecionado].iloc[0]
        paciente_id = dados_paciente["Cns_Cpf (Id)"]
        
        # Cabeçalho do Prontuário
        st.markdown(f"### {dados_paciente.get('Nome de Registro', 'Nome não informado')}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.write(f"**Data de Nasc:** {dados_paciente.get('Nascimento', '-')}")
        c2.write(f"**Idade:** {dados_paciente.get('Idade', '-')}")
        c3.write(f"**Sexo:** {dados_paciente.get('Sexo', '-')}")
        c4.write(f"**Telefone:** {dados_paciente.get('Telefone', '-')}")
        
        st.write(f"**Unidade de Acompanhamento:** {dados_paciente.get('Unidade de Saúde', '-')}")
        
        # Bloco de Tratamento
        st.info(f"**ESQUEMA E POSOLOGIA:** {dados_paciente.get('Medicamento', '-')} | {dados_paciente.get('Posologia', '-')}")
        
        c_t1, c_t2, c_t3 = st.columns(3)
        c_t1.write(f"**Início TPT:** {dados_paciente.get('Data Início TPT', '-')}")
        c_t2.write(f"**Término Previsto:** {dados_paciente.get('Término Previsto', '-')}")
        
        # Cor de destaque para a situação
        sit = dados_paciente.get('Situação Atual', '-')
        cor_sit = "green" if sit == "Tratamento completo" else "red" if sit == "Interrupção" else "orange"
        c_t3.markdown(f"**Situação Atual:** <span style='color:{cor_sit}; font-weight:bold;'>{sit}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Histórico de Evoluções
        st.subheader("📋 Histórico de Evoluções e Curva de Peso")
        
        if not df_evolucoes.empty and "Cns_Cpf (Id)" in df_evolucoes.columns:
            # Filtra evoluções pelo ID exato do paciente, convertendo ambos para string para garantir o match
            df_evolucoes["Cns_Cpf (Id)"] = df_evolucoes["Cns_Cpf (Id)"].astype(str)
            evos_paciente = df_evolucoes[df_evolucoes["Cns_Cpf (Id)"] == str(paciente_id)]
            
            if not evos_paciente.empty:
                # Tenta puxar as colunas exatas da aba de evoluções
                colunas_mostrar = []
                for col in ["Data Da Consulta", "Peso Corporal (kg)", "Nova Situação", "Relato Clínico", "Conduta", "Próxima Consulta"]:
                    if col in evos_paciente.columns:
                        colunas_mostrar.append(col)
                
                if colunas_mostrar:
                    # Inverte a ordem para a mais recente ficar no topo
                    st.dataframe(evos_paciente[colunas_mostrar].iloc[::-1], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(evos_paciente, use_container_width=True, hide_index=True)
            else:
                st.write("Nenhuma evolução registrada para este paciente.")
        else:
            st.write("Aba de evoluções ainda não sincronizada.")

# ------------------------------------------
# ABA 2: GRÁFICOS GERENCIAIS
# ------------------------------------------
with aba2:
    st.subheader("Visão Epidemiológica")
    
    g1, g2 = st.columns(2)
    
    with g1:
        # Gráfico de Situação
        contagem_sit = df_pacientes["Situação Atual"].value_counts().reset_index()
        contagem_sit.columns = ["Situação", "Quantidade"]
        fig_sit = px.pie(contagem_sit, names="Situação", values="Quantidade", title="Distribuição por Status de Tratamento", hole=0.4)
        st.plotly_chart(fig_sit, use_container_width=True)
        
    with g2:
        # Gráfico por Esquema Medicamentoso
        if "Medicamento" in df_pacientes.columns:
            contagem_med = df_pacientes["Medicamento"].value_counts().reset_index()
            contagem_med.columns = ["Esquema", "Quantidade"]
            fig_med = px.bar(contagem_med, x="Esquema", y="Quantidade", title="Tratamentos por Esquema (Medicamento)", text="Quantidade", color="Esquema")
            st.plotly_chart(fig_med, use_container_width=True)
        else:
            st.info("Coluna de 'Medicamento' não encontrada para gerar o gráfico.")
        
    st.markdown("---")
    
    # Gráfico de Unidades de Saúde
    if "Unidade de Saúde" in df_pacientes.columns:
        st.write("**Volume de Pacientes por Unidade de Saúde**")
        contagem_uni = df_pacientes["Unidade de Saúde"].value_counts().reset_index()
        contagem_uni.columns = ["Unidade", "Quantidade"]
        fig_uni = px.bar(contagem_uni, y="Unidade", x="Quantidade", orientation='h', title="Pacientes Ativos por Unidade", text="Quantidade")
        fig_uni.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_uni, use_container_width=True)
