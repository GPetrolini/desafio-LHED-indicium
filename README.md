# Desafio Indicium - BanVic - Engenharia de Dados

[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/apache--airflow-2.8.2-orange)](https://airflow.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-16-blue)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Descrição

Este repositório contém a solução do **Desafio de Engenharia de Dados do Banco Vitória (BanVic)**. O objetivo é construir um **pipeline de dados** que:

- Extraia dados de múltiplas fontes (CSV e SQL);
- Armazene os dados no **Data Warehouse** (PostgreSQL);
- Utilize o **Apache Airflow** como orquestrador de tarefas;
- Garanta extrações idempotentes e paralelas;
- Estruture os dados em arquivos CSV com padrão de nomenclatura por data.

O pipeline simula uma **jornada real de dados financeiros** de um banco fictício e é reproduzível em outros ambientes.

---

## Estrutura do Projeto

```
.
├── dags/
│   └── data_pipeline.py
├── data_fonte/
├── data_extraida/
│   ├── csv/
│   │   └── transacoes.csv
│   └── sql/
│       ├── agencias.csv
│       ├── clientes.csv
│       ├── colaboradores.csv
│       ├── colaborador_agencia.csv
│       ├── contas.csv
│       └── propostas_credito.csv
├── dbdata/
├── dw_data/
├── logs/
├── plugins/
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Pré-requisitos
- Docker e Docker Compose instalados;

- Navegador para acessar o Airflow Web UI (localhost:8080);

- Git para clonar o repositório.


## Configuração e Execução
### 1. Clone o repositório:
```
git clone https://github.com/GPetrolini/desafio-LHED-indicium
cd desafio-LHED-indicium
```
### 2. Suba os containers:
```
docker-compose up -d
```
Isso criará:

- banvic_source_db (PostgreSQL fonte);

- banvic_dw (Data Warehouse);

- airflow_webserver e airflow_scheduler (Airflow).

### 3. Verifique se os containers estão rodando:
```
docker ps
```
### 4. Acesse o Airflow Web UI: http://localhost:8080

### 5 . Execute a ```DAG banvic_data_pipeline``` manualmente ou aguarde a execução agendada (04:35 AM).


## Estrutura da DAG
A DAG realiza três tarefas principais:

1. extrai_csv: lê o CSV de transações e salva em ```data_extraida/csv/YYYY-MM-DD/transacoes.csv```.

2. extrai_tabelas: extrai tabelas SQL do banco fonte e salva em ```data_extraida/sql/YYYY-MM-DD/<tabela>.csv```.

3. carrega_dw: carrega os CSVs extraídos no Data Warehouse PostgreSQL.

Dependências de execução:

- ```extrai_csv``` e ```extrai_tabelas``` executam em paralelo;

- ```carrega_dw``` só inicia após sucesso das extrações.

## Observações
- Extrações são idempotentes: rodar a DAG várias vezes não duplicará os dados;

- O pipeline está programado para execução diária às 04:35 AM;

- Todos os arquivos seguem padrão ```<ano>-<mês>-<dia>/<fonte>/<nome>.csv```.

- O pipeline pode ser reproduzido em qualquer máquina com Docker e Docker Compose;

- Logs do Airflow estão disponíveis na pasta ```logs/```.