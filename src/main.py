"""
Insights sobre os dados de custeio administrativo da administração
pública federal brasileira usando dashboard Streamlit e ChatGPT.
As despesas constituem a base para a prestação de serviços públicos e
compreendem gastos correntes relativos a apoio administrativo,
energia elétrica, água, telefone, locação de imóveis, entre outros.
"""

import locale
from urllib.request import urlopen, quote
from zipfile import ZipFile
from io import BytesIO
import pandas as pd
import streamlit as st
import plotly.express as px
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


def all_filters(df: pd.DataFrame):
    """Executa todas as filtragens conforme seleção do usuário"""
    df = filter_data(df, "orgao_superior_nome", "Órgão Superior")
    df = filter_data(df, "orgao_nome", "Órgão/Entidade")
    df = filter_data(df, "item_despesa", "Item de despesa")
    df = filter_data(df, "natureza_despesa", "Natureza de despesa")
    filtered = dict()
    for col in ["orgao_superior_nome", "orgao_nome",
                "item_despesa", "natureza_despesa"]:
        if df[col].nunique() == 1:
            filtered[col] = df[col].iloc[0]
    return (df, filtered)


def create_dashboard(df: pd.DataFrame, filtered: dict):
    """Gera o painel com indicadores e gráficos"""

    ind1, ind2 = st.columns(2)
    valor = locale.currency(df["valor"].max(), grouping=True)
    ind1.metric(label="Máximo", value=valor)
    valor = locale.currency(df["valor"].sum(), grouping=True)
    ind2.metric(label="Soma", value=valor)

    tab1, tab2, tab3 = st.tabs(["Evolução mensal",
                          "Maiores despesas",
                          "Dados detalhados"])
    with tab1:
        df_group = df.groupby(["ano_mes", "item_despesa"],
                            as_index=False)["valor"].agg({"total": "sum"})
        fig = px.bar(df_group, x="ano_mes", y="total", color="item_despesa")
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df_group = df.groupby(["item_despesa", "natureza_despesa"],
                            as_index=False)["valor"].agg({"total": "sum"})
        # Trata valores negativos que impedem a geração do treemap
        df_group.loc[df_group.total < 0, "total"] = 0
        fig = px.treemap(df_group, path=[px.Constant("Total"), "item_despesa",
                                         "natureza_despesa"], values="total")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        df_grid = df.copy()
        # Remove colunas preenchidas nas filtragens
        for col in filtered:
            df_grid = df_grid.drop(col, axis=1)
        st.dataframe(df_grid
                    .sort_values(by=list(df_grid.columns))
                    .set_index("ano_mes"))


def get_insights(df: pd.DataFrame, filtered: dict, qti: int):
    """Chama o ChatGPT para obter insights sobre os dados"""

    if filtered:
        filter_msg = "o dataset está filtrado, contendo somente: "
        for col, value in filtered.items():
            filter_msg += f"{col} = '{value}'; "
    else:
        filter_msg = "o dataset está completo, sem nenhuma filtragem."

    openai.api_key = st.secrets["openai"]["api_key"]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.,
        messages=[
            {"role": "system",
            "content": "Você é um gestor especializado na área financeira "
            "que monitora as despesas públicas da administração pública, com "
            "o objetivo de identificar gastos excessivos e grandes variações "
            "mensais."
            },
            {"role": "user",
            "content": f"O dataset {df} contém dados do custeio administrativo "
            "da administração pública federal. O custeio é o conjunto de "
            "despesas que formam a base para a prestação de serviços públicos e "
            "compreendem gastos correntes relativos a apoio administrativo, "
            "energia elétrica, água, telefone, locação de imóveis, etc. "
            f"Explorando os dados, informe {qti} insights sobre este dataset."
            f"Nos insights, considere que {filter_msg}"
            "Para calcular o gasto total ou as despesas totais de um órgão, de "
            "um item ou de uma natureza de despesa, some todos os valores dos "
            "meses do ano. "
            "Na análise, destaque: "
            "1. Valores muito discrepantes entre órgãos para itens ou naturezas "
            "de despesa iguais. "
            "2. Valores muito diferentes para órgãos com atividades fim "
            "semelhantes, por exemplo: entre ministérios, entre agências, "
            "entre fundações, entre universidades. "
            "4. Variações de valores muito altas nos meses do ano. "
            "5. Variações mensais de valores muito destoantes de outros órgãos. "
            "6. Nas comparações de valores, cite os valores nominais e também "
            "a variação percentual."
            },
        ]
    )
    chat_msg = completion.choices[0].message.content
    st.markdown(chat_msg.replace('$', '\$'))


### Main ###

NUMBER_OF_INSIGHTS = 6

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
    load = st.checkbox("Carregar os dados")
    if load:
        df_full = load_data(year_sel)
        st.session_state.data_loaded = True
        df_filtered, filters = all_filters(df_full)

if load and st.session_state.data_loaded:
    create_dashboard(df_filtered, filters)
    insights = st.button("Insights do ChatGPT")
    if insights:
        get_insights(df_filtered, filters, NUMBER_OF_INSIGHTS)
