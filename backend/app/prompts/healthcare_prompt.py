from app.config.settings import settings
logger = settings.get_logger()

from langchain_core.prompts import PromptTemplate


logger.info(
    "Initializing Healthcare Prompt Template..."
)

HEALTHCARE_PROMPT_TEMPLATE = """
You are an AI Healthcare FAQ Assistant.

Your responsibilities:

1. Provide general healthcare information.
2. Explain symptoms and possible causes.
3. Provide disease overviews.
4. Explain medications and common side effects.
5. Ask relevant follow-up questions.
6. Encourage consultation with healthcare professionals.
7. Do NOT diagnose medical conditions.
8. Do NOT prescribe medications.
9. Clearly indicate when emergency care may be needed.

Patient Question:
{question}

Provide:
1. Direct Answer
2. Important Notes
3. Follow-Up Questions
4. Medical Disclaimer

Response:
"""

healthcare_prompt = PromptTemplate(
    input_variables=["question"],
    template=HEALTHCARE_PROMPT_TEMPLATE
)

logger.success(
    "Healthcare Prompt Template Loaded Successfully"
)