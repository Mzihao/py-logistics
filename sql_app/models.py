import time
from sonyflake import SonyFlake
from sqlalchemy import Column, Integer, String, BigInteger
from .database import Base


class Logistics(Base):
    __tablename__ = 'logistics'

    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, default=lambda: SonyFlake().next_id())
    tracking_number = Column(String(100), nullable=False)
    carrier_code = Column(String(50))
    created_at = Column(Integer, nullable=False, default=lambda: int(time.time()))


class PickUp(Base):
    __tablename__ = 'pick_up'

    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, default=lambda: SonyFlake().next_id())
    address = Column(String(500), nullable=False)
    status = Column(Integer, nullable=False)
    created_at = Column(Integer, nullable=False, default=lambda: int(time.time()))
    updated_at = Column(Integer, onupdate=lambda: int(time.time()))
