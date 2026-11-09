from collections import defaultdict
from typing import List, Dict

from app.config.settings import settings
logger = settings.get_logger()


class ChatMemory:

    def __init__(self):

        logger.info(
            "Initializing Chat Memory"
        )

        self.memory = defaultdict(list)

        logger.success(
            "Chat Memory Initialized Successfully"
        )

    def add_user_message(
        self,
        session_id: str,
        message: str
    ):

        logger.info(
            f"Adding user message | Session={session_id}"
        )

        self.memory[session_id].append(
            {
                "role": "user",
                "content": message
            }
        )

        logger.debug(
            f"User Message Added: {message}"
        )

    def add_assistant_message(
        self,
        session_id: str,
        message: str
    ):

        logger.info(
            f"Adding assistant message | Session={session_id}"
        )

        self.memory[session_id].append(
            {
                "role": "assistant",
                "content": message
            }
        )

        logger.debug(
            f"Assistant Message Added: {message}"
        )

    def get_history(
        self,
        session_id: str
    ) -> List[Dict]:

        logger.info(
            f"Fetching History | Session={session_id}"
        )

        history = self.memory.get(
            session_id,
            []
        )

        logger.debug(
            f"History Count={len(history)}"
        )

        return history

    def clear_history(
        self,
        session_id: str
    ):

        logger.warning(
            f"Clearing History | Session={session_id}"
        )

        self.memory.pop(
            session_id,
            None
        )

        logger.success(
            f"History Cleared | Session={session_id}"
        )

    def get_conversation_summary(
        self,
        session_id: str
    ) -> str:

        logger.info(
            f"Generating Summary | Session={session_id}"
        )

        history = self.memory.get(
            session_id,
            []
        )

        if not history:

            logger.warning(
                f"No History Found | Session={session_id}"
            )

            return "No conversation available."

        summary = "\n".join(
            [
                f"{msg['role']}: {msg['content']}"
                for msg in history
            ]
        )

        logger.success(
            f"Summary Generated | Session={session_id}"
        )

        return summary


chat_memory = ChatMemory()