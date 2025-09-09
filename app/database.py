from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "carelle%402025"
POSTGRES_SERVER = "localhost"  # ou l'adresse IP de votre serveur
POSTGRES_PORT = "5432"
POSTGRES_DB = "SP_db" # Le nom de la base de données que vous avez créée

SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:carelle%402025@localhost:5432/SP_db"
# --- FIN DE LA CONFIGURATION ---

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()