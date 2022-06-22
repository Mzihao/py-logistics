from fastapi import APIRouter, Depends, Security
from fastapi import Path
from sql_app.database import get_db
from sql_app.schemas import PickUpResponse, PickUpStatusPayload, PickUpAddressPayload
from sqlalchemy.orm import Session
from service.v1.pick_up_service import PickUpService
from fastapi.security import APIKeyHeader
from settings import TOKEN_LIST
from utils.error_msg import get_error_msg

router = APIRouter(tags=['PickUp'], prefix="/v1/logistics/pickUp")


@router.get("/{barcode}", summary='自提查询', response_model=PickUpResponse, response_model_exclude_unset=True)
def get(
        barcode: str = Path(default=1, description='物流运单号'),
        db: Session = Depends(get_db),
        api_key_header: str = Security(APIKeyHeader(name='token', auto_error=False)),
):
    if api_key_header in TOKEN_LIST:
        return PickUpService.search_router(db, barcode)
    else:
        return {"code": 1006, "message": get_error_msg(1006)}


@router.put("/{barcode}", summary='自提状态修改', response_model=PickUpResponse, response_model_exclude_unset=True)
def put(statusPayload: PickUpStatusPayload,
        barcode: str = Path(default=1, description='物流运单号'),
        db: Session = Depends(get_db),
        api_key_header: str = Security(APIKeyHeader(name='token', auto_error=False)),
        ):
    if api_key_header in TOKEN_LIST:
        return PickUpService.update_status(db, barcode, statusPayload.status)
    else:
        return {"code": 1006, "message": get_error_msg(1006)}


@router.delete("/{barcode}", summary='取消自提订单', response_model=PickUpResponse, response_model_exclude_unset=True)
def delete(
        barcode: str = Path(default=1, description='物流运单号'),
        db: Session = Depends(get_db),
        api_key_header: str = Security(APIKeyHeader(name='token', auto_error=False)),
):
    if api_key_header in TOKEN_LIST:
        return PickUpService.update_status(db, barcode, '2')
    else:
        return {"code": 1006, "message": get_error_msg(1006)}


@router.post("/", summary='自提下单', response_model=PickUpResponse, response_model_exclude_unset=True)
def post(
        addressPayload: PickUpAddressPayload,
        db: Session = Depends(get_db),
        api_key_header: str = Security(APIKeyHeader(name='token', auto_error=False)),
):
    if api_key_header in TOKEN_LIST:
        return PickUpService.add_pick_up_order(db, addressPayload.address)
    else:
        return {"code": 1006, "message": get_error_msg(1006)}
