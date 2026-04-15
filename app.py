import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SIG-ILTB Nova Iguaçu", layout="wide", page_icon="📊")

# 2. ENDEREÇOS DA PLANILHA (IDs que você forneceu)
SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"
URL_PACIENTES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes"
URL_EVOLUCOES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes"

# Título e Estilo
st.title("📊 Painel de Monitoramento SIG-ILTB")
st.markdown("### Vigilância Epidemiológica - Nova Iguaçu")

# 3. FUNÇÃO PARA CARREGAR DADOS COM BOTÃO DE ATUALIZAÇÃO FORÇADA
def carregar_dados():
    try:
        # Lendo abas
        df_p = pd.read_csv(URL_PACIENTES)
        df_e = pd.read_csv(URL_EVOLUCOES)
        return df_p, df_e
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return None, None

# Botão para limpar o cache e ver dados novos na hora
if st.sidebar.button('🔄 Atualizar Dados Agora'):
    st.cache_data.clear()
    st.rerun()

df_p, df_e = carregar_dados()

if df_p is not None:
    # 4. TRATAMENTO DE COLUNAS (Remover espaços e garantir nomes)
    df_p.columns = [c.strip() for c in df_p.columns]
    
    # 5. MÉTRICAS NO TOPO
    c1, c2, c3 = st.columns(3)
    total_pacientes = len(df_p)
    ativos = len(df_p[df_p['Situação Atual'] == 'Em andamento'])
    interrompidos = len(df_p[df_p['Situação Atual'] == 'Interrupção do tratamento'])
    
    c1.metric("Total Notificado", total_pacientes)
    c2.metric("Em Tratamento", ativos)
    c3.metric("Interrupções (Busca Ativa)", interrompidos, delta_color="inverse")

    # 6. FILTROS LATERAIS
    st.sidebar.divider()
    st.sidebar.header("Filtros")
    unidades = df_p['Unidade de Tratamento'].unique()
    sel_unid = st.sidebar.multiselect("Filtrar por Unidade", unidades)
    
    if sel_unid:
        df_p = df_p[df_p['Unidade de Tratamento'].isin(sel_unid)]

    # 7. ABAS DE VISUALIZAÇÃO
    tab1, tab2 = st.tabs(["📋 Lista de Pacientes", "📈 Histórico de Evoluções"])
    
    with tab1:
        st.write(f"Exibindo {len(df_p)} registros")
        st.dataframe(df_p, use_container_width=True)
        
    with tab2:
        if df_e is not None and not df_e.empty:
            st.write("Evoluções registradas no Prontuário")
            st.dataframe(df_e, use_container_width=True)
        else:
            st.info("Nenhuma evolução clínica registrada ainda.")
else:
    st.warning("Verifique se a planilha está compartilhada como 'Qualquer pessoa com o link pode ler'.")
