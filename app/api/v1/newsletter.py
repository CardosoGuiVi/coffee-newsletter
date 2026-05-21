from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.models.newsletter import Subscriber
from app.schemas.newsletter import SubscribeRequest, SubscribeResponse, StatsResponse, UnsubscribeRequest
from app.services.newsletter import NewsletterService
from app.core.dependencies import get_service


router = APIRouter()


@router.post(
    "/subscribe",
    response_model = SubscribeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscreve um novo email na newsletter."
)
async def subscribe(
    payload: SubscribeRequest,
    service: NewsletterService = Depends(get_service)
) -> Subscriber:
    return await service.register(payload)


@router.get(
    "/stats",
    response_model=StatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Retorna estatísticas da newsletter."
)
async def get_stats(
    service: NewsletterService = Depends(get_service)
) -> StatsResponse:
    return await service.stats()


@router.post(
    "/unsubscribe",
    status_code=status.HTTP_200_OK,
    summary="Desinscreve um email da newsletter."
)
async def unsubscribe(
    payload: UnsubscribeRequest,
    service: NewsletterService = Depends(get_service)
) -> JSONResponse:
    return await service.unregister(payload)
