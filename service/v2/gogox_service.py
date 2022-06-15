import time
import requests
from sql_app.crud import find_secret_key
from utils import creat_or_update_logistics
from sql_app.schemas import CreateOrderPayload


class GogoxService:
    def get_token(self):
        url = "https://stag-hk-api.gogox.com/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": GOGOX_CLIENT_ID,
            "client_secret": GOGOX_CLIENT_SECRET
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers).json()
        return response.get("access_token")

    def search_router(self, db, tenant_id: str, tracking_number: str, id=None, *args, **kwargs) -> dict:
        """
        获取快递信息
        :param db:
        :param tenant_id: 租户id
        :param id: 雪花id
        :param tracking_number: 物流单号
        :return: 快递信息
        """
        key, secret = find_secret_key(db, tenant_id, "gogox")
        if not key or not secret:
            return {'code': 200, 'message': 'failure', 'data': {'success': False, 'errorMessage': "未配置秘钥！"}}
        url = f"https://stag-hk-api.gogox.com/delivery/orders/{tracking_number}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.get_token()}"
        }
        info = {'origin_info': {}}
        message_list = []
        info['status'] = True
        info['origin_info']['weblink'] = 'https://www.gogox.com/hk/'
        info['origin_info']['carrier_code'] = 'gogox'
        info.update({'carrier_code': 'gogox', 'tracking_number': tracking_number})
        creat_or_update_logistics(db, id, info)
        response = requests.request("POST", url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            message_list.append({
                'Date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'StatusDescription': data.get("destinations", "not_delivered")
            })
            info['origin_info']['trackinfo'] = message_list
            info.update({'success': True})
            return {'code': 200, 'message': 'success', 'data': info}
        return {'code': 200, 'message': 'failure', 'data': {'success': False, 'errorMessage': 'Not Found'}}

    def create_order(self, payload: CreateOrderPayload, **kwargs):
        url = "https://stag-hk-api.gogox.com/transport/orders"
        sender: str = payload.sendContact
        delivery_address: str = payload.deliveryAddress
        sender_phone: str = payload.sendMobile
        recipient: str = payload.deliveryContact
        shipping_address: str = payload.deliveryAddress
        recipient_phone: str = payload.deliveryMobile
        payload = data = {
            "pickup": {
                "location": {
                    "lat": 22.3353139,
                    "lng": 114.1758402
                },
                "contact": {
                    "name": "Michal",
                    "phone_number": "+660923447588"
                },
                "name": "martin",
                "street_address": "Jl. Perum Dasana",
                "floor_or_unit_number": "603"
            },
            "destinations": [
                {
                    "location": {
                        "lat": 22.2812946,
                        "lng": 114.159861
                    },
                    "contact": {
                        "name": "Karen",
                        "phone_number": "+660923447575"
                    },
                    "name": "Karen",
                    "street_address": "Statue Square, Des Voeux Rd Central, Central",
                    "floor_or_unit_number": "+660923447575"
                }
            ],
            "vehicle_type": "mudou",
            "delivery_type": "speed",  # one of: same_day_day, speed, instant, same_day_night
            "package": {
                "weight": "1.2",
                "height": "1.6",
                "length": "1.3",
                "width": "1.4",
                "content": "2.49"
            },
            "payment_method": "prepaid_wallet"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_token()}"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            data = response.json()
            order_id = data.get("id")
            uuid = data.get("uuid")
