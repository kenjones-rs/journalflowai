# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import json
import psycopg2
import psycopg2.extras
from cai_database import Database

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
        except Exception as e:
            print(f"Failed to connect to PostgreSQL database: {e}")

    def execute_query(self, query, params=None):
        if self.connection is None:
            self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().lower().startswith("select"):
                    results = cursor.fetchall()
                    return results
                self.connection.commit()
        except Exception as e:
            print(f"Failed to execute query: {e}")
            self.connection.rollback()

    def execute_select(self, procedure_name, params=None):
        if self.connection is None:
            self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.callproc(procedure_name, params)
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                return results, column_names
        except Exception as e:
            print(f"Failed to execute select procedure: {e}")
            self.connection.rollback()

    def execute_batch(self, procedure_name, records):
        if self.connection is None:
            self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"CALL {procedure_name}(%s)", [json.dumps(records)])
                self.connection.commit()
        except Exception as e:
            print(f"Failed to execute batch operation: {e}")
            self.connection.rollback()

    def insert_dataframe_to_table(self, df, table_name):
        # Convert DataFrame to list of tuples
        records = df.to_dict('records')
        columns = [to_snake_case(col) for col in df.columns.tolist()]

        # Generate the SQL query
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"

        # Use psycopg2 to execute the batch insert
        try:
            with self.connection.cursor() as cursor:
                psycopg2.extras.execute_values(
                    cursor, insert_query, [tuple(record[col] for col in df.columns) for record in records]
                )
                self.connection.commit()
        except Exception as e:
            print(f"Failed to insert records into {table_name}: {e}")
            self.connection.rollback()
            raise e
        
    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

def to_snake_case(name):
    return name.replace(" ", "_").lower()
        
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
