from contextlib import asynccontextmanager
from fastapi import Depends, status, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.config import settings
from src.core.database import get_db_session, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"[FATAL] Database connection failed at startup: {e}")
        raise e
    yield

    await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)


@app.get("/health", tags=["System Probe"], status_code=status.HTTP_200_OK)
async def health_check(session: AsyncSession = Depends(get_db_session)):
    """Verifies that the API service and PostgreSQL connection pool are healthy."""
    result = await session.execute(text("SELECT 1"))
    scaler_val = result.scalar()

    return JSONResponse(
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "database_connection": scaler_val == 1,
        }
    )
