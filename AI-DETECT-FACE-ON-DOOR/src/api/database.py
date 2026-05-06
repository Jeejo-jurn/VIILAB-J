import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------
# Connection — MySQL ถ้ามี DB_URL ใน .env, fallback SQLite
# ------------------------------------------------------------
DB_URL = os.getenv("DB_URL")

def _make_sqlite_engine():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATH = os.path.join(BASE_DIR, "data", "door_access.db")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    print("[DB] Using SQLite fallback:", DB_PATH)
    return create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


if DB_URL:
    # สร้าง database อัตโนมัติถ้ายังไม่มี
    try:
        import pymysql
        from urllib.parse import urlparse
        parsed = urlparse(DB_URL.replace("mysql+pymysql://", "mysql://"))
        _conn = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password or "",
        )
        _db_name = parsed.path.lstrip("/")
        with _conn.cursor() as _cur:
            _cur.execute(f"CREATE DATABASE IF NOT EXISTS `{_db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        _conn.close()
        engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=3600, echo=False)
    except Exception as _e:
        print(f"[DB] Warning: MySQL unavailable ({_e}), falling back to SQLite")
        engine = _make_sqlite_engine()
else:
    engine = _make_sqlite_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ------------------------------------------------------------
# Models
# ------------------------------------------------------------

class AccessLog(Base):
    __tablename__ = "access_logs"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(100), nullable=False, index=True)
    status      = Column(String(30), nullable=False, default="unknown", index=True)
    similarity  = Column(Float, default=0.0)
    is_live     = Column(Boolean, default=True)
    timestamp   = Column(DateTime, default=datetime.datetime.utcnow, index=True)



# สร้าง tables อัตโนมัติถ้ายังไม่มี
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
