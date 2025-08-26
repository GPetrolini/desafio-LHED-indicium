from __future__ import annotations

import os
import pendulum
import pandas as pd

from airflow.models.dag import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook

PASTA_DESTINO = '/opt/airflow/data_extraida'
TABELAS = ['agencias', 'clientes', 'colaboradores', 'contas', 'propostas_credito']

with DAG(
    dag_id="banvic_data_pipeline",
    start_date=pendulum.datetime(2025, 8, 25, tz="America/Sao_Paulo"),
    schedule_interval="35 4 * * *",
    catchup=False,
    tags=["banvic", "data_engineering"],
) as dag:

    @task
    def extrai_csv():
        print("Extraindo CSV de transacoes")

        data_execucao = pendulum.now().format('YYYY-MM-DD')
        pasta_csv = os.path.join(PASTA_DESTINO, data_execucao, 'csv')
        os.makedirs(pasta_csv, exist_ok=True)

        arquivo_origem = '/opt/airflow/data_fonte/transacoes.csv'
        arquivo_destino = os.path.join(pasta_csv, 'transacoes.csv')

        df_transacoes = pd.read_csv(arquivo_origem)
        df_transacoes.to_csv(arquivo_destino, index=False)

        print("CSV pronto em: " + arquivo_destino)
        return arquivo_destino

    @task
    def extrai_tabelas():
        print("Extraindo tabelas do banco")

        data_execucao = pendulum.now().format('YYYY-MM-DD')
        pasta_sql = os.path.join(PASTA_DESTINO, data_execucao, 'sql')
        os.makedirs(pasta_sql, exist_ok=True)

        pg_hook = PostgresHook(postgres_conn_id='banvic_source_db')
        arquivos_extraidos = []

        for tabela in TABELAS:
            print("Extraindo tabela " + tabela)
            df_tabela = pg_hook.get_pandas_df("SELECT * FROM " + tabela)
            arquivo_csv = os.path.join(pasta_sql, tabela + ".csv")
            df_tabela.to_csv(arquivo_csv, index=False)
            arquivos_extraidos.append(arquivo_csv)
            print("Tabela " + tabela + " salva em: " + arquivo_csv)

        return arquivos_extraidos

    @task
    def carrega_dw(csv_transacoes: str, csv_tabelas: list[str]):
        print("Carregando dados no Data Warehouse")

        pg_dw = PostgresHook(postgres_conn_id='banvic_dw')

        print("Carregando transacoes")
        df_transacoes = pd.read_csv(csv_transacoes)
        pg_dw.run("""
            CREATE TABLE IF NOT EXISTS transacoes (
                cod_transacao BIGINT,
                num_conta BIGINT,
                data_transacao TIMESTAMP,
                nome_transacao VARCHAR,
                valor_transacao FLOAT
            );
        """)
        pg_dw.run("TRUNCATE TABLE transacoes;")
        df_transacoes.to_sql('transacoes', con=pg_dw.get_sqlalchemy_engine(), if_exists='append', index=False)
        print("Transacoes carregadas")

        for arquivo_csv in csv_tabelas:
            tabela_nome = os.path.basename(arquivo_csv).replace('.csv', '')
            print("Carregando tabela " + tabela_nome)
            df_tabela = pd.read_csv(arquivo_csv)
            pg_dw.run("DROP TABLE IF EXISTS " + tabela_nome + ";")
            df_tabela.to_sql(tabela_nome, con=pg_dw.get_sqlalchemy_engine(), if_exists='replace', index=False)
            print("Tabela " + tabela_nome + " carregada")

        print("Todos os dados carregados")

    arquivo_csv = extrai_csv()
    arquivos_tabelas = extrai_tabelas()
    carrega_dw(arquivo_csv, arquivos_tabelas)
