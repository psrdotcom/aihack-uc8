# database.py
import os
from sqlmodel import create_engine, SQLModel, Session

# Use a real database URL in production
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://your_user:your_password@your_aurora_endpoint/myappdb"
).replace("postgresql://", "postgresql+psycopg://")

# The 'connect_args' is needed for SQLite, but not for PostgreSQL.
# For PostgreSQL, you can remove it.
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    # This function creates all tables defined by SQLModel models
    # that are subclasses of SQLModel. It's good to run this once at startup.
    SQLModel.metadata.create_all(engine)

# Dependency function to get a database session
def get_session():
    with Session(engine) as session:
        yield session