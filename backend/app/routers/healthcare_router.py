from fastapi import APIRouter, HTTPException
from app.config.settings import settings
logger = settings.get_logger()

from app.schemas.request_model import FAQRequest
from app.schemas.response_model import FAQResponse
from app.services.healthcare_service import HealthcareService


router = APIRouter()

healthcare_service = HealthcareService()


@router.post(
    "/faq",
    response_model=FAQResponse,
    summary="Healthcare FAQ Chatbot"
)
async def healthcare_faq(
    request: FAQRequest
):

    try:

        logger.info(
            f"Healthcare FAQ Request Received | "
            f"Session={request.session_id}"
        )

        response = await healthcare_service.ask_question(
            question=request.question,
            session_id=request.session_id
        )

        logger.success(
            f"Healthcare FAQ Request Processed | "
            f"Session={request.session_id}"
        )

        return FAQResponse(
            status="success",
            answer=response["answer"],
            session_id=request.session_id,
            follow_up_questions=response.get(
                "follow_up_questions",
                []
            ),
            confidence_score=response.get(
                "confidence_score",
                0.0
            ),
            disclaimer=(
                "This information is for educational "
                "purposes only and should not replace "
                "professional medical advice."
            ),
            metadata=response.get(
                "metadata",
                {}
            )
        )

    except ValueError as ex:

        logger.warning(
            f"Validation Error: {str(ex)}"
        )

        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )

    except Exception as ex:

        logger.exception(
            f"Healthcare Router Error: {str(ex)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )