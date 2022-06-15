# 基于fastapi封装的api模板

## version
python 3.9

## 安装库
pip install -r requirement.txt

## mysql连接
```python
path:// app/setting.py

SQLALCHEMY_DATABASE_URL = 'mysql+mysqlconnector://root:root@localhost/logistics?charset=utf8'

path:// app/sql_app/database.py

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
```

## 本地运行
```shell
python app_run.py
```

## docker run
```shell
docker build -t fastapi_template:latest .

docker run -it -p 9000:9000 fastapi_template
```

## 预览
http://127.0.0.1:9000/docs
