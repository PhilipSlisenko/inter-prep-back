from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import config

CONNECT_TO_SCHEMA = "inter-test"

engine = create_engine(
    config["db_connection_string"],
    connect_args={
        # "check_same_thread": False,  # needed for SQLite, remove for other databases
        "options": f"-c search_path={CONNECT_TO_SCHEMA}"
    },
    # echo=True,
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
