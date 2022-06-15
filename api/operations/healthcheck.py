from typing import Any
from healthcheck import HealthCheck
from fastapi import APIRouter, Response

router = APIRouter(tags=['healthcheck'])
health = HealthCheck()


@router.get("/healthcheck")
async def healthcheck(response: Response) -> Any:
    message, status_code, headers = health.run()
    response.status_code = status_code
    return message
