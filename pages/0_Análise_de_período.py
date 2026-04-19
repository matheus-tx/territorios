from datetime import date
import polars as pl
import streamlit as st
from apperance_utils import formatar_tabela, style_row_by_interval
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Relatórios", layout="wide")

# Tentar recuperar os dados da memória
if 'cartoes_' in st.session_state:
    df_cartoes: pl.DataFrame = st.session_state['cartoes_']
    df_periodos: pl.DataFrame = st.session_state['periodos']
    df_registros: pl.DataFrame = st.session_state['registros_']
else:
    # Caso o utilizador entre direto pelo link da página 2 sem passar pela 1
    st.warning("Dados não encontrados. Por favor, aceda primeiro à Página Inicial.")
    
    # Opcional: Se quiser que a página 2 também carregue os dados caso falhe o state
    # df_segunda_pagina = carregar_dados() # Chamando a sua função de cache

col1, col2 = st.columns(2)
with col1:
    st.title("Análise de período")
with col2:
    opcoes_filtro = df_periodos['Período'].unique().to_list()
    periodo_selecionado = st.selectbox(
        'Período',
        options=opcoes_filtro,
        index=opcoes_filtro.index(df_periodos['Período'].max()),
        key='filtro_periodo'
    )

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        opcoes_filtro = df_cartoes['Noturno'].unique().to_list()
        noturnos_selecionados = st.pills(
            'Pregação noturna',
            options=opcoes_filtro,
            default=opcoes_filtro,
            selection_mode='multi',
            key='filtro_noturno'
        )
    with col2:
        opcoes_filtro = df_cartoes['Território'].unique().to_list()
        territorios_selecionados = st.pills(
            'Território',
            options=opcoes_filtro,
            default=opcoes_filtro,
            selection_mode='multi',
            key='filtro_territorio'
        )

cartoes_selecionados = (
    df_cartoes
    .filter(pl.col('Noturno').is_in(noturnos_selecionados))
    .filter(pl.col('Território').is_in(territorios_selecionados))
    ['ID']
    .unique()
    .to_list()
)
df_cartoes = df_cartoes.filter(pl.col('ID').is_in(cartoes_selecionados))
df_registros = df_registros.filter(pl.col('ID').is_in(cartoes_selecionados))

n_cartoes = df_cartoes.height
n_cartoes_abertos = df_cartoes.filter(pl.col('Status') == pl.lit('Aberto')).height
n_cartoes_fechados = df_cartoes.filter(pl.col('Fechamento').is_not_null()).height
n_cartoes_pendentes = df_cartoes.filter(pl.col('Fechamento').is_null()).height
n_cartoes_progresso = (
    df_cartoes
    .filter(pl.col('Status') == pl.lit('Aberto'))
    .filter(pl.col('Fechamento').is_null())
).height

col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        fig = go.Figure(
            go.Indicator(
                mode = "gauge+number",
                value = n_cartoes_fechados,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Cartões fechados", 'font': {'size': 14}},
                gauge = {
                    'axis': {
                        'range': [0, n_cartoes],
                        'tickwidth': 0.5,
                        'dtick': n_cartoes / 2
                    },
                    'bar': {'color': "rgba(219, 15, 49, 0.75)"},
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "gray",
                }
            )
        )
        fig.update_layout(height=100, margin=dict(t=45, b=5, l=20, r=20))
        st.plotly_chart(fig, width='stretch', key='n_fechados')
with col2:
    with st.container(border=True):
        fig = go.Figure(
            go.Indicator(
                mode = "gauge+number",
                value = n_cartoes_pendentes,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Cartões pendentes", 'font': {'size': 14}},
                gauge = {
                    'axis': {
                        'range': [0, n_cartoes],
                        'tickwidth': 0.5,
                        'dtick': n_cartoes / 2
                    },
                    'bar': {'color': "rgba(219, 15, 49, 0.75)"},
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "gray",
                }
            )
        )
        fig.update_layout(height=100, margin=dict(t=45, b=5, l=20, r=20))
        st.plotly_chart(fig, width='stretch', key='n_pendentes')
with col3:
    with st.container(border=True):
        fig = go.Figure(
            go.Indicator(
                mode = "gauge+number",
                value = n_cartoes_abertos,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Cartões abertos", 'font': {'size': 14}},
                gauge = {
                    'axis': {
                        'range': [0, n_cartoes],
                        'tickwidth': 0.5,
                        'dtick': n_cartoes / 2
                    },
                    'bar': {'color': "rgba(219, 15, 49, 0.75)"},
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "gray",
                }
            )
        )
        fig.update_layout(height=100, margin=dict(t=45, b=5, l=20, r=20))
        st.plotly_chart(fig, width='stretch', key='n_abertos')
with col4:
    with st.container(border=True):
        fig = go.Figure(
            go.Indicator(
                mode = "gauge+number",
                value = n_cartoes_progresso,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Cartões em progresso", 'font': {'size': 14}},
                gauge = {
                    'axis': {
                        'range': [0, n_cartoes_abertos],
                        'tickwidth': 0.5,
                        'dtick': n_cartoes_abertos / 2
                    },
                    'bar': {'color': "rgba(219, 15, 49, 0.75)"},
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "gray",
                }
            )
        )
        fig.update_layout(height=100, margin=dict(t=45, b=5, l=20, r=20))
        st.plotly_chart(fig, width='stretch', key='n_progresso')

inicio_periodo_atual = df_periodos.filter(pl.col('Período') == periodo_selecionado)['Período'][0]
df_registros_atuais = (
    df_registros
    .filter(
        (pl.col('Início') >= inicio_periodo_atual)
            | (pl.col('Término') > inicio_periodo_atual)
            | (pl.col('Término').is_null())
    )
    .with_columns(**{
        'Status': pl.when(pl.col('Término').is_null()).then(pl.lit('Aberto')).otherwise(pl.lit('Não aberto')),
        'Término': pl.col('Término').fill_null(date.today())
    })
)
df_contagem = (
    df_registros_atuais
    .filter(pl.col('Término').is_not_null())
    .group_by('ID')
    .agg(
        pl.len().alias('Fechamentos')
    )
)

df_view = (
    df_cartoes
    .join(df_contagem, on='ID', how='left')
    .with_columns(
        pl.col('Fechamentos').fill_null(pl.lit(0))
    )
    .sort([pl.col('Fechamentos'), pl.col('ID')], descending=[True, False])
)

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        fig_head = px.bar(
            df_view.with_columns(pl.col('ID').cast(pl.Utf8)).head(10).to_pandas(), 
            x='ID', 
            y='Fechamentos',
            text='Fechamentos',
            color_discrete_sequence=['rgba(219, 15, 49, 0.75)']
        )
        fig_head.update_layout(
            xaxis={'type': 'category'},
            title='Territórios mais pregados'
        )
        st.plotly_chart(fig_head, width='stretch', key='fig_head')
with col2:
    with st.container(border=True):
        fig_tail = px.bar(
            df_view.with_columns(pl.col('ID').cast(pl.Utf8)).tail(10).to_pandas(), 
            x='ID', 
            y='Fechamentos',
            text='Fechamentos',
            color_discrete_sequence=['rgba(219, 15, 49, 0.75)']
        )
        fig_tail.update_layout(
            xaxis={'type': 'category'},
            title='Territórios menos pregados'
        )
        st.plotly_chart(fig_tail, width='stretch', key='fig_tail')

fig = px.timeline(
    df_registros_atuais
        .with_columns(**{
            'Duração_unidade': pl.format(
                "{} semana{}", 
                pl.col("Duração").cast(pl.Int16), 
                pl.when(pl.col("Duração") > 1).then(pl.lit("s")).otherwise(pl.lit(""))
            )
        }),
    x_start='Início',
    x_end='Término',
    y='ID',
    text='Duração',
    color='Status',
    hover_data={
        'ID': True,
        'Início': '|%d/%m/%Y',
        'Término': '|%d/%m/%Y',
        'Duração_unidade': True,
        'Saída': True
    },
    labels={'Duração_unidade': 'Duração'},
    color_discrete_map={
        'Aberto': 'rgba(219, 15, 49, 0.4)',
        'Não aberto': 'rgba(219, 15, 49, 0.8)'
    }
)
fig.update_yaxes(
    type='category',
    categoryorder='array',
    categoryarray=df_cartoes['ID'].sort().to_list(),
    autorange='reversed',
    tickmode='linear',
    dtick=1
)
fig.update_traces(
    textposition='inside',
    insidetextanchor='middle',
    textangle=0
)
fig.update_layout(
    xaxis_title='Linha do tempo',
    yaxis_title='Cartões',
    margin=dict(l=20, r=20, t=40, b=20),
    bargap=0.2,
    showlegend=True,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        xanchor='center',
        y=1.02,
        x=0.5
    )
)

with st.container(border=True):
    st.caption('Linha do tempo')
    st.plotly_chart(fig, width='stretch', key='timeline', height=max(df_cartoes.height * 25, 400))