# Insights sobre o custeio administrativo Brasil

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/washolive/public-costs-br/blob/main/README.md)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://public-costs-br.streamlit.app/)

Insights sobre os dados de custeio da **Administração Pública Federal brasileira** usando `Python`, `Streamlit`, `Plotly` e `ChatGPT`.

Essas despesas constituem a base para a prestação de serviços públicos e compreendem gastos correntes relativos a apoio administrativo, energia elétrica, água, telefone, locação de imóveis, entre outros.

Demonstração:

<img src="public-costs-br-demo.gif"/>

Os dados são consultados do [Portal Brasileiro de Dados Abertos](https://dados.gov.br/dados/conjuntos-dados/raio-x-da-administracao-publica-federal) entre 2020 e 2023.

## Instalar

1. Clonar o repositório
```bash
git clone https://github.com/washolive/public-costs-br.git
```
2. Informar a OpenAI API Key
```bash
cd public-costs-br
cp .streamlit/sample_secrets.toml .streamlit/secrets.toml
```
> Abrir o arquivo `.streamlit/secrets.toml` para edição e colocar a sua API Key na string indicada por `<>`.

## Executar

### Chamando o Streamlit
1. Criar ou usar um Virtual Env
2. Instalar as packages necessárias e executar
```bash
pip install -r requirements.txt
streamlit run src/main.py
```

### Ou usando container Docker
```
docker build --rm -t costs-br .
docker run -p 8501:8501 costs-br
```

### Ou usando Docker Compose
```
docker-compose build
docker-compose up
```

## Acessar
http://localhost:8501
