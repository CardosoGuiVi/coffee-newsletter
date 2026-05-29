from fastapi import APIRouter, status, Depends, HTTPException

from apps.api.schemas.newsletter import SubscribeRequest, SubscribeResponse, StatsResponse, UnsubscribeRequest
from apps.api.dependencies.newsletter import get_service
from packages.database.models.newsletter import Subscriber
from packages.newsletter.services.subscription import SubscriptionService
from packages.newsletter.exceptions import (
    EmailAlreadySubscribed,
    SubscriptionCooldownError,
    SubscriberNotFound,
)


router = APIRouter()


@router.post(
    "/subscribe",
    response_model = SubscribeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscreve um novo email na newsletter."
)
async def subscribe(
    payload: SubscribeRequest,
    service: SubscriptionService = Depends(get_service)
) -> Subscriber:
    try:
        return await service.register(payload)
    except EmailAlreadySubscribed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        )
    except SubscriptionCooldownError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You must wait 48 hours after unsubscribing."
        )

@router.get(
    "/stats",
    response_model=StatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Retorna estatísticas da newsletter."
)
async def get_stats(
    service: SubscriptionService = Depends(get_service)
) -> StatsResponse:
    return await service.stats()


@router.post(
    "/unsubscribe",
    status_code=status.HTTP_200_OK,
    summary="Desinscreve um email da newsletter."
)
async def unsubscribe(
    payload: UnsubscribeRequest,
    service: SubscriptionService = Depends(get_service)
) -> bool:
    try:
        return await service.unregister(payload)
    except SubscriberNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found."
        )
