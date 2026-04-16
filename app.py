import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha) ---
st.set_page_config(
    page_title="Dashboard Executivo",
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

@st.cache_data(ttl=3600) # Cache de 1 hora para testes, mude para 86400 depois
def carregar_dados():
    return pd.read_csv(URL_DADOS)

df = carregar_dados()

# --- 5. CABEÇALHO ---
st.title("Dashboard de controle de territórios")
st.caption(f"Dados sincronizados do Google Sheets | Atualizado em: {pd.Timestamp.now().strftime('%d/%m %H:%M')}")
st.divider()

# --- 6. KPIs / MÉTRICAS (Os "quadradinhos" do topo) ---
# Substitua 'Vendas' e 'Meta' pelos nomes reais das suas colunas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Geral", f"{df.iloc[:, 1].sum():,.0f}") 
with col2:
    st.metric("Média Mensal", f"{df.iloc[:, 1].mean():,.2f}")
with col3:
    st.metric("Registros", len(df))
with col4:
    st.metric("Status", "✅ Ativo")

st.write("##") # Espaçamento

# --- 7. ÁREA DE GRÁFICOS ---
col_esq, col_dir = st.columns([1, 1])

with col_esq:
    st.subheader("📈 Evolução Temporal")
    # Gráfico interativo do Plotly
    fig_linha = px.line(df, x=df.columns[0], y=df.columns[1], 
                         template="plotly_white", 
                         color_discrete_sequence=["#007bff"])
    fig_linha.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_linha, use_container_width=True)

with col_dir:
    st.subheader("📊 Distribuição")
    # Gráfico de barras ou pizza
    fig_barra = px.bar(df, x=df.columns[0], y=df.columns[1],
                        template="plotly_white",
                        color=df.columns[1],
                        color_continuous_scale="Blues")
    st.plotly_chart(fig_barra, use_container_width=True)

# --- 8. TABELA DETALHADA ---
with st.expander("🔍 Ver dados brutos detalhados"):
    st.dataframe(df, use_container_width=True)