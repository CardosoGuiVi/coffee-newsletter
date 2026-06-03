from fastapi import APIRouter, status, Depends, HTTPException

from apps.api.schemas.newsletter import SubscribeRequest, SubscribeResponse, UnsubscribeRequest, UnsubscribeResponse
from packages.newsletter.schemas import StatsResult
from apps.api.dependencies.newsletter import get_subscription_service
from packages.newsletter.services.subscription import SubscriptionService
from packages.mailer.exceptions import MailerError
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
    service: SubscriptionService = Depends(get_subscription_service)
) -> SubscribeResponse:
    try:
        subscriber = await service.register(payload.email)
        return SubscribeResponse.model_validate(subscriber)
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
    except MailerError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Subscribed successfully but failed to send welcome email."
        )

@router.get(
    "/stats",
    response_model=StatsResult,
    status_code=status.HTTP_200_OK,
    summary="Retorna estatísticas da newsletter."
)
async def get_stats(
    service: SubscriptionService = Depends(get_subscription_service)
) -> StatsResult:
    return await service.stats()

@router.post(
    "/unsubscribe",
    response_model=UnsubscribeResponse,
    status_code=status.HTTP_200_OK,
    summary="Desinscreve um email da newsletter."
)
async def unsubscribe(
    payload: UnsubscribeRequest,
    service: SubscriptionService = Depends(get_subscription_service)
) -> UnsubscribeResponse:
    try:
        await service.unregister(payload.email)
        return UnsubscribeResponse(message="Unsubscribed successfully.")
    except SubscriberNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found."
        )
