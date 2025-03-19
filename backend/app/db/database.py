from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import getpass

# 獲取當前用戶名
current_user = getpass.getuser()

# 數據庫URL(可通過環境變量配置)
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{current_user}:@localhost/testmanagement")

# 創建SQLAlchemy引擎
engine = create_engine(DATABASE_URL)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建基礎模型類
Base = declarative_base()

# 獲取數據庫會話的依賴
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 