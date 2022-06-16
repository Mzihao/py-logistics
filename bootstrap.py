import logging
import sys
from loguru import logger
from starlette.status import HTTP_403_FORBIDDEN
from sql_app.database import engine, Base
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from settings import TOKEN_LIST
from api.v1 import logistics_express, pick_up
from api.index import index
from api.operations import healthcheck
from extensions.logger import InterceptHandler, format_record


def bootstrap() -> FastAPI:
    app = FastAPI(version='1.0.0',
                  title='Logistics Query API.',
                  description='Logistics Query API.',
                  # dependencies=[Depends(get_api_key)],
                  )
    register_middleware(app)
    register_routes(app)
    init_database()
    init_log()
    return app


async def get_api_key(api_key_header: str = Security(APIKeyHeader(name='token', auto_error=False))):
    if api_key_header in TOKEN_LIST:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


def register_routes(app: FastAPI) -> None:
    app.include_router(router=index.router)
    app.include_router(router=healthcheck.router, prefix="")
    app.include_router(router=logistics_express.router, prefix="")
    app.include_router(router=pick_up.router, prefix="")


def register_middleware(app: FastAPI) -> None:
    # 文档地址：https://fastapi.tiangolo.com/zh/tutorial/cors/
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )


def init_database() -> None:
    # 创建数据表，在此之前应先创建数据库
    Base.metadata.create_all(bind=engine)


def init_log():
    logging.getLogger().handlers = [InterceptHandler()]
    logger.configure(
        handlers=[{"sink": sys.stdout, "level": logging.DEBUG, "format": format_record}])
    # log_dir = os.path.join(os.getcwd(), f'application\log\\{time.strftime("%Y-%m-%d")}.log')
    logger.add('log.log', format="{time} {level} {message}", encoding="utf-8", enqueue=True, retention="7 days")
    # logger.add(log_dir, encoding='utf-8', rotation="9:46")
    logger.debug('日志系统已加载')
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
