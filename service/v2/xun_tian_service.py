import requests
from app.utils import creat_or_update_logistics


class XunTianService:
    def __init__(self):
        self.url: str = 'http://xtl.itdida.com/itdida-api/track'
        self.headers: dict = {
            'Content-Type': 'application/json'
        }

    def login(self):
        login_url = "http://xtl.itdida.com/itdida-api/login"
        payload = "username=13750063787&password=123456"

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Origin': 'http://xtl.itdida.com',
            'Referer': 'http://xtl.itdida.com/itdida-flash/website/landing',
            }

        result = requests.post(login_url, headers=headers, data=payload).json()
        token = result['data']
        return token

    def get_id(self, tracking_number):
        url = f"https://ledii.itdida.com/itdida-api/portal/waybill/list?q={tracking_number}"
        headers = {
            'Accept': 'application/json, text/plain, */*'
        }
        result = requests.get(url, headers=headers).json()
        return result['data'][0]['id']

    def search_router(self, db, tenant_id: str, tracking_number, id: int = None, **kwargs):
        # token = self.login()
        # print(token)
        # url = f"https://ledii.itdida.com/itdida-api/portal/waybill/track?keHuDanHaoList=111&access_token={token}"
        # result = requests.get(url, headers=self.headers).json()
        # print(result)
        try:
            lid = self.get_id(tracking_number)
            url = f"https://xtl.itdida.com/itdida-api/portal/waybill/track/list?billId={lid}"
            result = requests.get(url, headers=self.headers).json()
            data = result.get('data')
            info = {}
            message_list: list = []
            if data:
                for i in data:
                    message_list.append(
                        {'Date': i['detail'], 'StatusDescription': i['time']}
                    )
            info.update({'carrier_code': 'xtl-express', 'tracking_number': tracking_number})
            creat_or_update_logistics(db, id, info)
            info['origin_info'] = {}
            info['status'] = True
            info['origin_info']['weblink'] = 'http://xtl.itdida.com/itdida-flash/website/landing'
            info['origin_info']['carrier_code'] = 'xtl-express'
            info['origin_info']['trackinfo'] = message_list
            info.update({'success': True})
            return {'code': 200, 'message': 'success', 'data': info}
        except Exception as e:
            return {'code': 200, 'message': 'success', 'data': {'success': False, 'errorMessage': '请求错误！'}}
