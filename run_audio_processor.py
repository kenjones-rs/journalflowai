from cai_postgres_database import PostgresDatabase
from cai_transcriber_factory import create_transcriber
from cai_repository import Repository
from cai_config_repository import ConfigRepository
from cai_audio_message_repository import AudioMessageRepository
from cai_llm_usage_repository import LLMUsageRepository
from cai_audio_processor import AudioProcessor

if __name__ == "__main__":

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
    config_repo = ConfigRepository(db)
    audio_repo = AudioMessageRepository(db)
    llm_usage_repo = LLMUsageRepository(db)

    # Fetch default transcriber config
    config = config_repo.get_transcriber(is_default=True)
    class_name = config[0]["class_name"]

    # Instantiate via factory
    transcriber = create_transcriber(class_name)

    # Run
    processor = AudioProcessor(config_repo, audio_repo, llm_usage_repo, transcriber)
    processor.run()

