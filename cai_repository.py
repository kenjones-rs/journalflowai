
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

    def update_json_key_with_version(
        self,
        schema,
        table,
        id_column,
        id_value,
        json_column,
        json_key,
        json_value,
        mode
    ):
        """
        Calls a generalized PostgreSQL function to update a versioned array in a JSONB column.

        :param schema: Schema name (e.g., 'data')
        :param table: Table name (e.g., 'audio_message')
        :param id_column: Primary key column name (e.g., 'id')
        :param id_value: Primary key value
        :param json_column: JSONB column name ('metadata' or 'enrichment')
        :param json_key: Key in the JSONB column to update
        :param json_value: Dictionary with 'value', 'model', and 'timestamp'
        :param mode: 'add' to append, 'replace' to replace highest-version entry
        """
        if not isinstance(json_value, dict):
            raise ValueError("json_value must be a dictionary")

        function_name = f"{schema}.update_json_key_with_version"
        params = (
            schema,
            table,
            id_column,
            id_value,
            json_column,
            json_key,
            json.dumps(json_value),
            mode
        )

        try:
            self.db.execute_query(f"SELECT {function_name}({', '.join(['%s'] * len(params))})", params)
            repo_logger.info(
                f"{mode.upper()} entry under '{json_key}' in '{json_column}' for {schema}.{table} id={id_value}: {json_value}"
            )
        except Exception as e:
            repo_logger.error(
                f"Failed to {mode} entry under '{json_key}' in '{json_column}' for {schema}.{table} id={id_value}: {json_value}. Error: {e}",
                exc_info=True
            )
            raise

    def update_column_value(
        self,
        schema: str,
        table: str,
        id_column: str,
        id_value,
        column_name: str,
        column_value
    ):
        """
        Updates a simple column (non-JSONB) in a PostgreSQL table.

        :param schema: Schema name (e.g., 'data')
        :param table: Table name (e.g., 'audio_message')
        :param id_column: Primary key column name (e.g., 'id')
        :param id_value: Primary key value
        :param column_name: Column name to update (non-JSONB)
        :param column_value: New value to set
        """
        query = f"""
            UPDATE {schema}.{table}
            SET {column_name} = %s
            WHERE {id_column} = %s
        """
        try:
            self.db.execute_query(query, (column_value, id_value))
            repo_logger.info(
                f"Updated {schema}.{table}.{column_name} to '{column_value}' for {id_column} = {id_value}"
            )
        except Exception as e:
            repo_logger.error(
                f"Failed to update {schema}.{table}.{column_name} for {id_column} = {id_value} to '{column_value}'. Error: {e}",
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

    with repo.transaction():
        repo.update_column_value(
            schema="data",
            table="audio_message",
            id_column="id",
            id_value=75,
            column_name="message_type",
            column_value="unknown"
        )
