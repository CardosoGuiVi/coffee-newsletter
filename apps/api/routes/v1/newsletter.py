from fastapi import APIRouter, Depends, HTTPException, Request, status

from apps.api.dependencies.newsletter import get_subscription_service
from apps.api.schemas.newsletter import (
    SubscribeRequest,
    SubscribeResponse,
    UnsubscribeRequest,
    UnsubscribeResponse,
)
from apps.api.security import limiter
from packages.mailer.exceptions import MailerError
from packages.newsletter.exceptions import (
    EmailAlreadySubscribed,
    SubscriberNotFound,
    SubscriptionCooldownError,
)
from packages.newsletter.schemas import StatsResult
from packages.newsletter.services.subscription import SubscriptionService

router = APIRouter()


@router.post(
    "/subscribe",
    response_model=SubscribeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscreve um novo email na newsletter.",
)
@limiter.limit("5/minute")
async def subscribe(
    request: Request,
    payload: SubscribeRequest,
    service: SubscriptionService = Depends(get_subscription_service),
) -> SubscribeResponse:
    try:
        subscriber = await service.register(payload.email)
        return SubscribeResponse.model_validate(subscriber)
    except EmailAlreadySubscribed as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        ) from e
    except SubscriptionCooldownError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You must wait 48 hours after unsubscribing.",
        ) from e
    except MailerError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Subscribed successfully but failed to send welcome email.",
        ) from e


@router.post(
    "/unsubscribe",
    response_model=UnsubscribeResponse,
    status_code=status.HTTP_200_OK,
    summary="Desinscreve um email da newsletter.",
)
@limiter.limit("5/minute")
async def unsubscribe(
    request: Request,
    payload: UnsubscribeRequest,
    service: SubscriptionService = Depends(get_subscription_service),
) -> UnsubscribeResponse:
    try:
        await service.unregister(payload.email)
        return UnsubscribeResponse(message="Unsubscribed successfully.")
    except SubscriberNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found."
        ) from e


@router.get(
    "/stats",
    response_model=StatsResult,
    status_code=status.HTTP_200_OK,
    summary="Retorna estatísticas da newsletter.",
)
@limiter.limit("30/minute")
async def get_stats(
    request: Request,
    service: SubscriptionService = Depends(get_subscription_service),
) -> StatsResult:
    return await service.stats()
