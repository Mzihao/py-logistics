from fastapi import APIRouter, Depends
from fastapi import Query, Path
from sql_app.schemas import V2LogisticsResponse, LogisticsResponse, CreateOrderPayload, CreateOrderResponse
from sql_app.database import get_db
from sqlalchemy.orm import Session
from transport import V2Transport

router = APIRouter(tags=['LogisticsExpress'], prefix="/v2/logistics/express")


@router.get("/{barcode}", summary='物流查询', response_model=V2LogisticsResponse)
def get_express(
        db: Session = Depends(get_db),
        barcode: str = Path(default=1, description='物流运单号'),
        tenant_id: str = Query(default="", description="租户id"),
        carrier_code: str = Query(default='', description="物流商对应的唯一简码")):
    return V2Transport.get_transport(db, barcode, tenant_id, carrier_code)


# @router.delete("/{barcode}", summary='取消订单', response_model=LogisticsResponse)
# def get_express(
#         barcode: str = Path(default=1, description='物流运单号'),
#         carrier_code: str = Query(default='', description="物流商对应的唯一简码")
# ):
#     return Transport.delete_transport(barcode, carrier_code)
#
#
# @router.post("/{carrier_code}", summary='物流下单', response_model=CreateOrderResponse)
# def post(
#         create_order_payload: CreateOrderPayload,
#         carrier_code: str = Path(default=1, description="物流商对应的唯一简码")
# ):
#     return Transport.post_transport(carrier_code, create_order_payload)
