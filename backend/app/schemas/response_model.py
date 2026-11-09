from pydantic import BaseModel
from typing import List, Optional


class FAQResponse(BaseModel):
    """
    Healthcare FAQ Response
    """

    status: str

    answer: str

    session_id: str

    follow_up_questions: Optional[List[str]] = None

    disclaimer: Optional[str] = (
        "This information is for educational purposes only and "
        "should not replace professional medical advice."
    )