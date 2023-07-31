# Brazilian public costs insights

[![pt-br](https://img.shields.io/badge/lang-pt--br-green.svg)](https://github.com/washolive/public-costs-br/blob/main/README.pt-br.md)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://public-costs-br.streamlit.app/)

Artificial Intelligence insights on the administrative costs of **brazilian federal public administration** using `Python`, `Streamlit`, `Plotly` and `ChatGPT`.

These expenses form the basis for the provision of public services and include current expenses related to administrative support, electricity, water, telephone, property rental, among others.

Demonstration:

<img src="public-costs-br-demo.gif"/>

The data are consulted from the [Brazilian Open Data Portal](https://dados.gov.br/dados/conjuntos-dados/raio-x-da-administracao-publica-federal) between 2020 and 2023.

## Install

1. Clone repository
```bash
git clone https://github.com/washolive/public-costs-br.git
```
2. Fill the OpenAI API Key
```bash
cd public-costs-br
cp .streamlit/sample_secrets.toml .streamlit/secrets.toml
```
> Open file `.streamlit/secrets.toml` to edit and fill your API Key in the string inside `<>`.

## Execute

### Running Streamlit from the command line
1. Create or use an existing Virtual Env
2. Install the necessary packages and run
```bash
pip install -r requirements.txt
streamlit run src/main.py
```

### Or using Docker container
```
docker build --rm -t costs-br .
docker run -p 8501:8501 costs-br
```

### Or using Docker Compose
```
docker-compose build
docker-compose up
```

## Open
http://localhost:8501
