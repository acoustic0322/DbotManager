from sqlalchemy import create_engine

DB_USER = "root"
DB_PASSWORD = "abcd1234"
DB_HOST = "203.137.53.205"
DB_PORT = "3306"
DB_NAME = "d_bot"

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)