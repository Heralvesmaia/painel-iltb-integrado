import streamlit as st
import pandas as pd
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SIG-ILTB - Prontuário Eletrônico", layout="wide", page_icon="🔒")

# 2. CENTRAL DE ACESSOS
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

# 4. PAINEL PRINCIPAL
if tela_login():
    
    # CSS básico apenas para cores de fundo
    st.markdown("""
        <style>
        .main { background-color: #f4f6f9; }
        </style>
        """, unsafe_allow_html=True)

    nome_unidade_atual = USUARIOS[st.session_state['usuario_atual']]["nome_oficial"]

    st.title("🏥 Prontuário Digital SIG-ILTB")
    st.caption(f"Unidade Ativa: {nome_unidade_atual}" if st.session_state['usuario_atual'] != 'heraldo_admin' else "Visão Geral - Administração Central")

    SHEET_ID = "1cG2uey69Vb2nnu_n-m5VTEwKuAnvCs2OkaQIvN7Izs8"
    
    # COLE O SEU LINK DO GOOGLE FORMS DE EVOLUÇÃO AQUI:
    LINK_FORM_EVOLUCAO = "https://docs.google.com/forms/d/e/COLE_SEU_LINK_AQUI/viewform"

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1085/1085810.png", width=80)
        st.markdown(f"**Logado como:** {st.session_state['usuario_atual']}")
        if st.button('🔄 ATUALIZAR DADOS', use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        if st.button('🚪 SAIR DO SISTEMA', use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

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
        if st.session_state['usuario_atual'] != 'heraldo_admin':
            col_unidade = next((col for col in df_pacientes.columns if 'unidade' in col.lower() or 'local' in col.lower()), None)
            if col_unidade:
                df_pacientes = df_pacientes[df_pacientes[col_unidade].astype(str).str.contains(nome_unidade_atual, case=False, na=False)]

        col_nome_p = next((c for c in df_pacientes.columns if 'nome' in c.lower() or 'paciente' in c.lower()), df_pacientes.columns[1])

        tab_prontuario, tab_pacientes, tab_evolucoes = st.tabs(["🩺 Prontuário Longitudinal", "📋 Lista de Pacientes", "📈 Base Global"])
        
        # ==========================================
        # ABA 1: PRONTUÁRIO LONGITUDINAL (CORRIGIDO)
        # ==========================================
        with tab_prontuario:
            st.markdown("### 🔍 Busca de Prontuário")
            lista_pacientes = ["Selecione um paciente..."] + sorted(df_pacientes[col_nome_p].dropna().astype(str).unique().tolist())
            paciente_selecionado = st.selectbox("Busque o paciente para iniciar a evolução:", lista_pacientes, label_visibility="collapsed")

            if paciente_selecionado != "Selecione um paciente...":
                d_pac = df_pacientes[df_pacientes[col_nome_p] == paciente_selecionado].iloc[0]
                
                # Extratores Inteligentes
                c_cns = next((c for c in df_pacientes.columns if 'cns' in c.lower() or 'cartão' in c.lower()), None)
                c_cpf = next((c for c in df_pacientes.columns if 'cpf' in c.lower()), None)
                c_sit = next((c for c in df_pacientes.columns if 'situa' in c.lower() or 'encerra' in c.lower()), None)
                c_esq = next((c for c in df_pacientes.columns if 'esquema' in c.lower() or 'medicamento' in c.lower()), None)
                c_pos = next((c for c in df_pacientes.columns if 'posologia' in c.lower()), None)
                c_ini = next((c for c in df_pacientes.columns if 'início' in c.lower() or 'inicio' in c.lower()), None)
                c_ter = next((c for c in df_pacientes.columns if 'término' in c.lower() or 'termino' in c.lower()), None)
                c_pro = next((c for c in df_pacientes.columns if 'próxima' in c.lower() or 'retorno' in c.lower()), None)
                
                val_cns = str(d_pac[c_cns]) if c_cns and pd.notna(d_pac[c_cns]) else "Não informado"
                val_cpf = str(d_pac[c_cpf]) if c_cpf and pd.notna(d_pac[c_cpf]) else "Não informado"
                val_sit = str(d_pac[c_sit]) if c_sit and pd.notna(d_pac[c_sit]) else "Em andamento"
                
                # ----------------------------------------------------
                # FICHA DE IDENTIFICAÇÃO (NATIVA STREAMLIT - SEM ERROS DE HTML)
                # ----------------------------------------------------
                st.markdown("---")
                with st.container(border=True):
                    # Cabeçalho Principal
                    st.markdown(f"### 👤 {str(d_pac[col_nome_p]).upper()}")
                    st.markdown(f"**CNS:** {val_cns} &nbsp;&nbsp;|&nbsp;&nbsp; **CPF:** {val_cpf}")
                    
                    st.divider()
                    
                    # Colunas de Dados
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Início TPT:** {str(d_pac[c_ini]) if c_ini and pd.notna(d_pac[c_ini]) else '-'}")
                        st.markdown(f"**Tratamento (Esquema):** {str(d_pac[c_esq]) if c_esq and pd.notna(d_pac[c_esq]) else '-'}")
                        st.markdown(f"**Posologia:** {str(d_pac[c_pos]) if c_pos and pd.notna(d_pac[c_pos]) else '-'}")
                    with c2:
                        st.markdown(f"**Término Previsto:** {str(d_pac[c_ter]) if c_ter and pd.notna(d_pac[c_ter]) else '-'}")
                        st.markdown(f"**Próxima Consulta:** {str(d_pac[c_pro]) if c_pro and pd.notna(d_pac[c_pro]) else '-'}")
                        
                        # Alertas Coloridos de Acordo com a Situação
                        sit_lower = val_sit.lower()
                        if 'óbito' in sit_lower or 'obito' in sit_lower:
                            st.error(f"**Situação:** {val_sit}")
                        elif 'alta' in sit_lower or 'completo' in sit_lower or 'cura' in sit_lower:
                            st.success(f"**Situação:** {val_sit}")
                        elif 'interrup' in sit_lower or 'abandono' in sit_lower or 'adversa' in sit_lower:
                            st.warning(f"**Situação:** {val_sit}")
                        else:
                            st.info(f"**Situação:** {val_sit}")
                # ----------------------------------------------------

                # BOTÃO DE AÇÃO: ADICIONAR EVOLUÇÃO
                with st.expander("➕ Adicionar Evolução Diária / Mensal", expanded=False):
                    st.info("Para registar o atendimento de hoje, preencha o formulário oficial. Os dados aparecerão na linha do tempo abaixo assim que atualizar a página.")
                    st.link_button("📝 Preencher Evolução do Paciente", LINK_FORM_EVOLUCAO, use_container_width=True)

                # LINHA DO TEMPO (HISTÓRICO) NATIVA DO STREAMLIT
                st.markdown("### 🗓️ Histórico Longitudinal de Evoluções")
                
                if df_evolucoes is not None and not df_evolucoes.empty:
                    col_nome_e = next((c for c in df_evolucoes.columns if 'nome' in c.lower() or 'paciente' in c.lower()), df_evolucoes.columns[1])
                    hist_pac = df_evolucoes[df_evolucoes[col_nome_e].astype(str) == paciente_selecionado]
                    
                    if not hist_pac.empty:
                        ce_data = next((c for c in hist_pac.columns if 'data' in c.lower() or 'carimbo' in c.lower()), None)
                        ce_tipo = next((c for c in hist_pac.columns if 'tipo' in c.lower() or 'mês' in c.lower() or 'mes' in c.lower()), None)
                        ce_peso = next((c for c in hist_pac.columns if 'peso' in c.lower()), None)
                        ce_sit = next((c for c in hist_pac.columns if 'situa' in c.lower() or 'tratamento' in c.lower()), None)
                        ce_prox = next((c for c in hist_pac.columns if 'próxima' in c.lower() or 'retorno' in c.lower()), None)
                        ce_relato = next((c for c in hist_pac.columns if 'adesão' in c.lower() or 'queixa' in c.lower() or 'relato' in c.lower()), None)
                        ce_cond = next((c for c in hist_pac.columns if 'conduta' in c.lower()), None)

                        # Inverte para mostrar a consulta mais recente no topo
                        hist_pac = hist_pac.iloc[::-1]

                        for _, row in hist_pac.iterrows():
                            r_data = str(row[ce_data]) if ce_data and pd.notna(row[ce_data]) else "Data não inf."
                            r_tipo = str(row[ce_tipo]) if ce_tipo and pd.notna(row[ce_tipo]) else "Rotina"
                            r_peso = str(row[ce_peso]) if ce_peso and pd.notna(row[ce_peso]) else "-"
                            r_sit = str(row[ce_sit]) if ce_sit and pd.notna(row[ce_sit]) else "-"
                            r_prox = str(row[ce_prox]) if ce_prox and pd.notna(row[ce_prox]) else "-"
                            r_relato = str(row[ce_relato]) if ce_relato and pd.notna(row[ce_relato]) else "Sem relatos."
                            r_cond = str(row[ce_cond]) if ce_cond and pd.notna(row[ce_cond]) else "Sem conduta registada."

                            # Cartão de Evolução Nativo (Sem risco de vazar HTML)
                            with st.container(border=True):
                                st.markdown(f"#### 📅 {r_data} | {r_tipo}")
                                st.markdown(f"**Situação:** {r_sit} &nbsp;&nbsp;|&nbsp;&nbsp; **Peso:** {r_peso} kg &nbsp;&nbsp;|&nbsp;&nbsp; **Próx. Consulta:** {r_prox}")
                                st.markdown(f"**Adesão, Queixas e Tolerância:**<br>{r_relato}", unsafe_allow_html=True)
                                st.markdown(f"**Conduta Médica/Enfermagem:**<br>{r_cond}", unsafe_allow_html=True)
                    else:
                        st.info("Nenhuma evolução diária ou mensal registada até o momento.")
                else:
                    st.warning("Base de evoluções vazia ou desconectada.")

        with tab_pacientes:
            st.dataframe(df_pacientes, use_container_width=True, hide_index=True)
            
        with tab_evolucoes:
            if df_evolucoes is not None:
                st.dataframe(df_evolucoes, use_container_width=True, hide_index=True)
    else:
        st.error("⚠️ Nenhum dado de paciente encontrado para a sua unidade.")
