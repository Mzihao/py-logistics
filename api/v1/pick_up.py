from fastapi import APIRouter, Depends
from fastapi import Path
from sql_app.database import get_db
from sql_app.schemas import PickUpResponse, PickUpStatusPayload, PickUpAddressPayload
from sqlalchemy.orm import Session
from service.v1.pick_up_service import PickUpService

router = APIRouter(tags=['PickUp'], prefix="/v1/logistics/pickUp")


@router.get("/{barcode}", summary='自提查询', response_model=PickUpResponse)
async def get(barcode: str = Path(default=1, description='物流运单号'),
              db: Session = Depends(get_db)):
    return PickUpService.fop_rece_ltl_search_router(db, barcode)


@router.put("/{barcode}", summary='自提状态修改', response_model=PickUpResponse)
async def put(statusPayload: PickUpStatusPayload,
              barcode: str = Path(default=1, description='物流运单号'),
              db: Session = Depends(get_db)):
    return PickUpService.update_status(db, barcode, statusPayload.status)


@router.delete("/{barcode}", summary='取消自提订单', response_model=PickUpResponse)
async def delete(barcode: str = Path(default=1, description='物流运单号'),
                 db: Session = Depends(get_db)):
    return PickUpService.update_status(db, barcode, '2')


@router.post("/", summary='自提下单', response_model=PickUpResponse)
async def post(addressPayload: PickUpAddressPayload,
               db: Session = Depends(get_db)):
    return PickUpService.add_pick_up_order(db, addressPayload.address)

