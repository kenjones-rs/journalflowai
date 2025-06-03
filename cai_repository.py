
# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import json
import logging
from logging.handlers import RotatingFileHandler

# Set up logging for Repository
repo_logger = logging.getLogger('Repository')
repo_handler = RotatingFileHandler('./logs/repository.log', maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
repo_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
repo_handler.setFormatter(repo_formatter)
repo_logger.addHandler(repo_handler)
repo_logger.setLevel(logging.INFO)

class Repository:
    def __init__(self, db):
        self.db = db

    def transaction(self):
        class TransactionContext:
            def __init__(self, connection):
                self.connection = connection

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:
                    self.connection.commit()
                    repo_logger.info("Transaction committed successfully.")
                else:
                    self.connection.rollback()
                    repo_logger.error("Transaction rolled back due to an exception.", exc_info=True)

        return TransactionContext(self.db.connection)

    def upsert_record(self, table, record, schema="scratch"):
        function_name = f"{schema}.upsert_{table}"
        params = tuple(json.dumps(value) if isinstance(value, dict) else value for value in record.values())
        try:
            self.db.execute_query(f"SELECT {function_name}({', '.join(['%s'] * len(params))})", params)
            repo_logger.info(f"Upserted record into {schema}.{table} with params: {record}.")
        except Exception as e:
            repo_logger.error(f"Failed to upsert record into {schema}.{table} with params {record}: {e}", exc_info=True)
            raise

    def update_json_column(self, table, key_columns, json_key, json_value, schema="scratch"):
        function_name = f"{schema}.update_{table}_data"
        key_params = tuple(key_columns.values())
        params = key_params + (json_key, json.dumps(json_value))
        try:
            self.db.execute_query(f"SELECT {function_name}({', '.join(['%s'] * len(params))})", params)
            repo_logger.info(
                f"Updated JSON column in table '{schema}.{table}' for keys {key_columns} with key '{json_key}' and value: {json_value}."
            )
        except Exception as e:
            repo_logger.error(
                f"Failed to update JSON column in table '{schema}.{table}' for keys {key_columns} with key '{json_key}' and value {json_value}: {e}",
                exc_info=True
            )
            raise

    def fetch_record(self, table, filters, schema="scratch"):
        function_name = f"{schema}.get_{table}"
        params = tuple(filters.values())
        try:
            results, columns = self.db.execute_select(function_name, params)
            repo_logger.info(f"Fetched records from {schema}.{table} with filters {filters}.")
            return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            repo_logger.error(f"Failed to fetch records from {schema}.{table} with filters {filters}: {e}", exc_info=True)
            raise

    def fetch_record_custom(self, label, filters=None, schema="scratch"):
        function_name = f"{schema}.get_{label}"
        params = tuple(filters.values()) if filters else None

        try:
            if params:
                repo_logger.debug(f"Executing function: {function_name} with params: {params}")
                results, columns = self.db.execute_select(function_name, params)
            else:
                repo_logger.debug(f"Executing function: {function_name} without params")
                results, columns = self.db.execute_select(function_name)

            repo_logger.info(f"Fetched records using function {function_name} with filters: {filters}")
            return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            repo_logger.error(f"Failed to fetch records using function {function_name} with filters: {filters}: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    from cai_postgres_database import PostgresDatabase

    postgres = {
        'host': 'dev02',
        'port': 5432,
        'user': 'dev',
        'password': 'Alpha909Time',
        'dbname': 'journalflowai'
    }

    db = PostgresDatabase(postgres)
    repo = Repository(db)

    audio_file_name = 'Ken Jones-20250526-163600.mp3'
    record = {
        'filename': audio_file_name,
        'transcription': None,
        'message_type': None,
        'status': None,
        'metadata': None,
        'enrichment': None
    }
    with repo.transaction():
        repo.upsert_record(table='audio_message', record=record, schema='data')

    filters = {
        'message_type': 'unknown',
        'status': 'new'
    }

    results = repo.fetch_record(table='audio_message', filters=filters, schema='data')

    for row in results:
        print(row)

