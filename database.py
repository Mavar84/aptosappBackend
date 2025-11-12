# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config

# -------------------------------------------------------------------
# 🧩 Lectura de credenciales Supabase desde el archivo .env
# -------------------------------------------------------------------
SUPABASE_URL = config("SUPABASE_URL")
SUPABASE_PORT = config("SUPABASE_PORT", default="6543")
SUPABASE_USER = config("SUPABASE_USER")
SUPABASE_PASSWORD = config("SUPABASE_PASSWORD")
SUPABASE_DATABASE = config("SUPABASE_DATABASE")

# -------------------------------------------------------------------
# 🧠 Construcción automática del string de conexión
# -------------------------------------------------------------------
DATABASE_URL = (
    f"postgresql+psycopg://{SUPABASE_USER}:{SUPABASE_PASSWORD}"
    f"@{SUPABASE_URL}:{SUPABASE_PORT}/{SUPABASE_DATABASE}"
)

# -------------------------------------------------------------------
# ⚙️ Creación del engine (configuración estable para psycopg3)
# -------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # Verifica la conexión antes de usarla
    pool_recycle=1800,           # Recicla conexiones cada 30 min
    pool_size=5,                 # Tamaño del pool razonable
    max_overflow=2,
    connect_args={
        "sslmode": "require",
        "prepare_threshold": None,  # 🚫 Desactiva completamente prepared statements
    },
    echo=False
)

# -------------------------------------------------------------------
# Sesión y base declarativa
# -------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -------------------------------------------------------------------
# Dependencia FastAPI para obtener sesión
# -------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # ⚠️ Cierra la conexión después de cada request
