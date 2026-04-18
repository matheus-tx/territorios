from datetime import datetime
from dateutil.relativedelta import relativedelta
import io
import polars as pl
import streamlit as st
import unidecode
import urllib

@st.cache_data(ttl=3600) # Cache de 1 hora para testes, mude para 86400 depois

def clean_names(df):
    def limpar_string(nome):
        # Remove acentos e espaços e coloca tudo em minúsculo
        nome = unidecode.unidecode(nome)
        nome = nome.lower().strip().replace(" ", "_").replace(".", "_").replace("?", " ")

        return nome
    
    return df.rename({col: limpar_string(col) for col in df.columns})


def carregar_dados(id_planilha, gid_aba):
    url = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv&gid={gid_aba}"
    # Baixa o conteúdo da URL
    with urllib.request.urlopen(url) as response:
        conteudo = response.read()
    
    # Lê o CSV usando o motor do Polars
    df = pl.read_csv(io.BytesIO(conteudo), try_parse_dates=True)

    # df = clean_names(df)
    
    return df


def processar_cartoes(cartoes, registros):
    # Determina quais cartões estão abertos
    cartoes_abertos = (
        registros
        .filter(pl.col('Início').is_not_null() & pl.col('Término').is_null())
        .with_columns(**{'Status': pl.lit('Aberto')})
        .select(pl.col('ID'), pl.col('Status'))
    )

    # Determina há quanto tempo cada cartão com registro de fechamento não é fechado
    hoje = pl.lit(datetime.now())
    ultimos_fechamentos = (
        registros
        .select(pl.col('ID'), pl.col('Término'))
        .group_by(pl.col('ID'))
        .agg(**{'Fechamento': pl.col('Término').max()})
        .with_columns(
            **{
                'Intervalo': ((hoje - pl.col('Fechamento')).dt.total_days() / 7 + 1).round(),
            }
        )
    )

    # Determina há quanto tempo os becos do cartão não são feitos
    fechamentos_becos = (
        registros
        .filter(pl.col('Feitos os becos?') == pl.lit('Sim'))
        .select(pl.col('ID'), pl.col('Término'))
        .group_by(pl.col('ID'))
        .agg(**{'Fechamento': pl.col('Término').max()})
        .with_columns(
            **{
                'Intervalo': ((hoje - pl.col('Fechamento')).dt.total_days() / 7 + 1).round(),
            }
        )
    )
    fechamentos_becos.columns = [col + ' (becos)' for col in fechamentos_becos.columns]

    # Classifica os cartões como abertos ou fechados
    df = (
        cartoes
        .join(cartoes_abertos, on='ID', how='left')
        .with_columns(**{'Status': pl.col('Status').fill_null(pl.lit('Não aberto'))})
    )

    # Determina há quanto tempo cada cartão não é fechado
    df = (
        df
        .join(ultimos_fechamentos, on='ID', how='left')
        .with_columns(**{
            'Intervalo': pl.when(pl.col('Status') == pl.lit('Aberto'))
                .then(pl.lit(0))
                .otherwise(pl.col('Intervalo').fill_null(pl.lit(float('inf'))))
        })
    )

    # Determina há quanto tempo os becos de cada cartão não são fechados
    df = (
        df
        .join(fechamentos_becos, left_on='ID', right_on='ID (becos)', how='left')
        .with_columns(**{
            'Intervalo (becos)': pl.when(pl.col('Tem becos?') == pl.lit('Não')).then(pl.lit(float('-inf')))
                .when(pl.col('Status') == pl.lit('Aberto')).then(pl.lit(0))
                .otherwise(pl.col('Intervalo (becos)').fill_null(pl.lit(float('inf'))))
        })
    )

    return(df)


def processar_registros(registros):
    # Calcula o tempo de fechamento do cartão
    df = (
        registros
        .with_columns(**{
            'Duração': pl.when(pl.col('Término').is_not_null())
                .then(((pl.col('Término') - pl.col('Início')).dt.total_days() / 7 + 1).round())
                .otherwise(((pl.lit(datetime.now()) - pl.col('Início')).dt.total_days() / 7 + 1).round())
        })
    )

    # Calcula o intervalo entre o fechamento do cartão e sua próxima abertura
    df = (
        df
        .sort('Início')
        .with_columns(**{
            'Intervalo': ((pl.col('Início') - pl.col('Término').shift(1).over('ID')).dt.total_days() / 7).round()
        })
    )

    return df


def processar_conclusoes(cartoes, registros):
    n_cartoes = cartoes['ID'].n_unique()

    periodo_concluido = True
    id_periodo = 0
    df_periodo = registros
    data_conclusao = registros['Início'].min()  # Primeira data constante nos registros
    lista_periodos = []
    while periodo_concluido:  # Calcula a data de cada período de conclusão do território
        id_periodo += 1
        # Cada período começa no final do anterior
        data_inicio = data_conclusao
        df_periodo = df_periodo.filter(pl.col('Início') >= data_inicio)

        # A data de conclusão do território é o primeiro fechamento do último cartão a ser fechado dentro do período
        df_conclusao = (
            df_periodo
            .filter(pl.col('Término').is_not_null())
            .filter(pl.col('Término') == pl.col('Término').min().over('ID'))
        )

        # Mas só pode contar que o território foi concluído se todos os cartões tiverem sido fechados
        if df_conclusao.height == n_cartoes:
            # Se todos os cartões tiverem sido fechados, o período está concluído e o loop passa para o próximo
            data_conclusao = df_conclusao['Término'].max()  # O último cartão a ser concluído no período
            duracao = relativedelta(data_conclusao, data_inicio)
            lista_periodos.append({
                'Número': id_periodo,
                'Status': 'Fechado',
                'Data de início': data_inicio,
                'Data de conclusão': None,
                'Duração': duracao.years * 12 + duracao.months
            })
        else:
            # Se nem todos os cartões tiverem sido fechados, o período não está concluído e o loop termina, pois ele é
            # o último
            periodo_concluido = False
            duracao = relativedelta(datetime.now().date(), data_inicio)
            lista_periodos.append({
                'Número': id_periodo,
                'Status': 'Aberto',
                'Data de início': data_inicio,
                'Data de conclusão': None,
                'Duração': duracao.years * 12 + duracao.months
            })
    
    df_periodos = pl.DataFrame(lista_periodos)

    return df_periodos