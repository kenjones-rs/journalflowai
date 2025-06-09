from cai_postgres_database import PostgresDatabase
from cai_transcriber_factory import create_transcriber
from cai_repository import Repository
from cai_audio_message_repository import AudioMessageRepository
from cai_audio_processor import AudioProcessor

# Setup
postgres = {
    'host': 'dev02',
    'port': 5432,
    'user': 'dev',
    'password': 'Alpha909Time',
    'dbname': 'journalflowai'
}

db = PostgresDatabase(postgres)

repo = Repository(db)
audio_repo = AudioMessageRepository(db)

# Fetch default transcriber config
config = repo.fetch_record("transcriber", filters={"is_default": True}, schema="config")
class_name = config[0]["class_name"]

# Instantiate via factory
transcriber = create_transcriber(class_name)

# Run
processor = AudioProcessor(audio_repo, transcriber)
processor.run()
