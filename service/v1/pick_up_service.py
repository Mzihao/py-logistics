from utils.utils import time_transition
from sql_app import crud
from utils.utils import response_json


class PickUpService:
    status_map = {
        '0': '未取货',
        '1': '已取货',
        '2': '订单取消'
    }

    @classmethod
    @response_json
    def add_pick_up_order(cls, db: Session, address: str) -> (int, dict):
        """
        新增自提訂單
        :param db: 数据库实例
        :param address: 自提地址
        :return: 自提物流信息
        """
        data_obj = crud.pick_up_create(db, {'address': address, 'status': 0})
        id = data_obj.id
        updated_at = data_obj.created_at
        updated_at = time_transition(updated_at)
        return 200, {'id': id, 'address': address, 'status': cls.status_map['0'], 'updated_at': updated_at}

    @classmethod
    @response_json
    def search_router(cls, db: Session, barcode: str) -> (int, dict):
        """
        獲取自提物流信息
        :param db:
        :param barcode: 自提物流單號
        :return: 自提物流信息
        """
        data_obj = crud.pick_up_find_by_id(db, barcode)
        if not data_obj:
            return {'message': '查无订单'}
        id = data_obj.id
        updated_at = data_obj.updated_at if data_obj.updated_at else data_obj.created_at
        updated_at = time_transition(updated_at)
        address = data_obj.address
        status = data_obj.status
        return 200, {'id': id, 'address': address, 'status': cls.status_map[f'{status}'], 'updated_at': updated_at,}

    @classmethod
    @response_json
    def update_status(cls, db: Session, barcode: str, status: str) -> (int, dict):
        """
        更新物流狀態
        :param db:
        :param barcode: 自提物流單號
        :param status: 物流狀態
        :return: 自提物流信息
        """
        if status not in cls.status_map:
            return 4004, {}
        status, address, updated_at = crud.pick_up_update_status(db, barcode, status)
        updated_at = time_transition(updated_at)
        if not status:
            return 4006, {}
        return 200, {'id': barcode, 'address': address, 'status': cls.status_map[f'{status}'], 'updated_at': updated_at}
