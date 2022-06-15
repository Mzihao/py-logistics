import time
import requests
from app.utils import creat_or_update_logistics


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

    def search_router(self, db, tenant_id: str, tracking_number: str, id=None, *args, **kwargs) -> dict:
        """
        获取快递信息
        :param db:
        :param id: 雪花id
        :param tracking_number: 物流单号
        :return: 快递信息
        """
        info = {'origin_info': {}}
        message_list = []
        info['status'] = True
        info['origin_info']['weblink'] = 'https://www.zeek.one/hk'
        info['origin_info']['carrier_code'] = 'zeek'
        payload = {'order_sn': tracking_number, 'language': 'zh_HK'}
        info.update({'carrier_code': 'zeek', 'tracking_number': tracking_number})
        creat_or_update_logistics(db, id, info)
        try:
            response = requests.request("POST", self.url, headers=self.headers, data=payload, files=[]).json()
        except Exception:
            return {'code': 200, 'message': 'success', 'data': {'success': False, 'errorMessage': 'zeek服务器错误！'}}
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
        info['origin_info']['trackinfo'] = list(reversed(message_list))
        info.update({'success': True})
        return {'code': 200, 'message': 'success', 'data': info}
