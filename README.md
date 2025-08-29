# Desafio de Engenharia de Dados - Indicium

### Visão Geral

Este projeto é uma pipeline de ETL (Extração, Transformação e Carregamento) construída com Apache Airflow e Docker. Seu objetivo é extrair dados de um banco de dados e de um arquivo CSV, e carregá-los em um Data Warehouse.

### Tecnologias

* **Apache Airflow 2.11.0**: Orquestrador do pipeline.
* **Docker & Docker Compose**: Gerenciamento dos serviços.
* **Python 3.12**: Linguagem de desenvolvimento.
* **PostgreSQL**: Base de dados de origem e destino (DW).
* **Pandas**: Biblioteca para manipulação de dados.

---

### Pré-requisitos

Para executar este projeto, você precisará ter o Docker e o Docker Compose instalados e configurados em seu ambiente. O Git também é necessário para clonar o repositório.

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
├── docker-compose.yml
├── .gitignore
└── README.md
```
---

### Instruções de Execução

1.  **Clone o Repositório:**
    ```sh
    git clone [https://github.com/GPetrolini/desafio-LHED-indicium](https://github.com/GPetrolini/desafio-LHED-indicium)
    cd desafio-LHED-indicium
    ```

2.  **Inicie os Serviços com Docker Compose:**
    O comando a seguir irá iniciar todos os serviços (Airflow Webserver, Scheduler, PostgreSQL, etc.) e pode demorar alguns minutos na primeira execução.
    ```sh
    docker-compose up -d
    ```

3.  **Acesse a Interface do Airflow:**
    Após os serviços estarem prontos, abra seu navegador e acesse:
    * **URL:** http://localhost:8080
    * **Credenciais (usuário/senha):** `airflow` / `airflow`

4.  **Execute o DAG:**
    Na interface do Airflow, localize o DAG `banvic_data_pipeline`. Para iniciar a execução, basta clicar no botão de "play" e o pipeline de ETL será ativado.

---

### Fluxo do Pipeline

O DAG é composto por três etapas principais:

1.  **Extração de Dados**:
    * Uma tarefa extrai o arquivo `transacoes.csv` e o salva na pasta `data_extraida`.
    * Tarefas individuais extraem cada tabela do banco de dados de origem (`agencias`, `clientes`, etc.).

2.  **Transformação (implícita)**:
    * Os dados extraídos são convertidos para o formato CSV e salvos em disco. Embora não haja uma transformação complexa de dados, essa etapa representa a conversão e o armazenamento temporário em um formato padronizado antes do carregamento.

3.  **Carregamento para o Data Warehouse**:
    * Cada arquivo CSV extraído é carregado em uma tabela correspondente no Data Warehouse.
    * **Destaque:** Esta etapa utiliza paralelismo, permitindo que várias tabelas sejam carregadas simultaneamente para maior performance.

---

### Considerações Técnicas

* O pipeline foi projetada para ser **escalável** utilizando a criação dinâmica de tarefas. Isso permite adicionar novas tabelas ao pipeline de forma automática, apenas atualizando uma lista no código.
* A abordagem de tarefas atômicas para o carregamento de dados torna o pipeline **resiliente** a falhas, facilitando a depuração e a reexecução.