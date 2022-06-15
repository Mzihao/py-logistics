from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database
from settings import SQLALCHEMY_DATABASE_URL

# 创建一个 SQLAlchemy“引擎”
"""
pool_recycle=3600 表示1小时后该连接会被自动回收

pool_pre_ping=True 每次从连接池中拿连接的时候，都会向数据库发送一个类似 select 1的测试查询语句来判断服务器是否正常运行。
当该连接出现 disconnect 的情况时，该连接连同pool中的其它连接都会被回收。
pool_size： 最大连接数
"""
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_size=200, pool_recycle=3600)

# 创建数据库
if not database_exists(engine.url):
    create_database(engine.url, encoding='utf8')

# 创建SessionLocal类, 这个实例将是实际的数据库会话
# autocommit ： 是否自动提交
# autoflush：是否自动刷新并加载数据库
# bind ：绑定数据库引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base类: 创建每个数据库模型或类（ORM 模型）
Base = declarative_base()


def get_db():
    """
    每一个请求处理完毕后会关闭当前连接，不同的请求使用不同的连接
    :return:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
