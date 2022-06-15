from sql_app.models import Logistics, PickUp
from sqlalchemy.orm import Session


def logistics_create(db: Session, data: dict):
    create_data = {'tracking_number': data['tracking_number'],
                   'carrier_code': data.get('carrier_code')}
    logistics = Logistics(**create_data)
    db.add(logistics)
    db.commit()
    return logistics.id


def logistics_update(db: Session, id, message: str):
    logistics = db.query(Logistics).filter_by(id=id).first()
    logistics.message = message
    db.commit()  # 提交保存到数据库中


def logistics_find_by_id(db: Session, id):
    query_result = db.query(Logistics).filter_by(id=id).first()
    return query_result


def logistics_find_by_barcode(db: Session, tracking_number):
    query_result = db.query(Logistics).filter_by(tracking_number=tracking_number).first()
    return query_result


def pick_up_create(db: Session, data: dict):
    pick_up = PickUp(**data)
    db.add(pick_up)
    db.commit()
    return pick_up


def pick_up_find_by_id(db: Session, id):
    query_result = db.query(PickUp).filter_by(id=id).first()
    return query_result


def pick_up_update_status(db: Session, id, status):
    pick = db.query(PickUp).filter_by(id=id).first()
    if not pick:
        return None, None
    pick.status = status
    db.commit()
    return pick.status, pick.address, pick.updated_at
