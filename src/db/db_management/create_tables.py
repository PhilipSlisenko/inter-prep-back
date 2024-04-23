from src.db.engine_session import engine
from src.db.models._base import Base  # Import base
from src.db.models.feedback import Feedback
from src.db.models.qa_session import QASession
from src.db.models.user import User


def create_tables():
    Base.metadata.drop_all(engine)
    # Importing the models is essential for create_all to recognize them
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_tables()
