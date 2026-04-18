import numpy as np
import polars as pl
import polars.selectors as cs

def formatar_tabela(df):
    # Transforma todas as colunas de data para o formato DD/MM/YYYY
    df = (
        df
        .with_columns(
            cs.date().dt.strftime('%d/%m/%Y'),
            cs.datetime().dt.strftime('%d/%m/%Y')
        )
    )

    return df

def style_row_by_interval(row, vmin, vmax):
    val = row['Intervalo']
    # Normaliza o alpha baseado na coluna Intervalo
    alpha = np.clip((val - vmin) / (vmax - vmin), 0, 0.5)
    
    # Define a cor RGBA
    color = f"background-color: rgba(219, 15, 49, {alpha:.2f});"
    
    # Retorna o estilo para todas as células daquela linha
    return [color] * len(row)