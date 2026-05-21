from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.newsletter import NewsletterService


async def get_service(db: AsyncSession = Depends(get_session)) -> NewsletterService:
    return NewsletterService(db)
