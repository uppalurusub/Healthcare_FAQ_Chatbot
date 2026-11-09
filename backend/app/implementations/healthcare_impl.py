from app.config.settings import settings
logger = settings.get_logger()

from app.memory.chat_memory import chat_memory
from app.agents.healthcare_agent import healthcare_agent
from app.prompts.healthcare_prompt import healthcare_prompt


class HealthcareImplementation:
    async def process_question(self, question: str, session_id: str) -> dict:
        logger.info(f"Processing Question | Session={session_id}")
        history = chat_memory.get_history(session_id)
        chat_memory.add_user_message(session_id=session_id, message=question)

        # Use the existing healthcare prompt template (previously unused).
        prompt_value = healthcare_prompt.invoke({"question": question})
        prompt_text = prompt_value.to_string()
        answer = await healthcare_agent.ask(prompt_text)

        chat_memory.add_assistant_message(session_id=session_id, message=answer)
        return {
            "answer": answer,
            "follow_up_questions": [
                "Would you like more details?",
                "Do you have additional symptoms?",
            ],
            "confidence_score": 0.95,
            "metadata": {
                "session_id": session_id,
                "history_count": len(history) + 2,
                "llm_usage": healthcare_agent.last_usage,
            },
        }
