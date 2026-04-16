import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO ---
TOKEN_ACESSO = "sua_chave_secreta_aqui"  # Escolha algo difícil
ID_PLANILHA = "COLE_O_ID_DA_SUA_PLANILHA_AQUI"
URL_DADOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv"

# --- SEGURANÇA POR URL ---
if st.query_params.get("token") != TOKEN_ACESSO:
    st.title("🔒 Acesso Restrito")
    st.warning("Você precisa do link de acesso correto para visualizar este dashboard.")
    st.stop()

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=86400) # Atualiza a cada 24 horas
def carregar_dados():
    df = pd.read_csv(URL_DADOS)
    return df

df = carregar_dados()

# --- DASHBOARD ---
st.set_page_config(page_title="Meu Dashboard", layout="wide")
st.title("📊 Indicadores de Negócio")

# Exemplo de métricas (ajuste conforme os nomes das suas colunas)
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("Visualização dos Dados")
    st.dataframe(df, use_container_width=True)

with col2:
    st.subheader("Gráfico de Evolução")
    # Gera gráfico com a primeira coluna no X e a segunda no Y
    st.line_chart(df.set_index(df.columns[0]))

st.caption(f"Última atualização: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")
