import hashlib
from typing import List
from sqlalchemy.orm import Session
from app.sql_app.models import LogisticsBusiness
from app.sql_app.crud import (
    query_logistics_business,
    tenant_id_platform,
    query_logistics_business_like,
    writer_or_update_secret_key,
    find_secret_key
)


class IndexService:
    @staticmethod
    def add_secret_key(db: Session, data: dict, sign: str, timestamp: int):
        content = f"martin-{int(timestamp/1000)}"
        md5hash = hashlib.md5(content.encode())
        md5 = md5hash.hexdigest() + "a"
        if md5 == sign:
            writer_or_update_secret_key(db, data)
            return {"code": 200, "message": "success", "data": data}
        else:
            return {"code": 403}

    @staticmethod
    def find_logistics_business(db: Session, pageSize: int, pageIndex: int, tenant_id: str):
        key_list = []
        if tenant_id:
            key_list = tenant_id_platform(db, tenant_id)
        data: List[LogisticsBusiness] = query_logistics_business(db, pageSize, pageIndex)
        for datum in data:
            if datum.carrier_code in key_list:
                datum.option = "2"
        return {"code": 200, "message": "success", "data": data, "total": len(data)}

    @staticmethod
    def find_logistics_like(db: Session, keyword: str):
        if keyword == "":
            return {"code": 200, "message": "success", "data": [], "total": 0}
        data = query_logistics_business_like(db, keyword)
        return {"code": 200, "message": "success", "data": data, "total": len(data)}

    @staticmethod
    def find_key(db: Session, tenant_id: str, platform: str):
        return find_secret_key(db, tenant_id, platform)
