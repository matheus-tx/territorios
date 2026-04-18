import streamlit as st
from apperance_utils import formatar_tabela, style_row_by_interval

st.set_page_config(page_title="Relatórios", layout="wide")

st.title("Esta é a segunda página")

# 1. Tentar recuperar os dados da memória
if 'cartoes_' in st.session_state:
    df_cartoes_2 = st.session_state['cartoes_']
    
    # Agora pode usar o df_segunda_pagina normalmente
    st.write("Dados carregados da página inicial!")
    st.dataframe(df_cartoes_2)
    
else:
    # Caso o utilizador entre direto pelo link da página 2 sem passar pela 1
    st.warning("Dados não encontrados. Por favor, aceda primeiro à Página Inicial.")
    
    # Opcional: Se quiser que a página 2 também carregue os dados caso falhe o state
    # df_segunda_pagina = carregar_dados() # Chamando a sua função de cache

st.dataframe(
    formatar_tabela(df_cartoes_2)
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