# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import logging
from logging.handlers import RotatingFileHandler
from cai_repository import Repository

# Set up logging for AudioMessageRepository
audio_logger = logging.getLogger('AudioMessageRepository')
audio_handler = RotatingFileHandler('./logs/audio_message_repository.log', maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
audio_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
audio_handler.setFormatter(audio_formatter)
audio_logger.addHandler(audio_handler)
audio_logger.setLevel(logging.INFO)

class AudioMessageRepository(Repository):
    def get_by_id(self, message_id):
        audio_logger.info(f"Fetching audio_message by id: {message_id}")
        return self.fetch_record("audio_message_by_id", {"id": message_id}, schema="data")

    def get_by_status(self, status):
        audio_logger.info(f"Fetching audio_message by status: {status}")
        return self.fetch_record("audio_message_by_status", {"status": status}, schema="data")

    def get_by_filename(self, filename):
        audio_logger.info(f"Fetching audio_message by filename: {filename}")
        return self.fetch_record("audio_message_by_filename", {"filename": filename}, schema="data")

    def upsert(self, record):
        audio_logger.info(f"Upserting audio_message with data: {record}")
        self.upsert_record("audio_message", record, schema="data")

    def update_status(self, message_id, new_status):
        audio_logger.info(f"Updating status of audio_message id={message_id} to '{new_status}'")
        self.update_column_value(
            schema="data",
            table="audio_message",
            id_column="id",
            id_value=message_id,
            column_name="status",
            column_value=new_status
        )