# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

class Database:
    def __init__(self, host, port, user, password, dbname):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.connection = None

    def connect(self):
        raise NotImplementedError("Subclasses should implement this method")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=None):
        raise NotImplementedError("Subclasses should implement this method")
    
    def execute_batch(self, procedure_name, records):
        raise NotImplementedError("Subclasses should implement this method")
