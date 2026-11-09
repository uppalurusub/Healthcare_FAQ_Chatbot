from fastapi import FastAPI
from app.config.settings import settings
logger = settings.get_logger()

from app.routers.healthcare_router import router


logger.info(
    "Starting Healthcare FAQ Chatbot Application..."
)

app = FastAPI(
    title="Healthcare FAQ Chatbot",
    description="Healthcare FAQ Assistant using AutoGen, LangChain and FastAPI",
    version="1.0.0"
)

app.include_router(
    router,
    prefix="/api/v1"
)

@app.get("/")
async def root():

    logger.info(
        "Root Endpoint Invoked"
    )

    return {
        "application": "Healthcare FAQ Chatbot",
        "version": "1.0.0",
        "status": "running"
    }