import time
import requests
from sqlalchemy.orm import Session
from utils.utils import creat_or_update_logistics


class ZeekService:
    def __init__(self):
        self.url = "https://ap1-zeek2door-api.ks-it.co/Index/get_order_log"
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://www.zeek.one',
            'Referer': 'https://www.zeek.one/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        }

    def search_router(self, db: Session, barcode: str, tenant_id: str, id=None) -> (int, dict):
        """
        获取快递信息
        :param db:
        :param barcode: 物流单号
        :param tenant_id: 租户id
        :param id: 订单id
        :return: 快递信息
        """
        info = {}
        message_list = []
        info['weblink'] = 'https://www.zeek.one/hk'
        info['carrier_code'] = 'zeek'
        payload = {'order_sn': barcode, 'language': 'zh_HK'}
        info.update({'carrier_code': 'zeek', 'tracking_number': barcode})
        creat_or_update_logistics(db, id, info)
        try:
            response = requests.request("POST", self.url, headers=self.headers, data=payload, files=[]).json()
        except Exception:
            return 500, {}
        if response.get("error", 1) == 0:
            data = response.get("data", [])
            for datum in data:
                if datum.get("detail", ""):
                    message_list.append({
                        'Date': datum.get("addtime", ""),
                        'StatusDescription': datum.get("detail", "")
                    })
        else:
            message_list.append({'Date': time.strftime("%Y-%m-%d %H:%M:%S"), 'StatusDescription': "訂單正在創建"})
        info['origin_info'] = list(reversed(message_list))
        return 200, info
