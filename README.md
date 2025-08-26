# Desafio de Engenharia de Dados - Banco Vitória

## Introdução

Este projeto simula um pipeline de engenharia de dados para o Banco Vitória S.A. (BanVic), uma instituição fictícia que busca aprimorar sua cultura e uso de dados. O objetivo é centralizar dados de diferentes fontes em um Data Warehouse local para análises futuras.

O pipeline de dados foi orquestrado usando **Apache Airflow**, e a solução utiliza **Docker** e **Docker Compose** para garantir um ambiente de desenvolvimento e produção consistente e reproduzível. As fontes de dados são um arquivo CSV com dados de transações e um banco de dados PostgreSQL com informações de clientes, agências e propostas de crédito.

## Estrutura do Projeto

O projeto está organizado na seguinte estrutura de diretórios:

```desafio-LHED-indicium/
├── dags/
│   └── data_pipeline.py
├── data_fonte/
│   ├── banvic.sql
│   └── transacoes.csv
├── dbdata/
├── dw_data/
├── logs/
├── docker-compose.yml
└── README.md
```

## Pré-requisitos

Para executar este projeto, você precisa ter o **Docker** e o **Docker Compose** instalados em sua máquina.

## Como Executar o Projeto

Siga os passos abaixo para iniciar o ambiente e executar o pipeline de dados:

1.  Clone este repositório para o seu ambiente local:
    `git clone https://github.com/GPetrolini/desafio-LHED-indicium.git`
2.  Navegue até o diretório do projeto:
    `cd desafio-LHED-indicium`
3.  Inicie os contêineres Docker (Airflow, banco de dados fonte e Data Warehouse):
    `docker-compose up -d`
    *Este processo pode demorar alguns minutos na primeira vez, pois irá baixar as imagens e configurar os serviços.*
4.  Acesse a interface de usuário do Airflow em seu navegador:
    `http://localhost:8080`
5.  Faça login com as credenciais padrão:
    * **Usuário:** `airflow`
    * **Senha:** `airflow`
6.  A DAG `banvic_data_pipeline` deve estar visível e em estado "Paused". Ative-a clicando no botão de alternância. Você pode acionar uma execução manual a partir da interface do Airflow para ver o pipeline em ação.

## Lógica do Pipeline (DAG)

O pipeline de dados é uma DAG com a seguinte lógica:

1.  **Extração em Paralelo:** Duas tarefas independentes são executadas simultaneamente para extrair os dados.
    * Uma tarefa extrai os dados do arquivo `transacoes.csv`.
    * A outra tarefa extrai os dados das tabelas do banco de dados `banvic`.
    * Todos os dados extraídos são salvos em arquivos CSV temporários no diretório `./data_extraida/` seguindo o padrão de nomenclatura `<ano>-<mês>-<dia>/<fonte-de-dados>/<nome-da-tabela-ou-csv>.csv`.

2.  **Carregamento no Data Warehouse:**
    * Esta tarefa só é iniciada após a conclusão bem-sucedida de ambas as extrações.
    * Os arquivos CSV temporários são lidos e os dados são carregados no Data Warehouse.
    * Para garantir a **idempotência**, as tabelas de destino são limpas antes de um novo carregamento.

---
**Autor:** Gustavo Antony Petrolini