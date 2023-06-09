# Insights sobre o custeio administrativo BR

Insights sobre os dados de custeio da **Administração Pública Federal brasileira**, usando `Python`, `Streamlit` e `ChatGPT`.

Essas despesas constituem a base para a prestação de serviços públicos e compreendem gastos correntes relativos a apoio administrativo, energia elétrica, água, telefone, locação de imóveis, entre outros.

Os dados são consultados do [Portal Brasileiro de Dados Abertos](https://dados.gov.br/dados/conjuntos-dados/raio-x-da-administracao-publica-federal).

## Instalar

1. Clonar o repositório
```bash
git clone https://github.com/washolive/public-costs-br.git
```
2. Ir para o diretório onde o repositório foi clonado
```bash
cd public-costs-br
```
3. Preencher a Openai API Key
```bash
cp .streamlit/sample_secrets.toml .streamlit/secrets.toml
```
> Abrir o arquivo `.streamlit/secrets.toml` para edição e colocar a sua API Key na string indicada por `<>`.

## Executar

### Se preferir com o Streamlit
1. Criar ou usar um Virtual Env
2. Instalar as packages necessárias
```bash
pip install -r requirements.txt
```
3. Executar
```bash
streamlit run src/main.py
```

### Se preferir container Docker
```
docker build --rm -t costs-br .
docker run -p 8501:8501 costs-br
```

### Se preferir Docker Compose
```
docker-compose build
docker-compose up
```

## Acessar
http://localhost:8501
