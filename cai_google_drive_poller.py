# Copyright (c) 2025 Claritee Group, LLC. All rights reserved.

import os
import json
import io
import logging
from logging.handlers import RotatingFileHandler
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from cai_audio_message_repository import AudioMessageRepository

# Set up logging for GoogleDrivePoller
gdrive_logger = logging.getLogger('GoogleDrivePoller')
gdrive_handler = RotatingFileHandler('./logs/google_drive_poller.log', maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
gdrive_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
gdrive_handler.setFormatter(gdrive_formatter)
gdrive_logger.addHandler(gdrive_handler)
gdrive_logger.setLevel(logging.INFO)

class GoogleDrivePoller:
    def __init__(self, config_path, audio_repo: AudioMessageRepository):
        with open(config_path, "r") as f:
            config = json.load(f)
        drive_config = config["google_drive"]

        self.service_account_path = drive_config["service_account_path"]
        self.folder_id = drive_config["folder_id"]
        self.audio_repo = audio_repo

        gdrive_logger.info("Initializing GoogleDrivePoller with folder ID %s", self.folder_id)
        self.service = self.authenticate()

    def authenticate(self):
        gdrive_logger.info("Authenticating Google Drive service account")
        creds = service_account.Credentials.from_service_account_file(
            self.service_account_path,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        return build("drive", "v3", credentials=creds)

    def poll(self, download_dir="./audio"):
        os.makedirs(download_dir, exist_ok=True)
        gdrive_logger.info("Polling folder: %s", self.folder_id)

        query = f"'{self.folder_id}' in parents and mimeType contains 'audio/' and trashed = false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])

        for file in files:
            filename = file["name"]
            if not filename.lower().endswith((".mp3", ".wav")):
                gdrive_logger.debug("Skipping non-audio file: %s", filename)
                continue

            gdrive_logger.info("Checking file: %s", filename)
            existing = self.audio_repo.get_by_filename(filename)
            if existing:
                gdrive_logger.info("File %s already exists in database, skipping.", filename)
                continue

            file_path = os.path.join(download_dir, filename)
            self.download_file(file["id"], file_path)

            gdrive_logger.info("Inserting new audio file into database: %s", file_path)
            self.audio_repo.upsert({
                "filename": file_path,
                "transcription": None,
                "message_type": None,
                "status": "new",
                "metadata": {},
                "enrichment": {}
            })

    def download_file(self, file_id, destination_path):
        gdrive_logger.info("Downloading file ID %s to %s", file_id, destination_path)
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            gdrive_logger.debug("Download progress: %d%%", int(status.progress() * 100))
