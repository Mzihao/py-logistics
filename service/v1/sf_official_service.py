import requests
import uuid
import hashlib
import json
import time
import base64
from urllib import parse
from utils.utils import creat_or_update_logistics


class SfOfficialService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }
        self.url = 'https://fapi.sf-express.com/fopApiServices/access/sandbox/enter'
        self.partner_id = 'TOPK'
        self.key = 'iULO3R9wjT'
        self.timestamp = int(time.time())

    def fop_rece_ltl_create_order(self, msgData: dict):
        """
        物流下单
        :param msgData:
        :return: 响应结果
        """
        serviceCode: str = 'FOP_RECE_LTL_CREATE_ORDER'
        msgData.customId = '7550446467'  # 添加月卡信息
        msgData = dict(msgData)
        addition_list = ['cargoList', 'packageList', 'AdditionServices']
        for addition in addition_list:
            if msgData[addition]:
                for i, msg in enumerate(msgData[addition]):
                    msgData['cargoList'][i] = dict(msg)
        result: dict = json.loads(self.send_post(serviceCode, json.dumps(msgData)).get('apiResultData'))
        return {'code': 200, 'message': 'success', 'data': result}

    def fop_rece_ltl_search_router(self, db, tracking_number: str, id=None, **kwargs):
        """
        轨迹查询
        :param db:
        :param id:
        :param tracking_number: 如果tracking_type=1，则此值为顺丰运单号,如果trackingType=2，则此值为客户订单号,如果有多个单号，以逗号分隔，如”123,124,125”
        :return: 响应结果
        """
        serviceCode = 'FOP_RECE_LTL_SEARCH_ROUTER'
        msgData = {
            'trackingType': 1,
            'trackingNumber': tracking_number,
            'methodType': 1,  # 路由查询类别： 1：标准路由查询
            # 'checkPhoneNo': ''  # checkPhoneNo: 校验电话号码后四位(非必须)
        }
        result: dict = json.loads(self.send_post(serviceCode, json.dumps(msgData)).get('apiResultData'))
        if result.get('success'):
            obj = result.get('obj')
            info = {'carrier_code': 'sf-official', 'tracking_number': tracking_number, 'origin_info': {}}
            creat_or_update_logistics(db, id, info)
            info['origin_info']['weblink'] = 'https://www.sf-express.com/'
            info['origin_info']['carrier_code'] = 'sf-express'
            routeList = obj[0].get('routeList', [])
            if routeList:
                info['origin_info']['trackinfo'] = []
                for route in routeList:
                    info['origin_info']['trackinfo'].append({
                        'Date': route.pop('acceptTime'),
                        'Details': route.pop('acceptAddress'),
                        'StatusDescription': route.pop('remark'),
                        'substatus': route.pop('opcode'),
                    })
            info.update({'success': True})
            return {'code': 200, 'message': 'success', 'data': info}
        return {'code': 200, 'message': 'success',
                'data': {'success': False, 'errorMessage': result.get('errorMessage', '未知错误！')}}

    def fop_rece_address_reachable_check(self, addressType: int, province: str, city: str, district: str = None,
                                         address: str = None):
        """
        地址可达校验
        :param addressType: 1：寄件(用户维度：寄件，小哥维度：收件) 2：收件(用户维度：收件，小哥维度：派件)
        :param province: 省
        :param city: 市
        :param district: 区(非必须)
        :param address: 详细地址(非必须)
        :return: 响应结果
        """
        serviceCode = "FOP_RECE_ADDRESS_REACHABLE_CHECK"
        msgData = {
            'addressType': addressType,
            'province': province,
            'city': city,
        }
        if district:
            msgData.update({'district': district})
        if address:
            msgData.update({'address': address})
        return self.send_post(serviceCode, json.dumps(msgData))

    def fop_rece_ltl_get_order_result(self, orderId: str):
        """
        下单结果查询
        :param orderId: 客户订单号
        :return: 响应结果
        """
        serviceCode = 'FOP_RECE_LTL_GET_ORDER_RESULT'
        msgData = {
            'orderId': orderId,
        }
        return self.send_post(serviceCode, json.dumps(msgData))

    def fop_rece_ltl_query_fee(self, orderId: str):
        """
        费用查询
        :param orderId: 客户订单号
        :return: 响应结果
        """
        serviceCode: str = 'FOP_RECE_LTL_QUERY_FEE'
        msgData: dict = {
            'orderId': orderId,
        }
        return self.send_post(serviceCode, json.dumps(msgData))

    def fop_rece_ltl_cancel_order(self, orderId: str):
        """
        取消订单
        :param orderId 客户订单号
        :return: 响应结果
        """
        serviceCode = 'FOP_RECE_LTL_CANCEL_ORDER'
        msgData = {
            'orderId': orderId,
        }
        result = json.loads(self.send_post(serviceCode, json.dumps(msgData)).get('apiResultData'))
        return {'code': 200, 'message': 'success', 'data': result}

    def fop_rece_ltl_register_router(self, orderId: str, waybillNo: str):
        """
        使用推送服务时，需通过此接口注册运单，并配置回调之后，方可接收到路由推送。
        :param orderId: 客户订单号
        :param waybillNo: 运单号
        :return: 响应结果
        """
        serviceCode = 'FOP_RECE_LTL_REGISTER_ROUTER'
        msgData = {
            'orderId': orderId,
            'waybillNo': waybillNo
        }
        return self.send_post(serviceCode, json.dumps(msgData))

    @staticmethod
    def fop_push_ltl_router(payload: dict):
        """
        轨迹推送(路由推送)
        :param payload:
        :return:
        """
        # orderId = payload.get('orderId')  # 外部订单号 O
        # waybillNo = payload.get('waybillNo')  # 运单号 R
        # acceptTime = payload.get('acceptTime')  # 路由节点发生的时间，格式：YYYY-MM-DD HH24:MM:SS，示例：2012-07-30 09:30:00。 R
        # acceptCity = payload.get('acceptCity')  # 路由节点发生的城市 R
        # remark = payload.get('acceptCity')  # 路由节点具体描述 R
        # opCode = payload.get('opCode')  # 路由节点操作码，常用的有以下：54=上门收件,50=完成揽收,30=装车,31=卸车,204=开始派件,80=已妥投 R
        # stayWhyCode = payload.get(
        #     'stayWhyCode')  # 异常原因代码，如70异常操作码下有很多细分(有天气异常，交通异常…)，常用的有：取消寄件(opCode=70，stayWhyCode=46) R
        # uniqueId = payload.get('uniqueId')  # 路由唯一ID
        return {"errorCode": "", "errorMessage": "", "success": True}

    @staticmethod
    def fop_push_ltl_order_status(payload):
        """
        订单状态推送
        :param payload:
        :return:
        """
        orderId = payload.get('orderId')  # 外部订单号
        waybillNo = payload.get('waybillNo')  # 运单号（生成后会传）
        orderStatus = payload.get('orderStatus')  # 订单状态（00取消，04执行中，05执行完成）
        operateCode = payload.get('operateCode')  # 操作码
        reasonCode = payload.get('reasonCode')  # 异常码
        operateEmpTel = payload.get('operateEmpTel')  # 操作员电话
        operateTime = payload.get('operateTime')  # 操作时间
        operateName = payload.get('operateName')  # 操作员姓名
        return {"errorCode": "", "errorMessage": "", "success": "true"}

    def get_digest(self, msgData):
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

    def send_post(self, serviceCode, msgData):
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
            "msgDigest": self.get_digest(msgData),
        }
        data = parse.urlencode(required)
        res = requests.post(self.url, headers=self.headers, data=data).json()
        return res


if __name__ == '__main__':
    s = SfOfficialService()
    r = s.fop_rece_ltl_create_order({
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
