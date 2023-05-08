"""
Insights sobre os dados de custeio administrativo da administração
pública federal brasileira usando dashboard Streamlit e ChatGPT.
As despesas constituem a base para a prestação de serviços públicos e
compreendem gastos correntes relativos a apoio administrativo,
energia elétrica, água, telefone, locação de imóveis, entre outros.

Requisitos:
    - python >= 3.7
    - openai >= 0.27
    - streamlit >= 1.21

Para executar:
    > streamlit run src/main.py
"""

import locale
from urllib.request import urlopen, quote
from zipfile import ZipFile
from io import BytesIO
import pandas as pd
import streamlit as st
import openai


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

@st.cache_data(persist="disk")
def load_data(year: int) -> pd.DataFrame:
    """Lê os arquivos de dados abertos e carrega em um dataframe"""

    REPO_URL = "https://repositorio.dados.gov.br/seges/raio-x/"
    FILE_PREFIX = "raiox"
    CSV_FILE = "custeio-administrativo.csv"

    df_list = []
    for ref in range(12):
        file_name = f"{FILE_PREFIX}-{year}-{(ref + 1):02d}.zip"
        file_url = REPO_URL + quote(file_name)
        url = urlopen(file_url)
        file = ZipFile(BytesIO(url.read()))
        df_month = pd.read_csv(file.open(CSV_FILE))
        df_list.append(df_month)

    df = pd.concat(df_list, axis=0, ignore_index=True)

    df["ano_mes_referencia"] = df["ano_mes_referencia"].apply(str)
    df = df[["ano_mes_referencia", "orgao_superior_nome",
            "orgao_nome", "nome_item", "nome_natureza_despesa_detalhada",
            "valor"]]
    df.rename({"ano_mes_referencia": "ano_mes",
               "nome_item": "item_despesa",
               "nome_natureza_despesa_detalhada": "natureza_despesa"},
            axis=1, inplace=True)
    df = df[df["valor"] != 0]
    return df


def filter_data(df: pd.DataFrame, col: str, col_lbl: str) -> pd.DataFrame:
    """Filtra linhas no dataframe"""
    SELECT_ALL = ""
    col_list = pd.unique(df[col]).tolist()
    col_list.append(SELECT_ALL)
    filter_sel = st.selectbox(col_lbl, sorted(col_list))
    if filter_sel != SELECT_ALL:
        df = df[df[col] == filter_sel]
    return df


def all_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Executa todas as filtragens conforme seleção do usuário"""
    df = filter_data(df, "orgao_superior_nome", "Órgão Superior")
    df = filter_data(df, "orgao_nome", "Órgão/Entidade")
    df = filter_data(df, "item_despesa", "Item de despesa")
    df = filter_data(df, "natureza_despesa", "Natureza de despesa")
    return df


def create_dashboard(df: pd.DataFrame):
    """Gera o painel com indicadores e gráficos"""

    ind1, ind2 = st.columns(2)
    valor = locale.currency(df["valor"].min(), grouping=True)
    ind1.metric(label="Mínimo", value=valor)
    valor = locale.currency(df["valor"].max(), grouping=True)
    ind2.metric(label="Máximo", value=valor)

    ind3, ind4 = st.columns(2)
    valor = locale.currency(df["valor"].mean(), grouping=True)
    ind3.metric(label="Média", value=valor)
    valor = locale.currency(df["valor"].sum(), grouping=True)
    ind4.metric(label="Soma", value=valor)

    st.subheader("Evolução mensal")
    df_group = df.groupby(["ano_mes"],
                          as_index=False)["valor"].agg({"total": "sum"})
    st.bar_chart(data=df_group, x="ano_mes", y="total")

    st.subheader("Dados detalhados")
    df_grid = df.copy()
    for col in ["orgao_superior_nome", "orgao_nome",
                "item_despesa", "natureza_despesa"]:
        # Remove colunas preenchidas nas filtragens
        if df_grid[col].nunique() == 1:
            df_grid = df_grid.drop(col, axis=1)
    st.dataframe(df_grid.set_index("ano_mes"))


def get_insights(df: pd.DataFrame):
    """Chama o ChatGPT para obter insights sobre os dados"""

    # Temporarily using may API key
    openai.api_key = st.secrets["openai"]["api_key"]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.1,
        messages=[
            {"role": "user",
                "content": f"""O dataset a seguir contém dados do
                custeio administrativo da administração pública federal.
                Informe 6 insights sobre este dataset: {df}"""
            },
        ]
    )
    st.markdown(completion.choices[0].message.content)


### Main ###

st.set_page_config(
    page_title="Custeio Insights",
    layout="wide",
    initial_sidebar_state="expanded",
)
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

st.header("Custeio Insights")
st.markdown("""Visualização e obtenção de insights sobre os custos
    da Administração Pública Federal brasileira.""")

with st.sidebar:
    st.subheader("Filtros")
    year_sel = st.selectbox("Ano", [2020, 2021, 2022], index=2)
    if year_sel:
        df_full = load_data(year_sel)
        st.session_state.data_loaded = True
    if st.session_state.data_loaded:
        df_filtered = all_filters(df_full)

create_dashboard(df_filtered)
insights = st.button("Insights do ChatGPT")
if insights:
    get_insights(df_filtered)
