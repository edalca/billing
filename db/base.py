import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Ensure the 'data' directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 2. Define the database URL pointing to the new directory
# Usando un nombre mucho más corto y limpio
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATA_DIR}/app.db"

# 3. Create Engine and SessionLocal
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Declarative Base for models
Base = declarative_base()