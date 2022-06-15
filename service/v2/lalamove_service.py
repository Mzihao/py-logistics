import time
import hashlib
import hmac
import uuid
import requests
# from app.sql_app.schemas import CreateOrderPayload
from app.utils import creat_or_update_logistics
from app.sql_app.crud import find_secret_key


class LalamoveService:
    def get_token(self, secret, timestamp, method, path, body=None):
        if method == "GET":
            raw_signature = f"{timestamp}\r\n{method}\r\n{path}\r\n\r\n"
        else:
            raw_signature = f"{timestamp}\r\n{method}\r\n{path}\r\n\r\n{body}"
        message = bytes(raw_signature, 'utf-8')
        secret = bytes(secret, 'utf-8')
        hash = hmac.new(secret, message, hashlib.sha256)
        return hash.hexdigest()

    def search_router(self, db, tenant_id: str, tracking_number: str, id=None, *args, **kwargs) -> dict:
        """
        获取快递信息
        :param db:
        :param tenant_id: 租户id
        :param id: 雪花id
        :param tracking_number: 物流单号
        :return: 快递信息
        """
        key, secret = find_secret_key(db, tenant_id, "lalamove")
        if not key or not secret:
            return {'code': 200, 'message': 'failure', 'data': {'success': False, 'errorMessage': "未配置秘钥！"}}
        # https://rest.lalamove.com/v3/orders/{id}
        url = f"https://rest.sandbox.lalamove.com/v3/orders/{tracking_number}"
        timestamp = int(time.time() * 1000)
        headers = {
            "Authorization": f"hmac {secret}:{timestamp}:{self.get_token(key, timestamp, 'GET', '/v3/orders/' + tracking_number)}",
            "Market": "HK",
            "Request-ID": str(uuid.uuid1()),
            "Content-Type": "application/json",
        }
        message_list = []
        info = {'origin_info': {}}
        info['origin_info']['weblink'] = 'https://www.lalamove.com/en-hk/'
        info['origin_info']['carrier_code'] = 'lalamove'
        info.update({'carrier_code': 'lalamove', 'tracking_number': tracking_number})
        creat_or_update_logistics(db, id, info)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            message_list.append({
                'Date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'StatusDescription': data["data"]["status"]
            })
            info['origin_info']['trackinfo'] = message_list
            info['status'] = True
            info.update({'success': True})
            return {'code': 200, 'message': 'success', 'data': info}
        return {'code': 200, 'message': 'failure', 'data': {'success': False, 'errorMessage': "Order not found."}}

    # def create_order(self, payload: CreateOrderPayload, **kwargs):
    #     """
    #     物流下单
    #     :param payload:
    #     :return: 响应结果
    #     """
    #     url: str = "https://rest.sandbox.lalamove.com/v3/orders"
    #     timestamp: int = int(time.time() * 1000)
    #     sender: str = payload.sendContact
    #     sender_phone: str = payload.sendMobile
    #     recipient: str = payload.deliveryContact
    #     recipient_phone: str = payload.deliveryMobile
    #     remark: str = payload.remark
    #     quotations = self.get_quotation(payload)
    #     stop_list = []
    #     for stop in quotations.get("stops", []):
    #         stop_list.append(stop.get("stopId"))
    #     body = {
    #         "data": {
    #             "quotationId": quotations["quotationId"],
    #             "sender": {
    #                 "stopId": stop_list[0],
    #                 "name": sender,
    #                 "phone": sender_phone
    #             },
    #             "recipients": [
    #                 {
    #                     "stopId": stop_list[1],
    #                     "name": recipient,
    #                     "phone": recipient_phone,
    #                     "remarks": remark  # 可选
    #                 }
    #             ],
    #         }
    #     }
    #     headers = {
    #         "Authorization": f"hmac {LALAMOVE_KEY}:{timestamp}:{self.get_token(timestamp, 'POST', '/v3/orders', body)}",
    #         "Market": "HK",
    #         "Request-ID": str(uuid.uuid1()),
    #         "Content-Type": "application/json",
    #     }
    #     response = requests.post(url, headers=headers, json=body)
    #     if response.status_code == 201:
    #         data = response.json()
    #         order_id = data["data"]["orderId"]
    #         pass
    #
    # def get_quotation(self, payload: CreateOrderPayload):
    #     url = "https://rest.sandbox.lalamove.com/v3/quotations"
    #     timestamp = int(time.time() * 1000)
    #     shipping_address: str = payload.deliveryAddress
    #     body = {
    #         "data": {
    #             # "scheduleAt": "2020-09-01T14:30:00.00Z",  # 取件时间(UTC时区和ISO 8601格式),可选，默认立即下单
    #             "serviceType": "MOTORCYCLE",  # 车辆类型
    #             "language": "zh_HK",
    #             "stops": [{
    #                 "coordinates": {
    #                     "lat": "22.3353139",
    #                     "lng": "114.1758402"
    #                 },
    #                 "address": shipping_address
    #             }]
    #         }
    #     }
    #     headers = {
    #         "Authorization": f"hmac {LALAMOVE_KEY}:{timestamp}:{self.get_token(timestamp, 'POST', '/v3/quotations', body)}",
    #         "Market": "HK",
    #         "Request-ID": str(uuid.uuid1()),
    #         "Content-Type": "application/json",
    #     }
    #     response = requests.post(url, headers=headers, json=body).json()
    #     data = response.get("data")
    #     return data
