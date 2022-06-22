from fastapi import Query, Path
from pydantic import BaseModel
from typing import Optional, List


class PickUp(BaseModel):
    id: Optional[str] = Query(default=None, description='编号')
    address: Optional[str] = Query(default=None, description='自提地址')
    status: Optional[str] = Query(default=None, description='状态')
    updated_at: Optional[str] = Query(default=None, description='更新时间')
    message: Optional[str] = Query(default=None, description='请求结果')


# 自提物流查询响应
class PickUpResponse(BaseModel):
    code: int = Query(default=200)
    message: str = Query(default='success')
    data: PickUp = Query(default={})


# 自提物流状态修改
class PickUpStatusPayload(BaseModel):
    status: str = Path(default='', description='状态代码{0:未取货,1:已取货,2:订单取消}')


# 自提物流下单
class PickUpAddressPayload(BaseModel):
    address: str = Path(default='', description='自提地址')


class CargoList(BaseModel):
    name: Optional[str] = Query(default=None, description='货物名称')
    unit: Optional[str] = Query(default=None, description='单位， 如个、台、件')
    category: Optional[str] = Query(default=None, description='货物的分类')
    spec: Optional[str] = Query(default=None, description='规格')
    count: Optional[int] = Query(default=None, description='数量')
    length: Optional[float] = Query(default=None, description='长 单位默认为厘米')
    height: Optional[float] = Query(default=None, description='高 单位默认为厘米')
    width: Optional[float] = Query(default=None, description='宽 单位默认为厘米')
    volume: Optional[float] = Query(default=None, description='体积 单位默认为立方厘米')
    weight: Optional[float] = Query(default=None, description='重量 单位:kg')
    goodsCode: Optional[str] = Query(default=None, description='商品编码')
    stateBarCode: Optional[str] = Query(default=None, description='国条码')
    boxNo: Optional[str] = Query(default=None, description='箱号')
    snCode: Optional[str] = Query(default=None, description='验货服务SN码')


class PackageList(BaseModel):
    waybillNo: Optional[str] = Query(default=None, description='运单号或子单号')
    boxNo: Optional[str] = Query(default=None, description='箱号')
    length: Optional[float] = Query(default=None, description='包裹长，单位为厘米')
    height: Optional[float] = Query(default=None, description='包裹高，单位为厘米')
    width: Optional[float] = Query(default=None, description='包裹宽，单位为厘米')
    weight: Optional[float] = Query(default=None, description='包裹重量')
    unitWeight: Optional[str] = Query(default=None, description='包裹重量单位，默认为KG')
    volume: Optional[float] = Query(default=None, description='包裹体积')
    unitVolume: Optional[str] = Query(default=None, description='体积单位, 默认立方厘米')


class AdditionServicesPayload(BaseModel):
    name: Optional[str] = Query(default=None, description='增值服务Code')
    value: Optional[str] = Query(default=None, description='增值服务扩展属性')


# 物流-物流下单负载
class CreateOrderPayload(BaseModel):
    orderId: Optional[str] = Path(default='', description='客户订单号。CP须保证订单号唯一。(必须)')
    isGenBillNo: Optional[int] = Query(default=None, description='是否生成运单号， 0为不生成，使用传入的运单号。默认为1(非必须)')
    customId: Optional[str] = Query(default=None, description='月卡账号')
    sendCompany: Optional[str] = Query(default=None, description='寄件方公司名称(非必须)')
    sendContact: Optional[str] = Path(default='', description='寄件方联系人(必须)')
    sendMobile: Optional[str] = Path(default='', description='寄件方联系手机(必须)')
    sendTel: Optional[str] = Query(default=None, description='寄件方联系电话(非必须)')
    sendProvince: Optional[str] = Path(default='', description='寄件方所在省级行政区名称(必须)')
    sendCity: Optional[str] = Path(default='', description='寄件方所在地级行政区名称(必须)')
    sendCounty: Optional[str] = Path(default='', description='寄件人所在县/区级行政区名称(必须)')
    sendAddress: Optional[str] = Path(default='', description='寄件方详细地址(必须)')
    pickUpMode: Optional[int] = Query(default=None, description='取件方式 1. 客户自送 2 上门接货。默认为2上门接货。(非必须)')
    isDoCall: Optional[str] = Path(default='1', description='是否下call，0-不下call，不会通知小哥上门；1-下call，默认2小时内上门，适用于散件，需小哥上门打单的场景。(必须)')
    expectedPickUpTime: Optional[str] = Query(default=None, description='希望上门取件时间。格式：yyyy-MM-dd HH:mm:ss。isDocall=1时有效，其中，预约时间超过晚8点，会自动约成第二天。(非必须)')
    deliveryCompany: Optional[str] = Query(default=None, description='到件方公司名称(非必须)')
    deliveryContact: Optional[str] = Path(default='', description='到件方联系人(必须)')
    deliveryProvince: Optional[str] = Path(default='', description='到件方所在省级行政区名称(必须)')
    deliveryCity: Optional[str] = Path(default='', description='到件方所在地级行政区名称(必须)')
    deliveryCounty: Optional[str] = Path(default='', description='到件方所在县/区级行政区名称(必须)')
    deliveryAddress: Optional[str] = Path(default='', description='到件方详细地址(必须)')
    deliveryMobile: Optional[str] = Path(default='', description='到件方联系手机(必须)')
    deliveryTel: Optional[str] = Query(default=None, description='到件方联系电话(非必须)')
    deliveryEmail: Optional[str] = Query(default=None, description='到件方邮箱地址(非必须)')
    payMethod: Optional[int] = Path(default=1, description='付款方式(邮费)：1.寄方付2.收方付3.第三方付(必须)')
    parcelQuantity: Optional[int] = Query(default=None, description='包裹数，一个包裹对应一个运单号；若包裹数大于1，则返回1个母运单号和N-1个子运单号。(非必须)')
    cargoLength: Optional[float] = Query(default=None, description='客户订单货物总长，单位厘米，精确到小数点后3位，包含子母件。(非必须)')
    cargoWidth: Optional[float] = Query(default=None, description='客户订单货物总宽，单位厘米，精确到小数点后3位，包含子母件。(非必须)')
    cargoHeight: Optional[float] = Query(default=None, description='客户订单货物总高，单位厘米，精确到小数点后3位，包含子母件。(非必须)')
    volume: Optional[float] = Query(default=None, description='订单货物总体积，单位立方厘米，精确到小数点后3位。(非必须)')
    cargoTotalWeight: Optional[float] = Query(default=None, description='订单货物总体积，单位立方厘米，精确到小数点后3位。(非必须)')
    needReturnTrackingNo: Optional[int] = Query(default=None, description='是否返回签回单的运单号(非必须)')
    specialDeliveryTypeCode: Optional[str] = Query(default=None, description='特殊派送类型代码 1:身份验证（要求验证身份证）(非必须)')
    specialDeliveryValue: Optional[str] = Query(default=None, description='特殊派件具体表述 证件类型:证件后8位 如：1:09296231（1表示身份证，暂不支持其他证件）(非必须)')
    deliveryMode: Optional[int] = Query(default=None, description='派送方式： 1. 派送 2.自提 （不传默认为1）(非必须)')
    hasElevator: Optional[int] = Query(default=None, description='是否有电梯（派送端) 1：有 其他：未知(非必须)')
    deliveryResType: Optional[int] = Query(default=None, description='派送预约上门时间类型：1.工作日、双休均可送货 2.仅工作日送货3.仅休息日送货 4.仅周六周日收货 5.仅周一至周六收货 6.仅周一至周五收货(非必须)')
    cargoType: Optional[str] = Query(default=None, description='货物分类， 如家电、家俱等。(非必须)')
    cargoName: Optional[str] = Query(default=None, description='货物名称 如小天鹅洗衣机(非必须)')
    currencyCode: Optional[str] = Query(default=None, description='声明价值的货币类型，默认CNY(非必须)')
    productCode: Optional[str] = Query(default=None, description='SF快运产品类型，参见 快运产品列表。(非必须)')
    originalNumber: Optional[str] = Query(default=None, description='电商原始订单号(非必须)')
    orderSource: Optional[str] = Query(default=None, description='客户订单来源（taobao, tmall,jd,pdd等）(非必须)')
    remark: Optional[str] = Query(default=None, description='备注(非必须)')
    cargoList: List[CargoList] = Path(default=[{"name": "topkee商品"}], description='货物明细(必须)')
    packageList: List[PackageList] = Query(default=None, description='包裹信息(非必须)')
    AdditionServices: List[AdditionServicesPayload] = Query(default=None, description='增值服务 参见AdditionService(非必须)')


class CreateOrderObj(BaseModel):
    orderId: Optional[str] = Query(default=None, description='客户订单号')
    waybillNo: Optional[str] = Query(default=None, description='运单号')


class CreateOrder(BaseModel):
    obj: CreateOrderObj = Query(default={}, description='返回数据')
    success: Optional[bool] = Query(default=True, description='是否成功')
    errorCode: Optional[str] = Query(default=None, description='错误代码')
    errorMessage: Optional[str] = Query(default=None, description='错误描述')


class CreateOrderResponse(BaseModel):
    code: int = Query(default=200)
    message: str = Query(default='success')
    data: CreateOrder = Query(default={})


class CancelOrderObj(BaseModel):
    orderid: Optional[str] = Query(default=None, description='客户订单号')


class CancelOrderResponse(BaseModel):
    obj: CancelOrderObj = Query(default={}, description='返回数据')
    success: Optional[bool] = Query(default=True, description='是否成功')


# new
# ============================================================================
class TrackInfo(BaseModel):
    StatusDescription: str = Query(default='', description='路由节点具体描述')
    Date: str = Query(default='', description='路由节点发生的时间')
    Details: str = Query(default='', description='路由节点发生的地点')
    checkpoint_status: str = Query(default='')
    substatus: str = Query(default='', description='路由节点操作码')


class Logistics(BaseModel):
    id: str = Query(default=None, description='Topkee唯一物流订单号')
    tracking_number: str = Query(default=None, description='物流运单号')
    carrier_code: str = Query(default=None, description='物流商对应的唯一简码')
    weblink: str = Query(default=None, description='物流商的官网的链接')
    phone: str = Query(default=None, description='物流商官网上的电话')
    status: str = Query(default=None, description='物流状态')
    origin_info: List[TrackInfo] = Query(description='路由信息Route的集合', default=None)


# 物流查询响应
class SearchLogisticsResponse(BaseModel):
    code: int
    message: str
    data: Logistics = {}


class CancelLogisticsResponse(BaseModel):
    code: int
    message: str
