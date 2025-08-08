import streamlit as st
import pandas as pd
import plotly.express as px

# ----- Configuração da Página -----
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv("./dados-imersão-final.csv")

# --- Barra Lateral ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df["ano"].unique())
anos_selecionados = st.sidebar.multiselect(
    "Ano", anos_disponiveis, default=anos_disponiveis
)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df["senioridade"].unique())
senioridades_selecionadas = st.sidebar.multiselect(
    "Senioridade", senioridades_disponiveis, default=senioridades_disponiveis
)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df["contrato"].unique())
contratos_selecionados = st.sidebar.multiselect(
    "Contrato", contratos_disponiveis, default=contratos_disponiveis
)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df["tamanho_empresa"].unique())
tamanhos_selecionados = st.sidebar.multiselect(
    "Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis
)

# ----- Filtragem do DataFrame -----
df_filtrado = df[
    (df["ano"].isin(anos_selecionados))
    & (df["senioridade"].isin(senioridades_selecionadas))
    & (df["contrato"].isin(contratos_selecionados))
    & (df["tamanho_empresa"].isin(tamanhos_selecionados))
]

# ----- Contéudo Principal -----
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown(
    "Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros na barra lateral para refinar a sua análise."
)
st.markdown("---")

# ----- Métricas Principais (KPIs) -----
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado["salario"].mean()
    salario_maximo = df_filtrado["salario"].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio = 0
    salario_maximo = 0
    total_registros = 0
    cargo_mais_frequente = "-"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"US$ {salario_medio:.2f}")
col2.metric("Salário Máximo", f"US$ {salario_maximo:.2f}")
col3.metric("Total de Registros", total_registros)
col4.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")

# ----- Análises visuais com Plotly Express -----
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = (
            df_filtrado.groupby("cargo")["usd"]
            .mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )

        grafico_top_cargos = px.bar(
            top_cargos,
            x="usd",
            y="cargo",
            orientation="h",
            title="Top 10 Cargos por salário médio",
            labels={"usd": "Média salarial anual (USD)", "cargo": ""},
        )
        grafico_top_cargos.update_layout(
            title_x=0.1,
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(grafico_top_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de top cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x="usd",
            nbins=30,
            title="Distribuição de Salários anuais",
            labels={"usd": "Faixa salarial (USD)", "count": ""},
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado["remoto"].value_counts().reset_index()
        remoto_contagem.columns = ["tipo_trabalho", "quantidade"]

        grafico_remoto = px.pie(
            remoto_contagem,
            names="tipo_trabalho",
            values="quantidade",
            title="Proporção dos tipos de trabalhos",
            hole=0.5,
        )
        grafico_remoto.update_traces(textinfo="percent+label")
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de proporção de trabalhos.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado["cargo"] == "Data Scientist"]
        media_ds_pais = df_ds.groupby("residencia_iso3")["usd"].mean().reset_index()

        grafico_paises = px.choropleth(
            media_ds_pais,
            locations="residencia_iso3",
            color="usd",
            color_continuous_scale="rdylgn",
            title="Média salarial de Cientista de Dados por País",
            labels={"usd": "Salário médio (USD)", "residencia_iso3": "País"},
        )
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de paises.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
