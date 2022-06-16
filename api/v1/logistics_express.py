from fastapi import APIRouter, Depends, Security
from fastapi import Query, Path
from fastapi.security import APIKeyHeader
from settings import TOKEN_LIST
from sql_app.schemas import SearchLogisticsResponse, CancelLogisticsResponse, CreateOrderPayload, CreateOrderResponse
from sql_app.database import get_db
from sqlalchemy.orm import Session
from transport import Transport
from utils.error_msg import get_error_msg

router = APIRouter(tags=['LogisticsExpress'], prefix="/v1/logistics/express")


@router.get("/{barcode}", summary='物流查询', response_model=SearchLogisticsResponse)
def search(
        db: Session = Depends(get_db),
        barcode: str = Path(default=1, description='物流运单号'),
        tenant_id: str = Query(default="", description="租户id"),
        carrier_code: str = Query(default='', description="物流商对应的唯一简码"),
        api_key_header: str = Security(APIKeyHeader(name='token', auto_error=False)),
):
    if api_key_header in TOKEN_LIST:
        return Transport.get_transport(db, barcode, tenant_id, carrier_code)
    else:
        return {"code": 1006, "message": get_error_msg(1006), "data": {}}


@router.delete("/{barcode}", summary='取消订单', response_model=CancelLogisticsResponse)
def cancel(
        barcode: str = Path(default=1, description='物流运单号'),
        carrier_code: str = Query(default='', description="物流商对应的唯一简码"),
        api_key_header: str = Security(APIKeyHeader(name='token', auto_error=False)),
):
    if api_key_header in TOKEN_LIST:
        return Transport.delete_transport(barcode, carrier_code)
    else:
        return {"code": 1006, "message": get_error_msg(1006), "data": {}}


@router.post("/{carrier_code}", summary='物流下单', response_model=CreateOrderResponse)
def create(
        create_order_payload: CreateOrderPayload,
        carrier_code: str = Path(default=None, description="物流商对应的唯一简码"),
        api_key_header: str = Security(APIKeyHeader(name='token', auto_error=False)),
):
    if api_key_header in TOKEN_LIST:
        return Transport.post_transport(carrier_code, create_order_payload)
    else:
        return {"code": 1006, "message": get_error_msg(1006), "data": {}}
