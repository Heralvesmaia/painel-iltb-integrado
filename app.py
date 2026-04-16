import streamlit as st
import pandas as pd
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SIG-ILTB - Prontuário Eletrônico", layout="wide", page_icon="🔒")

# 2. CENTRAL DE ACESSOS (SUA LISTA OFICIAL)
USUARIOS = {
    "heraldo_admin": {"senha": "admin123", "nome_oficial": "TODAS"},
    "ist_hgni": {"senha": "ist_hgni", "nome_oficial": "AMBULATORIO DE IST DO HGNI"},
    "cav_mulher": {"senha": "cav_mulher", "nome_oficial": "CENTRO DE APOIO E VALORIZAÇÃO DA MULHER (CAV MULHER)"},
    "cta_vasco": {"senha": "cta_vasco", "nome_oficial": "CENTRO DE SAÚDE VASCO BARCELOS - CTA"},
    "hgni_pep": {"senha": "hgni_pep", "nome_oficial": "HOSPITAL GERAL DE NOVA IGUAÇU (HGNI) - PEP"},
    "mat_mariana": {"senha": "mat_mariana", "nome_oficial": "MATERNIDADE MARIANA BULHÕES"},
    "cf_carlinhos": {"senha": "cf_carlinhos", "nome_oficial": "CLÍNICA DA FAMÍLIA 24h CARLINHOS DA TINGUÁ (MIGUEL COUTO)"},
    "cf_gisele": {"senha": "cf_gisele", "nome_oficial": "CLÍNICA DA FAMÍLIA 24h GISELE PALHARES (VILA DE CAVA)"},
    "cf_adrianopolis": {"senha": "cf_adrianopolis", "nome_oficial": "CLÍNICA DA FAMÍLIA ADRIANÓPOLIS"},
    "cf_alianca": {"senha": "cf_alianca", "nome_oficial": "CLÍNICA DA FAMÍLIA ALIANÇA"},
    "cf_corumba": {"senha": "cf_corumba", "nome_oficial": "CLÍNICA DA FAMÍLIA CORUMBÁ"},
    "cf_ceramica": {"senha": "cf_ceramica", "nome_oficial": "CLÍNICA DA FAMÍLIA DA CERÂMICA"},
    "cf_dombosco": {"senha": "cf_dombosco", "nome_oficial": "CLÍNICA DA FAMÍLIA DOM BOSCO"},
    "cf_ambai": {"senha": "cf_ambai", "nome_oficial": "CLÍNICA DA FAMÍLIA DR MARCO POLO DE GOUVEIA PEREIRA (AMBAÍ)"},
    "cf_delmo": {"senha": "cf_delmo", "nome_oficial": "CLINICA DA FAMILIA Dr. DELMO MOURA SA"},
    "cf_emilia": {"senha": "cf_emilia", "nome_oficial": "CLÍNICA DA FAMÍLIA EMILIA GOMES - CTA"},
    "cf_cacuia": {"senha": "cf_cacuia", "nome_oficial": "CLÍNICA DA FAMÍLIA ERALDO SARDINHA (CACUIA)"},
    "cf_figueira": {"senha": "cf_figueira", "nome_oficial": "CLÍNICA DA FAMÍLIA FIGUEIRA"},
    "cf_ivo": {"senha": "cf_ivo", "nome_oficial": "CLINICA DA FAMILIA IVO MANOEL LOPES"},
    "cf_jaceruba": {"senha": "cf_jaceruba", "nome_oficial": "CLÍNICA DA FAMÍLIA JACERUBA"},
    "cf_palmares": {"senha": "cf_palmares", "nome_oficial": "CLÍNICA DA FAMÍLIA JARDIM  PALMARES"},
    "cf_viga": {"senha": "cf_viga", "nome_oficial": "CLÍNICA DA FAMÍLIA JARDIM DA VIGA"},
    "cf_iguacu": {"senha": "cf_iguacu", "nome_oficial": "CLÍNICA DA FAMÍLIA JARDIM IGUAÇU"},
    "cf_jasmim": {"senha": "cf_jasmim", "nome_oficial": "CLÍNICA DA FAMÍLIA JARDIM JASMIM"},
    "cf_roma": {"senha": "cf_roma", "nome_oficial": "CLÍNICA DA FAMÍLIA JARDIM ROMA"},
    "cf_caicara": {"senha": "cf_caicara", "nome_oficial": "CLÍNICA DA FAMÍLIA JOSÉ RODRIGUES DA SILVA (CAIÇARA)"},
    "cf_km32": {"senha": "cf_km32", "nome_oficial": "CLÍNICA DA FAMÍLIA KM32"},
    "cf_lagoinha": {"senha": "cf_lagoinha", "nome_oficial": "CLÍNICA DA FAMÍLIA LAGOINHA"},
    "cf_tingua": {"senha": "cf_tingua", "nome_oficial": "CLÍNICA DA FAMÍLIA MANOEL MOREIRA DE OLIVEIRA (TINGUÁ)"},
    "cf_marfel": {"senha": "cf_marfel", "nome_oficial": "CLÍNICA DA FAMÍLIA MARFEL"},
    "cf_boaesperanca": {"senha": "cf_boaesperanca", "nome_oficial": "CLÍNICA DA FAMÍLIA MARIA UMBELINA (BOA ESPERANÇA)"},
    "cf_geneciano": {"senha": "cf_geneciano", "nome_oficial": "CLÍNICA DA FAMÍLIA NÁDIA SILVA DE OLIVEIRA (GENECIANO)"},
    "cf_novaera": {"senha": "cf_novaera", "nome_oficial": "CLÍNICA DA FAMILIA NOVA ERA"},
    "cf_odiceia": {"senha": "cf_odiceia", "nome_oficial": "CLINICA DA FAMÍLIA ODICEIA MORAES"},
    "cf_palmeiras": {"senha": "cf_palmeiras", "nome_oficial": "CLÍNICA DA FAMÍLIA PARQUE DAS PALMEIRAS"},
    "cf_novaamerica": {"senha": "cf_novaamerica", "nome_oficial": "CLÍNICA DA FAMÍLIA PASTOR IRACY MARCELINO (NOVA AMÉRICA)"},
    "cf_grama": {"senha": "cf_grama", "nome_oficial": "CLÍNICA DA FAMÍLIA PEDRO ARUME (GRAMA)"},
    "cf_riodouro": {"senha": "cf_riodouro", "nome_oficial": "CLÍNICA DA FAMÍLIA RIO D'OURO"},
    "cf_vilaoperaria": {"senha": "cf_vilaoperaria", "nome_oficial": "CLÍNICA DA FAMÍLIA VILA OPERÁRIA"},
    "cnr_odiceia": {"senha": "cnr_odiceia", "nome_oficial": "CONSULTORIO NA RUA DA CLINICA ODICEIA MORAES"},
    "poli_santarita": {"senha": "poli_santarita", "nome_oficial": "POLICLÍNICA  SANTA RITA"},
    "poli_dirceu": {"senha": "poli_dirceu", "nome_oficial": "POLICLÍNICA DIRCEU DE AQUINO RAMOS"},
    "poli_domwalmor": {"senha": "poli_domwalmor", "nome_oficial": "POLICLÍNICA GERAL DE NOVA IGUAÇU (DOM WALMOR)"},
    "poli_cabucu": {"senha": "poli_cabucu", "nome_oficial": "POLICLÍNICA MANOEL B. DE ALMEIDA (CABUÇU)"},
    "super_dacyr": {"senha": "super_dacyr", "nome_oficial": "SUPERCLÍNICA DA FAMÍLIA DACYR SOARES - MORRO AGUDO"},
    "ubs_moqueta": {"senha": "ubs_moqueta", "nome_oficial": "UBS ALBERTO SOBRAL (MOQUETÁ)"},
    "ubs_austin": {"senha": "ubs_austin", "nome_oficial": "UBS AUSTIN"},
    "ubs_ceramica": {"senha": "ubs_ceramica", "nome_oficial": "UBS CERÂMICA"},
    "ubs_cobrex": {"senha": "ubs_cobrex", "nome_oficial": "UBS COBREX"},
    "ubs_paraiso": {"senha": "ubs_paraiso", "nome_oficial": "UBS JARDIM PARAÍSO (Antiga Patrícia Marinho)"},
    "ubs_santaeugenia": {"senha": "ubs_santaeugenia", "nome_oficial": "UBS JARDIM SANTA EUGÊNIA"},
    "ubs_julia": {"senha": "ubs_julia", "nome_oficial": "UBS JÚLIA TÁVORA"},
    "ubs_manoel": {"senha": "ubs_manoel", "nome_oficial": "UBS MANOEL REZENDE"},
    "ubs_montelibano": {"senha": "ubs_montelibano", "nome_oficial": "UBS MONTE LÍBANO (PROF° RUTILHES DOS SANTOS)"},
    "ubs_novabrasilia": {"senha": "ubs_novabrasilia", "nome_oficial": "UBS NOVA BRASÍLIA"},
    "ubs_prata": {"senha": "ubs_prata", "nome_oficial": "UBS PRATA"},
    "ubs_ranchofundo": {"senha": "ubs_ranchofundo", "nome_oficial": "UBS RANCHO FUNDO"},
    "ubs_santaclara": {"senha": "ubs_santaclara", "nome_oficial": "UBS SANTA CLARA DE VILA NOVA"},
    "ubs_vilajurema": {"senha": "ubs_vilajurema", "nome_oficial": "UBS VILA JUREMA"},
    "uni_pedreira": {"senha": "uni_pedreira", "nome_oficial": "UNIDADE SHOPPING DA PEDREIRA"},
    "usf_engenho": {"senha": "usf_engenho", "nome_oficial": "USF ENGENHO PEQUENO"},
    "usf_lino": {"senha": "usf_lino", "nome_oficial": "USF LINO VILELA"},
    "usf_k11": {"senha": "usf_k11", "nome_oficial": "USF PADRE MANOEL MONTEIRO (K11)"},
    "usf_palhada": {"senha": "usf_palhada", "nome_oficial": "USF PALHADA"},
    "usf_todos": {"senha": "usf_todos", "nome_oficial": "USF PARQUE TODOS OS SANTOS"},
    "usf_rodilandia": {"senha": "usf_rodilandia", "nome_oficial": "USF RODILÂNDIA"},
    "usf_guandu": {"senha": "usf_guandu", "nome_oficial": "USF SANTA CLARA DO GUANDÚ"},
    "usf_valverde": {"senha": "usf_valverde", "nome_oficial": "USF VALVERDE"},
    "usf_vilatania": {"senha": "usf_vilatania", "nome_oficial": "USF VILA TÂNIA"}
}

# 3. FUNÇÃO DE LOGIN
def tela_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<h1 style='text-align: center;'>🔐 Sistema SIG-ILTB</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Introduza as suas credenciais para aceder ao painel</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login"):
                usuario = st.text_input("Utilizador (Login da Unidade ou Admin)").lower().strip()
                senha = st.text_input("Senha", type="password").strip()
                botao_entrar = st.form_submit_button("Entrar no Sistema")
                
                if botao_entrar:
                    if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
                        st.session_state["autenticado"] = True
                        st.session_state["usuario_atual"] = usuario
                        st.success("Acesso autorizado! A carregar...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Utilizador ou senha incorretos.")
        return False
    return True

# 4. EXECUÇÃO DO PAINEL APÓS LOGIN
if tela_login():
    
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        div[data-testid="stMetric"] { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #0056b3; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .info-label { font-size: 0.85rem; color: #6c757d; margin-bottom: 0px; padding-bottom: 0px; }
        .info-value { font-size: 1.1rem; font-weight: 600; color: #212529; margin-top: 0px; padding-top: 0px; }
        </style>
        """, unsafe_allow_html=True)

    nome_unidade_atual = USUARIOS[st.session_state['usuario_atual']]["nome_oficial"]

    st.title("🏥 Prontuário Digital SIG-ILTB")
    if st.session_state['usuario_atual'] == 'heraldo_admin':
        st.caption("Visão Geral - Administração Central")
    else:
        st.caption(f"Unidade Ativa: {nome_unidade_atual}")

    SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1085/1085810.png", width=80)
        st.markdown(f"**Logado como:** {st.session_state['usuario_atual']}")
        
        if st.button('🔄 ATUALIZAR DADOS', use_container_width=True):
            st.cache_data.clear()
            st.rerun()
            
        if st.button('🚪 SAIR DO SISTEMA', use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()
            
        st.divider()
        st.caption("Nova Iguaçu - Vigilância Ativa")

    @st.cache_data(ttl=15)
    def carregar_dados_oficiais():
        try:
            agora = int(time.time())
            url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pacientes&nocache={agora}"
            url_e = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Evolucoes&nocache={agora}"
            
            df_p = pd.read_csv(url_p, on_bad_lines='skip')
            df_e = pd.read_csv(url_e, on_bad_lines='skip')
            return df_p, df_e
        except:
            return None, None

    df_pacientes, df_evolucoes = carregar_dados_oficiais()

    if df_pacientes is not None and not df_pacientes.empty:
        
        # Filtro de Unidade
        if st.session_state['usuario_atual'] != 'heraldo_admin':
            colunas_unidade = [col for col in df_pacientes.columns if 'unidade' in col.lower() or 'local' in col.lower()]
            if colunas_unidade:
                col_unidade = colunas_unidade[0]
                df_pacientes = df_pacientes[df_pacientes[col_unidade].astype(str).str.contains(nome_unidade_atual, case=False, na=False)]

        col_nome_paciente = next((c for c in df_pacientes.columns if 'nome' in c.lower() or 'paciente' in c.lower()), df_pacientes.columns[1])

        tab_prontuario, tab_pacientes, tab_evolucoes = st.tabs([
            "🩺 Prontuário Individual", 
            "📋 Tabela Geral", 
            "📈 Base de Evoluções"
        ])
        
        # ==========================================
        # ABA 1: PRONTUÁRIO DIGITAL INTELIGENTE
        # ==========================================
        with tab_prontuario:
            st.markdown("### 🔍 Busca de Paciente")
            lista_pacientes = ["Selecione um paciente..."] + sorted(df_pacientes[col_nome_paciente].dropna().astype(str).unique().tolist())
            paciente_selecionado = st.selectbox("Digite ou selecione o nome do paciente:", lista_pacientes, label_visibility="collapsed")

            if paciente_selecionado != "Selecione um paciente...":
                dados_paciente = df_pacientes[df_pacientes[col_nome_paciente] == paciente_selecionado].iloc[0]
                
                # Identificação dinâmica das colunas do Google Forms
                col_sit = next((c for c in df_pacientes.columns if 'situação' in c.lower() or 'situacao' in c.lower() or 'encerramento' in c.lower()), None)
                col_peso = next((c for c in df_pacientes.columns if 'peso' in c.lower()), None)
                col_med = next((c for c in df_pacientes.columns if 'medicamento' in c.lower() or 'esquema' in c.lower()), None)
                col_inicio = next((c for c in df_pacientes.columns if 'início' in c.lower() or 'inicio' in c.lower()), None)
                col_doses = next((c for c in df_pacientes.columns if 'doses' in c.lower() or 'tomadas' in c.lower()), None)
                col_termino = next((c for c in df_pacientes.columns if 'término' in c.lower() or 'termino' in c.lower()), None)
                col_causa = next((c for c in df_pacientes.columns if 'causa' in c.lower() or 'óbito' in c.lower() or 'justificativa' in c.lower()), None)
                
                # Extração segura dos dados
                situacao_atual = str(dados_paciente[col_sit]) if col_sit and pd.notna(dados_paciente[col_sit]) else "Em andamento"
                peso = str(dados_paciente[col_peso]) if col_peso and pd.notna(dados_paciente[col_peso]) else "Não inf."
                medicamento = str(dados_paciente[col_med]) if col_med and pd.notna(dados_paciente[col_med]) else "Não inf."
                data_inicio = str(dados_paciente[col_inicio]) if col_inicio and pd.notna(dados_paciente[col_inicio]) else "Não inf."
                doses = str(dados_paciente[col_doses]) if col_doses and pd.notna(dados_paciente[col_doses]) else "0"
                data_termino = str(dados_paciente[col_termino]) if col_termino and pd.notna(dados_paciente[col_termino]) else "Não inf."
                causa_obito = str(dados_paciente[col_causa]) if col_causa and pd.notna(dados_paciente[col_causa]) else "Não informada"
                
                st.markdown("---")
                
                # BANDEIRAS VISUAIS DE STATUS (Alertas)
                sit_lower = situacao_atual.lower()
                if 'óbito' in sit_lower or 'obito' in sit_lower:
                    st.error(f"🚨 **FICHA ENCERRADA - ÓBITO** | Causa Registada: {causa_obito}")
                elif 'completo' in sit_lower or 'alta' in sit_lower or 'cura' in sit_lower:
                    st.success(f"🏁 **TRATAMENTO COMPLETO** | Paciente recebeu alta com sucesso.")
                elif 'reação' in sit_lower or 'reacao' in sit_lower or 'adversa' in sit_lower:
                    st.warning(f"⚠️ **TRATAMENTO SUSPENSO** | Motivo: Reação adversa ao medicamento.")
                elif 'interrupção' in sit_lower or 'interrupcao' in sit_lower or 'abandono' in sit_lower:
                    st.warning(f"⚠️ **ALERTA DE BUSCA ATIVA** | Interrupção do tratamento identificada.")
                else:
                    st.info(f"🟢 **EM ANDAMENTO** | Acompanhamento ativo na unidade.")

                # CARTÃO DO PACIENTE (Novo Design Clínico)
                st.markdown("#### 👤 Dados Clínicos e Tratamento")
                with st.container(border=True):
                    # Linha 1
                    r1c1, r1c2, r1c3 = st.columns([2, 1, 2])
                    r1c1.markdown(f"<p class='info-label'>Nome do Paciente</p><p class='info-value'>{dados_paciente[col_nome_paciente]}</p>", unsafe_allow_html=True)
                    r1c2.markdown(f"<p class='info-label'>Peso Corporal</p><p class='info-value'>{peso} kg</p>", unsafe_allow_html=True)
                    r1c3.markdown(f"<p class='info-label'>Medicamento / Esquema</p><p class='info-value'>{medicamento}</p>", unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Linha 2
                    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
                    r2c1.markdown(f"<p class='info-label'>Data Início TPT</p><p class='info-value'>{data_inicio}</p>", unsafe_allow_html=True)
                    r2c2.markdown(f"<p class='info-label'>Nº Doses Tomadas</p><p class='info-value'>{doses}</p>", unsafe_allow_html=True)
                    r2c3.markdown(f"<p class='info-label'>Data Término Prevista</p><p class='info-value'>{data_termino}</p>", unsafe_allow_html=True)
                    r2c4.markdown(f"<p class='info-label'>Situação de Encerramento</p><p class='info-value'>{situacao_atual}</p>", unsafe_allow_html=True)

                # SUBFORMULÁRIO DE EVOLUÇÕES
                st.markdown("<br>#### 🗓️ Histórico de Consultas e Intercorrências", unsafe_allow_html=True)
                
                if df_evolucoes is not None and not df_evolucoes.empty:
                    col_nome_evolucao = next((c for c in df_evolucoes.columns if 'nome' in c.lower() or 'paciente' in c.lower()), df_evolucoes.columns[1])
                    historico_paciente = df_evolucoes[df_evolucoes[col_nome_evolucao].astype(str) == paciente_selecionado]
                    
                    if not historico_paciente.empty:
                        st.dataframe(historico_paciente, use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhuma consulta de acompanhamento registada para este paciente até ao momento.")
                else:
                    st.warning("A base de evoluções ainda está vazia ou a carregar.")

        # ==========================================
        # ABA 2 e 3: TABELAS GERAIS
        # ==========================================
        with tab_pacientes:
            st.markdown("### 📋 Visão Geral da Base")
            st.dataframe(df_pacientes, use_container_width=True, hide_index=True)
            
        with tab_evolucoes:
            st.markdown("### 📈 Histórico Global de Consultas")
            if df_evolucoes is not None and not df_evolucoes.empty:
                st.dataframe(df_evolucoes, use_container_width=True, hide_index=True)
            else:
                st.info("Aguardando os primeiros registos...")
    else:
        st.error("⚠️ Nenhum dado encontrado. A base está vazia ou a unidade não possui pacientes.")
