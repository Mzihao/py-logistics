import requests
import uuid
import hashlib
import json
import time
import base64
from urllib import parse
from settings import SF_PARTNER_ID, SF_KEY
from utils.utils import creat_or_update_logistics


class SfOfficialService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }
        self.url = 'https://fapi.sf-express.com/fopApiServices/access/sandbox/enter'
        self.partner_id = SF_PARTNER_ID
        self.key = SF_KEY
        self.timestamp = int(time.time())

    def create_order(self, msgData: dict) -> (int, dict):
        """
        物流下单
        :param msgData: 货物信息
        :return: 响应码
        """
        serviceCode: str = 'FOP_RECE_LTL_CREATE_ORDER'
        msgData.customId = 'xxxxx'  # 添加月卡信息
        msgData = dict(msgData)
        addition_list = ['cargoList', 'packageList', 'AdditionServices']
        for addition in addition_list:
            if msgData[addition]:
                for i, msg in enumerate(msgData[addition]):
                    msgData['cargoList'][i] = dict(msg)
        try:
            result = json.loads(self._send_post(serviceCode, json.dumps(msgData)).get('apiResultData'))
            return 200, result
        except Exception as e:
            return 500, {}

    def search_router(self, db, tenant_id: str, barcode: str, id=None) -> (int, dict):
        """
        获取快递信息
        :param db:
        :param barcode: 物流单号
        :param tenant_id: 租户id
        :param id: 订单id
        :return: 快递信息
        """
        serviceCode = 'FOP_RECE_LTL_SEARCH_ROUTER'
        msgData = {
            'trackingType': 1,
            'trackingNumber': barcode,
            'methodType': 1,  # 路由查询类别： 1：标准路由查询
            # 'checkPhoneNo': ''  # checkPhoneNo: 校验电话号码后四位(非必须)
        }
        result: dict = json.loads(self._send_post(serviceCode, json.dumps(msgData)).get('apiResultData'))
        if result.get('success'):
            obj = result.get('obj')
            info = {'carrier_code': 'sf-official', 'tracking_number': barcode, 'origin_info': {}}
            creat_or_update_logistics(db, id, info)
            info['weblink'] = 'https://www.sf-express.com/'
            info['carrier_code'] = 'sf-express'
            routeList = obj[0].get('routeList', [])
            if routeList:
                info['origin_info'] = []
                for route in routeList:
                    info['origin_info'].append({
                        'Date': route.pop('acceptTime'),
                        'Details': route.pop('acceptAddress'),
                        'StatusDescription': route.pop('remark'),
                        'substatus': route.pop('opcode'),
                    })
            return 200, info
        return 500, {}

    def cancel_order(self, orderId: str) -> (int, dict):
        """
        取消订单
        :param orderId 客户订单号
        :return: 响应结果
        """
        serviceCode = 'FOP_RECE_LTL_CANCEL_ORDER'
        msgData = {
            'orderId': orderId,
        }
        result = json.loads(self._send_post(serviceCode, json.dumps(msgData)).get('apiResultData'))
        return 200, result

    def _get_digest(self, msgData):
        """
        获取数字签名
        :param msgData: 业务数据报文
        :return: 数字签名
        """
        toVerifyText = parse.quote_plus(msgData + str(self.timestamp) + 'iULO3R9wjT')
        m = hashlib.md5()
        m.update(toVerifyText.encode('utf-8'))
        md5Str = m.digest()
        msgDigest = base64.b64encode(md5Str).decode('utf-8')
        return msgDigest

    def _send_post(self, serviceCode, msgData):
        """
        发送post请求
        :param serviceCode: 服务代码
        :param msgData: 业务数据报文
        :return: 响应结果
        """
        required = {
            "partnerID": "TOPK",
            "requestID": f"{uuid.uuid1()}",
            "serviceCode": serviceCode,
            "timestamp": self.timestamp,
            "msgData": msgData,
            "msgDigest": self._get_digest(msgData),
        }
        data = parse.urlencode(required)
        try:
            res = requests.post(self.url, headers=self.headers, data=data).json()
            return res
        except Exception as e:
            print(e)
            return {'apiResultData': ''}


if __name__ == '__main__':
    s = SfOfficialService()
    r = s.create_order({
        "cargoList": [
            {
                "boxNo": "商品下发3",
                "count": 1,
                "height": 6,
                "length": 4,
                "name": "商品下发3",
                "volume": 230000,
                "weight": 26,
                "width": 5
            }
        ],
        "cargoName": "商品下发3 （1件） 商品下发1 （1件）",
        "cargoTotalWeight": 126,
        "cargoTypeCode": "SP635",
        "customId": "7550446467",
        "declaredValue": 4,
        "deliveryAddress": "粤海街道软件产业基地",
        "deliveryCity": "深圳市",
        "deliveryCompany": "深圳市顺丰供应链有限公司旗下分公司快运科技有限公司",
        "deliveryContact": "彭伟",
        "deliveryCounty": "南山区",
        "deliveryMobile": "18025383086",
        "deliveryProvince": "广东省",
        "deliveryTel": "",
        "expectedPickUpTime": "",
        "isGenBillNo": 1,
        "isDoCall": "1",
        "isReturnSignBackRoutelabel": 0,
        "orderId": "EP110757945331731861",
        "parcelQuantity": 2,
        "payMethod": 1,
        "paymentType": 2,
        "remark": "",
        "sendAddress": "翠竹南路5412号",
        "sendCity": "深圳市",
        "sendCompany": "",
        "sendContact": "谢玉",
        "sendCounty": "罗湖区",
        "sendMobile": "15012794320",
        "sendProvince": "广东省",
        "sendTel": ""
    })
