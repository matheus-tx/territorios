from datetime import datetime
import numpy as np
import streamlit as st
import plotly.express as px
import pandas as pd
import polars as pl

from utils import carregar_dados, processar_cartoes, processar_registros, processar_conclusoes
from apperance_utils import formatar_tabela, style_row_by_interval

# --- 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha) ---
st.set_page_config(
    page_title="Territórios PF",
    page_icon="📊",
    layout="wide", # Usa a tela cheia
    initial_sidebar_state="collapsed"
)

# --- 2. SEGURANÇA (Mantendo o que já funciona) ---
TOKEN_ACESSO = st.secrets["meu_token"]
if st.query_params.get("token") != TOKEN_ACESSO:
    st.error("Acesso não autorizado.")
    st.stop()

# --- 3. ESTILO CSS (O "pulo do gato" para ficar bonito) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #007bff;
    }
    .stPlotlyChart {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CARREGAMENTO DE DADOS ---
ID_PLANILHA = st.secrets["id_sheets"]
URL_DADOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv"

registros = carregar_dados(ID_PLANILHA, st.secrets.gids.registros)
cartoes = carregar_dados(ID_PLANILHA, st.secrets.gids.cartoes)
saidas = carregar_dados(ID_PLANILHA, st.secrets.gids.saidas)
campanhas = carregar_dados(ID_PLANILHA, st.secrets.gids.campanhas)

cartoes_ = processar_cartoes(cartoes, registros)
registros_ = processar_registros(registros)
periodos = processar_conclusoes(cartoes, registros)

if cartoes_ not in st.session_state:
    st.session_state['cartoes_'] = cartoes_
if registros_ not in st.session_state:
    st.session_state['registros_'] = registros_
if periodos not in st.session_state:
    st.session_state['periodos'] = periodos

# --- 5. CABEÇALHO ---
st.title("Dashboard de controle de territórios - Praia do Futuro")
st.caption(f"Dados sincronizados do Google Sheets | Atualizado em: {datetime.now().strftime('%d/%m %H:%M')}")
st.divider()

# --- 6. KPIs / MÉTRICAS (Os "quadradinhos" do topo) ---
# Substitua 'Vendas' e 'Meta' pelos nomes reais das suas colunas
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(
        "Total de cartões",
        cartoes_['ID'].n_unique()
    )
with col2:
    st.metric(
        "Cartões com registro",
        cartoes_.filter(pl.col('Fechamento').is_not_null())['ID'].n_unique()
    )
with col3:
    st.metric(
        "Período atual",
        f'{periodos["Número"].max()}º período'
    )
with col4:
    st.metric(
        "Duração média",
        f'{round(registros_.filter(pl.col("Término").is_not_null())["Duração"].mean())} semanas'
    )
with col5:
    st.metric(
        "Intervalo médio",
        f'{round(registros_.filter(pl.col("Intervalo").is_not_null())["Intervalo"].mean())} semanas'
    )

st.write("##") # Espaçamento

# --- 7. ÁREA DE GRÁFICOS ---

# --- 8. TABELA DETALHADA ---
st.subheader("Territórios prioritários")

#Filtros
col1, col2 = st.columns(2)
with col1:
    opcoes_filtro = cartoes_['Noturno'].unique().to_list()
    noturnos_selecionados = st.segmented_control(
        'Território noturno',
        options=opcoes_filtro,
        default=opcoes_filtro,
        selection_mode='multi',
        key='filtro_noturno'
    )
with col2:
    opcoes_filtro = cartoes_['Território'].unique().to_list()
    territorios_selecionados = st.segmented_control(
        'Território',
        options=opcoes_filtro,
        default=opcoes_filtro,
        selection_mode='multi',
        key='filtro_territorio'
    )

# Se o usuário desmarcar tudo, mostra tudo
if not territorios_selecionados:
    territorios_selecionados = cartoes_['Território'].unique().to_list()
if not noturnos_selecionados:
    noturnos_selecionados = cartoes_['Noturno'].unique().to_list()

# Filtragem e Ordenação
df_base = cartoes_.filter(
    pl.col('Território').is_in(territorios_selecionados),
    pl.col('Noturno').is_in(noturnos_selecionados)
).sort(['Intervalo', 'Intervalo (becos)', 'ID'], descending=[True, True, False])

# Processamento da Tabela
# Passamos apenas os dados já filtrados para a função
df_view = formatar_tabela(df_base).drop(pl.col(['Noturno', 'Tem becos?']))

# Exibição
st.dataframe(
    df_view
    .to_pandas()
    .fillna('-')
    .style
    .apply(style_row_by_interval, axis=1, vmin=0, vmax=52)
    .format(precision=0)
    .format({
        'Intervalo': lambda x: '-' if (pd.isna(x) or np.isinf(x)) else
            f'{x:.0f} semanas' if x > 1 else f'{x:.0f} semana',
        'Intervalo (becos)': lambda x: '-' if (pd.isna(x) or np.isinf(x)) else
            f'{x:.0f} semanas' if x > 1 else f'{x:.0f} semana'
    }),
    use_container_width=True
)