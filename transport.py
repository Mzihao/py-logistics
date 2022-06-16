from utils.platform_entity import cancel_platform_map, create_platform_map, search_platform_map
from utils.utils import lazy_import, query_carrier_code, response_json


class Transport:
    @classmethod
    @response_json
    def get_transport(cls, db, barcode, tenant_id, carrier_code) -> (int, dict):
        """
        物流查询
        :param db: 数据库实例
        :param barcode: 物流单号
        :param tenant_id: 租户id
        :param carrier_code: 物流公司代码
        :return: 物流信息
        """
        if not carrier_code:
            carrier_code, tracking_number = query_carrier_code(db, barcode)
        try:
            service_name = search_platform_map[carrier_code]
            logistics_class = lazy_import(service_name)
            service = logistics_class()
            code, data = service.search_router(db, barcode, tenant_id)
            return code, data
        except KeyError:
            return 4003, {}

    @classmethod
    @response_json
    def post_transport(cls, carrier_code, payload):
        """
        物流下单
        :param carrier_code: 物流公司代码
        :param payload: 物流信息
        :return: 下单结果
        """
        try:
            service_name = create_platform_map[carrier_code]
            logistics_class = lazy_import(service_name)
            service = logistics_class()
            code, data = service.create_order(payload)
            return code, data
        except KeyError:
            return 4003, {}

    @classmethod
    def delete_transport(cls, carrier_code, tracking_number):
        """
        取消订单
        :param carrier_code: 物流公司代码
        :param tracking_number: 物流单号
        :return: 订单取消结果
        """
        try:
            service_name = cancel_platform_map[carrier_code]
            logistics_class = lazy_import(service_name)
            service = logistics_class()
            result = service.cancel_order(tracking_number)
            return result
        except KeyError:
            return {'code': 200, 'message': 'success',
                    'data': {'success': False, 'errorCode': 'unknown', 'errorMessage': '未知物流平台，请检查后再重试!'}}
