from cai_audio_message_repository import AudioMessageRepository
from cai_postgres_database import PostgresDatabase
from cai_google_drive_poller import GoogleDrivePoller

if __name__ == "__main__":
    postgres = {
        'host': 'dev02',
        'port': 5432,
        'user': 'dev',
        'password': 'Alpha909Time',
        'dbname': 'journalflowai'
    }

    db = PostgresDatabase(postgres)
    repo = AudioMessageRepository(db)

    poller = GoogleDrivePoller(config_path="./config/config.json", audio_repo=repo)
    poller.poll()
