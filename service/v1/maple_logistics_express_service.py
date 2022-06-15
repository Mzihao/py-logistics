import requests
import re
import time
from lxml import etree
from app.utils import creat_or_update_logistics


class MapleLogisticsExpressService:
    def __init__(self):
        self.url: str = 'http://www.25431010.tw/Search.php'
        self.headers: dict = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'http://www.25431010.tw',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': 'http://www.25431010.tw/Search.php',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.session = requests.session()

    def get_cookie_and_tik(self) -> str:
        """
        获取表单tik
        :return: 表单tik
        """
        res = self.session.get(self.url, headers=self.headers)
        # cookie_jar = res.cookies
        html = res.text
        # cookie_dict = requests.utils.dict_from_cookiejar(cookie_jar)
        # print(cookie_dict)
        pat = '<input name="tik" id="tik" type="hidden" value="(.*?)" />'
        tik = re.compile(pat).findall(html)
        return tik[0]

    @staticmethod
    def get_payload(tik: str, tracking_number: str) -> dict:
        """
        :param tik: 表单tik
        :param tracking_number: 物流单号
        :return: payload post资源
        """
        payload: dict = {
            'tik': tik,
        }
        payload.update({f'BARCODE1': tracking_number})
        return payload

    def fop_rece_ltl_search_router(self, db, tracking_number: str, id=None, *args, **kwargs) -> dict:
        """
        获取快递信息
        :param db:
        :param id: 雪花id
        :param tracking_number: 物流单号
        :return: 快递信息
        """
        if len(tracking_number) != 9 and len(tracking_number) != 10 and len(tracking_number) != 12:
            return {'code': 200, 'message': 'success', 'data': {'success': False, 'errorMessage': '條碼長度不正確'}}
        tik: str = self.get_cookie_and_tik()
        payload: dict = self.get_payload(tik, tracking_number)
        data: str = ''
        for k, v in payload.items():
            data += f'{k}={v}&'
        data = data[:-1]
        res = self.session.post(self.url, headers=self.headers, data=data).text
        logistics_info = res.strip()
        html = etree.HTML(logistics_info)
        state_list = html.xpath('//tr/td')
        state_not_null_list = []
        for state in state_list:
            if state.text:
                state_not_null_list.append(state.text.strip())
        info: dict = dict()
        res_list: list = []
        message_list: list = []
        for index, state in enumerate(state_not_null_list):
            try:
                int(state)
                info.update({'tracking_number': state})
            except Exception as e:
                if '外務已經至寄件人指定地點收到貨件' in state:
                    break
                if state:
                    res_list.append(state)
        res_list = res_list[:-1]
        if len(res_list) > 1:
            res_list = res_list[2:]
            for i in range(int(len(res_list) / 2)):
                message_list.append(
                    {'Date': res_list[2 * i].replace('/', '-'), 'StatusDescription': res_list[2 * i + 1]})
        else:
            message_list = [{'Date': time.strftime("%Y-%m-%d %H:%M:%S"), 'StatusDescription': res_list[0]}]
        info.update({'carrier_code': 'bld-express'})
        creat_or_update_logistics(db, id, info)
        info['origin_info'] = {}
        info['status'] = 'notfound' if res_list[0] == '查無條碼(6週)' else ''
        info['origin_info']['weblink'] = 'http://www.25431010.tw/Search.php'
        info['origin_info']['carrier_code'] = 'bld-express'
        info['origin_info']['trackinfo'] = list(reversed(message_list))
        info.update({'success': True})
        return {'code': 200, 'message': 'success', 'data': info}

# if __name__ == '__main__':
#     b = '125259548621'
#     info = MapleLogisticsExpress()
#     message = info.get_logistics_info(b)
#     print(message)
