from fastapi import APIRouter, Depends
from fastapi import Query, Path
from sql_app.schemas import LogisticsResponse, CreateOrderPayload, CreateOrderResponse
from sql_app.database import get_db
from typing import Optional
from sqlalchemy.orm import Session
from transport import Transport

router = APIRouter(tags=['LogisticsExpress'], prefix="/v1/logistics/express")


@router.get("/{barcode}", summary='物流查询', response_model=LogisticsResponse)
async def get_express(db: Session = Depends(get_db),
                      barcode: str = Path(default=1, description='物流运单号'),
                      carrier_code: Optional[str] = Query(
                          default='',
                          description="物流商对应的唯一简码(Topkee物流:tk-express;顺丰:sf-express;便利带物流:bld-express;德邦物流:deppon)"),
                      ):
    """更多物流公司代码信息地址：https://s.51tracking.com/admin/courier-code.csv。"""
    return Transport.get_transport(barcode, carrier_code, db)


@router.delete("/{barcode}", summary='取消订单', response_model=LogisticsResponse)
async def get_express(barcode: str = Path(default=1, description='物流运单号'),
                      carrier_code: Optional[str] = Query(
                          default='',
                          description="物流商对应的唯一简码(Topkee物流:tk-express;顺丰:sf-express;便利带物流:bld-express;德邦物流:deppon)"),
                      ):
    """更多物流公司代码信息地址：https://s.51tracking.com/admin/courier-code.csv。取消下单仅支持顺丰官方：sf-official"""
    return Transport.delete_transport(barcode, carrier_code)


@router.post("/{carrier_code}", summary='物流下单', response_model=CreateOrderResponse)
async def post(create_order_payload: CreateOrderPayload,
               carrier_code: str = Path(default=1, description="物流商对应的唯一简码(Topkee物流:tk-express;顺丰:sf-express;便利带物流:bld-express;德邦物流:deppon)")):
    """更多物流公司代码信息地址：https://s.51tracking.com/admin/courier-code.csv。"""
    return Transport.post_transport(carrier_code, create_order_payload)
