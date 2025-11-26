from sqlmodel import SQLModel, create_engine
from app.config import settings


# For now use a synchronous SQLModel engine; you can introduce AsyncSession later.
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)


def init_db() -> None:
    """
    Create tables defined on SQLModel metadata.
    """
    SQLModel.metadata.create_all(bind=engine)



