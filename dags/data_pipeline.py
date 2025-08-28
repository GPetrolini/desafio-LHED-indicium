from __future__ import annotations
import os
import pandas as pd
from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pendulum
from datetime import datetime

default_args = {
    "email_on_failure": True,
    "email_on_retry": False,
    "start_date": datetime(2025, 8, 25),
    "retries": 1,
}


pasta_destino = "/opt/airflow/data_extraida"
tabelas = [
    "agencias",
    "clientes",
    "colaboradores",
    "contas",
    "propostas_credito"]
drop_table = "DROP TABLE IF EXISTS {tabela_nome};"

with DAG(
    dag_id="banvic_data_pipeline",
    start_date=pendulum.datetime(2025, 8, 25, tz="America/Sao_Paulo"),
    schedule_interval="35 4 * * *",
    catchup=False,
    tags=["banvic", "data_engineering"],
    doc_md="""
    ### Banvic Data Pipeline
    DAG responsável por extrair e carregar dados.

    **Tasks:**
    - `extrai_csv_transacoes`: extrai o CSV de transações e salva em uma pasta diária.
    - `extracao_tabela_<tabela>`: extrai cada tabela do banco de origem e salva em pasta diária.
    - `carrega_dw`: carrega todos os CSVs (tabelas e transações) no Data Warehouse, substituindo tabelas existentes.
    """,
) as dag:

    @task(task_id="extrai_csv_transacoes")
    def extrai_csv_transacoes(file_path: str) -> str:
        os.makedirs(file_path, exist_ok=True)
        arquivo_origem = "/opt/airflow/data_fonte/transacoes.csv"
        arquivo_destino = os.path.join(file_path, "transacoes.csv")
        df_transacoes = pd.read_csv(arquivo_origem)
        df_transacoes.to_csv(arquivo_destino, index=False)
        return arquivo_destino

    def extracao_tabela(tabela: str, query: str):
        @task(task_id=f"extracao_tabela_{tabela}")
        def extrai_tabela(sql_query: str, table: str, file_path: str) -> str:
            os.makedirs(file_path, exist_ok=True)
            pg_hook = PostgresHook(postgres_conn_id="banvic_source_db")
            df_tabela = pg_hook.get_pandas_df(sql_query)
            arquivo_csv = os.path.join(file_path, f"{table}.csv")
            df_tabela.to_csv(arquivo_csv, index=False)
            return arquivo_csv
        return extrai_tabela

    tasks_extracao_tabelas = []
    for tabela in tabelas:
        query = f"SELECT * FROM {tabela}"
        task_tabela = extracao_tabela(tabela, query)(
            sql_query=query,
            table=tabela,
            file_path=os.path.join(pasta_destino, "{{ ds }}", "sql"),
        )
        tasks_extracao_tabelas.append(task_tabela)

    arquivo_transacoes = extrai_csv_transacoes(
        file_path=os.path.join(pasta_destino, "{{ ds }}", "csv")
    )

    @task(task_id="carrega_csv_transacoes")
    def carrega_csv_transacoes(arquivo: str, drop_query: str):
        pg_dw = PostgresHook(postgres_conn_id="banvic_dw")
        tabela_nome = os.path.basename(arquivo).replace(".csv", "")
        df_tabela = pd.read_csv(arquivo)
        pg_dw.run(drop_query.format(tabela_nome=tabela_nome))
        df_tabela.to_sql(
            tabela_nome,
            con=pg_dw.get_sqlalchemy_engine(),
            if_exists="replace",
            index=False,
        )

    def carrega_tabela(tabela: str):
        @task(task_id=f"carrega_dw_{tabela}")
        def carrega_dw(arquivo: str, drop_query: str):
            pg_dw = PostgresHook(postgres_conn_id="banvic_dw")
            tabela_nome = os.path.basename(arquivo).replace(".csv", "")
            df_tabela = pd.read_csv(arquivo)
            pg_dw.run(drop_query.format(tabela_nome=tabela_nome))
            df_tabela.to_sql(
                tabela_nome,
                con=pg_dw.get_sqlalchemy_engine(),
                if_exists="replace",
                index=False,
            )
        return carrega_dw

    tasks_carregamento = []
    for tabela in tabelas:
        carrega = carrega_tabela(tabela)(
            arquivo=os.path.join(
                pasta_destino, "{{ ds }}", "sql", f"{tabela}.csv"
            ),
            drop_query=drop_table,
        )
        tasks_carregamento.append(carrega)

    carrega_transacoes = carrega_csv_transacoes(
        arquivo=os.path.join(pasta_destino, "{{ ds }}", "csv", "transacoes.csv"),
        drop_query=drop_table,
    )

    for i, extrai_task in enumerate(tasks_extracao_tabelas):
        extrai_task >> tasks_carregamento[i]

    arquivo_transacoes >> carrega_transacoes