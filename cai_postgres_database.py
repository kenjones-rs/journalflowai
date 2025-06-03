
# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import json
import psycopg2
import psycopg2.extras
import logging
from logging.handlers import RotatingFileHandler
from cai_database import Database

# Set up logging for PostgresDatabase
pg_logger = logging.getLogger('PostgresDatabase')
pg_handler = RotatingFileHandler('./logs/postgres_database.log', maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
pg_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
pg_handler.setFormatter(pg_formatter)
pg_logger.addHandler(pg_handler)
pg_logger.setLevel(logging.INFO)

class PostgresDatabase(Database):
    def __init__(self, postgres):
        self.host = postgres['host']
        self.port = postgres['port']
        self.user = postgres['user']
        self.password = postgres['password']
        self.dbname = postgres['dbname']
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname
            )
            pg_logger.info("PostgreSQL connection established.")
        except Exception as e:
            pg_logger.error(f"Failed to connect to PostgreSQL database: {e}", exc_info=True)
            raise e

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            pg_logger.info("PostgreSQL connection closed.")

    def execute_query(self, query, params=None):
        if self.connection is None:
            self.connect()
        try:
            with self.connection.cursor() as cursor:
                pg_logger.debug(f"Executed query: {query} with params: {params}")
                cursor.execute(query, params)
                if query.strip().lower().startswith("select"):
                    results = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    return results, column_names
                self.connection.commit()
                pg_logger.info("Query committed successfully.")
        except Exception as e:
            self.connection.rollback()
            pg_logger.error(f"Failed to execute query: {query} with params: {params}. Error: {e}", exc_info=True)
            raise e

    def execute_select(self, procedure_name, params=None):
        if self.connection is None:
            self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.callproc(procedure_name, params)
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                pg_logger.info(f"Stored procedure executed: {procedure_name} with params: {params}")
                return results, column_names
        except Exception as e:
            self.connection.rollback()
            pg_logger.error(f"Failed to execute select procedure: {procedure_name} with params: {params}. Error: {e}", exc_info=True)
            raise e

    def execute_batch(self, procedure_name, records):
        if self.connection is None:
            self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"CALL {procedure_name}(%s)", [json.dumps(records)])
                self.connection.commit()
                pg_logger.info(f"Batch procedure executed: {procedure_name} with {len(records)} records.")
        except Exception as e:
            self.connection.rollback()
            pg_logger.error(f"Failed to execute batch operation: {procedure_name}. Error: {e}", exc_info=True)
            raise e

    def insert_dataframe_to_table(self, df, table_name):
        records = df.to_dict('records')
        columns = [to_snake_case(col) for col in df.columns.tolist()]
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"

        try:
            with self.connection.cursor() as cursor:
                psycopg2.extras.execute_values(
                    cursor, insert_query, [tuple(record[col] for col in df.columns) for record in records]
                )
                self.connection.commit()
                pg_logger.info(f"Inserted {len(records)} records into table: {table_name}")
        except Exception as e:
            self.connection.rollback()
            pg_logger.error(f"Failed to insert records into {table_name}: {e}", exc_info=True)
            raise e
        
def to_snake_case(name):
    return str(name).replace(" ", "_").lower()
        
if __name__ == "__main__":
    postgres = {
        'host': 'dev02',
        'port': 5432,
        'user': 'dev',
        'password': 'Alpha909Time',
        'dbname': 'dvirc_bgs'
    }
    
    db = PostgresDatabase(postgres)

    db.connect()
    
    select_query = "SELECT * FROM repository.request_file where id = 179"
    results = db.execute_query(select_query)
    print(results)

    procedure_name = 'select_request_file_by_id'
    procedure_params = (179,)  # Example parameter
    results = db.execute_select(procedure_name, procedure_params)
    print(results)

    db.disconnect()
