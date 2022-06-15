import requests
from utils.utils import creat_or_update_logistics


class Tracking51Service:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Tracking-Api-Key": "c169127f-0377-4f4e-bf53-b64566b638bb",
        }
        self.url = 'https://api.51tracking.com/v2/trackings/{}/{}'

    def search_router(self, db, tracking_number: str, id=None, carrier_code: str = None):
        """
        获取快递信息
        :param db:
        :param tracking_number: 物流单号
        :param id: 雪花id
        :param carrier_code: 物流公司代码
        :return: 物流信息
        """
        res = requests.get(self.url.format(carrier_code, tracking_number), headers=self.headers).json()
        code = res['meta']['code']
        data = res.get('data')
        if code == 200 and data:
            creat_or_update_logistics(db, id, data)
            data.update({'success': True})
            return 'success', data
        return 'failure', {'success': False, 'errorMessage': res['meta'].get('message', '未知物流平台或查无此单号，请检查后再重试!')}
