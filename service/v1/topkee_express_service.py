import requests
import json
from app.utils import creat_or_update_logistics


class TopkeeExpressService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'Content-Type': 'application/json-patch+json'
        }
        self.get_url = 'http://8004.grcb72b3.8nly52gh.7cc869apps.topkee.com/v1/logistics/checkinrecord/{}'
        self.post_url = 'http://8004.grcb72b3.8nly52gh.7cc869apps.topkee.com/v1/logistics/unit'

    def fop_rece_ltl_search_router(self, db, tracking_number, id=None, **kwargs):
        """
        获取快递信息
        :param tracking_number: 物流单号
        :param id: 雪花id
        :return: 快递信息
        """
        try:
            result = requests.get(self.get_url.format(tracking_number), verify=False).json()
            if result.get('code') == 200:
                info = {'carrier_code': 'tk-express', 'tracking_number': tracking_number}
                creat_or_update_logistics(db, id, info)
                data = result['data']['checkInRecord']
                info['origin_info'] = {}
                info['origin_info']['weblink'] = 'https://topkeemedia.com.hk/'
                info['origin_info']['carrier_code'] = 'tk-express'
                info['origin_info']['trackinfo'] = []
                for datum in data:
                    info['origin_info']['trackinfo'].append(
                        {"StatusDescription": datum['siteInfoDesc'], 'Date': datum['creationTime']})
                info.update({'success': True})
                return info
            return {'code': 200, 'message': 'success',
                    'data': {'success': False, 'errorCode': result.get('code', 'unknown'),
                             'errorMessage': result.get('message', '未知物流平台或查无此单号，请检查后再重试!')}}
        except Exception as e:
            return {'code': 200, 'message': 'success',
                    'data': {'success': False, 'errorCode': 'unknown', 'errorMessage': 'tk-express服务器错误'}}

    def fop_rece_ltl_create_order(self, payload: dict):
        """
        物流下单
        :param payload: 负载信息
        :return: 响应结果
        """
        deliveryAddress = payload['deliveryProvince'] + payload['deliveryCity'] + payload['deliveryCounty'] + payload[
            'deliveryAddress']
        shippingAddress = payload['sendProvince'] + payload['sendCity'] + payload['sendCounty'] + payload['sendAddress']
        cargoName = payload['cargoName']
        post_payload = {'deliveryAddress': deliveryAddress, 'shippingAddress': shippingAddress, 'cargoName': cargoName}
        post_payload.update({"logisticsMark": 1})
        result = requests.post(self.post_url, headers=self.headers, data=json.dumps(post_payload), verify=False).json()
        if result.get('code') == 201:
            obj: dict = dict()
            obj['orderId'] = result['data']['id']
            obj['waybillNo'] = result['data']['logisticsNumber']
            return {'obj': obj, 'success': True}
        return {'success': False, 'errorCode': result.get('code', 'unknown'),
                'errorMessage': result.get('message', '未知物流平台或查无此单号，请检查后再重试!')}
